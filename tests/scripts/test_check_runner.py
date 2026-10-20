from __future__ import annotations

import os
import resource
import runpy
import signal
import threading
from contextlib import nullcontext
from types import SimpleNamespace
from typing import TYPE_CHECKING

import check_runner
import pytest
from check_parsers import Finding, Parsed
from check_runner import (
    CommandResult,
    Outcome,
    annotation,
    environment_for,
    execute_step,
    final_line,
    format_duration,
    main,
    report,
    run_command,
    select_steps,
)
from check_steps import (
    SPARSE_ENVIRONMENT,
    Command,
    Group,
    Help,
    Invocation,
    Step,
    StepUnavailableError,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path

RUNNER_PID = 77
NO_HELP = Help(summary="", runs="", success="", failure="", args="")
TOOL_PID = 4321


def parse_output(output: str, return_code: int) -> Parsed:
    return Parsed(
        output.strip() or "done", (f"broke {return_code}",) if return_code else ()
    )


def command_named(name: str, *, timeout: int = 30, **fields) -> Command:
    return Command((name,), parse_output, timeout=timeout, **fields)


class FakeTimer:
    created: list[FakeTimer]

    def __init__(self, interval: float, function: Callable[[], None]) -> None:
        self.interval = interval
        self.function = function
        self.started = False
        self.cancelled = False
        self.joined = False
        self.created.append(self)

    def start(self) -> None:
        self.started = True

    def cancel(self) -> None:
        self.cancelled = True

    def join(self) -> None:
        self.joined = True


class FakeProcess:
    def __init__(
        self,
        *,
        lines: tuple[str, ...] = (),
        return_code: int = 0,
        during_output: Callable[[], None] | None = None,
        has_output: bool = True,
    ) -> None:
        self.pid = TOOL_PID
        self.return_code = return_code
        self.exit_check: Callable[[], bool] = lambda: True
        self.during_output = during_output
        self.stdout = self.read(lines) if has_output else None

    def read(self, lines: tuple[str, ...]) -> Iterator[str]:
        for line in lines:
            yield line
            if self.during_output:
                self.during_output()

    def wait(self) -> int:
        return self.return_code

    def poll(self) -> int | None:
        return self.return_code if self.exit_check() else None


class Sandbox:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.popen_calls: list[tuple[tuple[str, ...], dict[str, object]]] = []
        self.process = FakeProcess()
        self.popen_error: Exception | None = None
        self.killpg_calls: list[tuple[int, int]] = []
        self.killpg_errors: dict[int, Exception] = {}
        self.waitpid_calls: list[tuple[int, int]] = []
        self.waitpid_error: Exception | None = None
        self.checks_before_exit: int | None = 0
        self.leader_checks = 0
        self.now = 0.0
        self.sleeps: list[float] = []
        self.kill_calls: list[tuple[int, int]] = []
        self.handlers: dict[int, object] = {}
        self.limits: list[tuple[int, int]] = []
        self.hard_limit = resource.RLIM_INFINITY
        self.timers: list[FakeTimer] = []
        FakeTimer.created = self.timers
        monkeypatch.setattr(
            check_runner,
            "subprocess",
            SimpleNamespace(Popen=self.popen, PIPE=-1, STDOUT=-2),
        )
        monkeypatch.setattr(
            check_runner,
            "threading",
            SimpleNamespace(Event=threading.Event, Timer=FakeTimer),
        )
        monkeypatch.setattr(
            check_runner,
            "os",
            SimpleNamespace(
                killpg=self.killpg,
                kill=self.kill,
                waitpid=self.waitpid,
                WNOHANG=os.WNOHANG,
                getpid=lambda: RUNNER_PID,
                environ=os.environ,
            ),
        )
        monkeypatch.setattr(
            check_runner,
            "signal",
            SimpleNamespace(
                signal=self.register,
                SIGKILL=signal.SIGKILL,
                SIGTERM=signal.SIGTERM,
                SIG_DFL=signal.SIG_DFL,
                SIG_IGN=signal.SIG_IGN,
                Signals=signal.Signals,
            ),
        )
        monkeypatch.setattr(
            check_runner,
            "time",
            SimpleNamespace(monotonic=lambda: self.now, sleep=self.sleep),
        )
        monkeypatch.setattr(
            check_runner,
            "resource",
            SimpleNamespace(
                RLIMIT_DATA=resource.RLIMIT_DATA,
                RLIM_INFINITY=resource.RLIM_INFINITY,
                getrlimit=lambda _: (100, self.hard_limit),
                setrlimit=lambda _, limit: self.limits.append(limit),
            ),
        )

    def popen(self, argv, **options):
        if self.popen_error:
            raise self.popen_error
        self.popen_calls.append((argv, options))
        self.process.exit_check = self.leader_exited
        return self.process

    def killpg(self, group: int, number: int) -> None:
        self.killpg_calls.append((group, number))
        if number in self.killpg_errors:
            raise self.killpg_errors[number]

    def leader_exited(self) -> bool:
        self.leader_checks += 1
        return (
            self.checks_before_exit is not None
            and self.leader_checks > self.checks_before_exit
        )

    def waitpid(self, pid: int, options: int) -> tuple[int, int]:
        self.waitpid_calls.append((pid, options))
        if self.waitpid_error:
            raise self.waitpid_error
        return (pid, 0) if self.leader_exited() else (0, 0)

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds

    def kill(self, pid: int, number: int) -> None:
        self.kill_calls.append((pid, number))

    def register(self, number, handler):
        previous = self.handlers.get(number, signal.SIG_DFL)
        self.handlers[number] = handler
        return previous


@pytest.fixture
def sandbox(monkeypatch: pytest.MonkeyPatch) -> Sandbox:
    return Sandbox(monkeypatch)


def test_run_command_captures_output_and_exit_code(sandbox):
    sandbox.process = FakeProcess(lines=("hello\n",))

    result = run_command(command_named("tool"), {}, stream=False)

    assert result == CommandResult(0, "hello\n", None)


def test_run_command_starts_the_tool_in_its_own_session_with_merged_output(sandbox):
    sandbox.process = FakeProcess()

    run_command(command_named("tool", cwd="frontend"), {}, stream=False)

    ((argv, options),) = sandbox.popen_calls
    assert argv == ("tool",)
    assert options == {
        "cwd": "frontend",
        "env": {},
        "stdout": -1,
        "stderr": -2,
        "text": True,
        "start_new_session": True,
    }


def test_run_command_merges_the_environment_and_the_command_environment(sandbox):
    command = command_named("tool", environment={"B": "two"})

    run_command(command, {"A": "one", "B": "overridden"}, stream=False)

    ((_, options),) = sandbox.popen_calls
    assert options["env"] == {"A": "one", "B": "two"}


def test_run_command_streams_the_raw_output_when_asked(sandbox, capsys):
    sandbox.process = FakeProcess(lines=("raw line\n",))

    run_command(command_named("tool"), {}, stream=True)

    assert capsys.readouterr().out == "raw line\n"


def test_run_command_keeps_the_exit_code_of_a_failing_tool(sandbox):
    sandbox.process = FakeProcess(lines=("oops",), return_code=3)

    result = run_command(command_named("tool"), {}, stream=False)

    assert result == CommandResult(3, "oops", None)


def test_run_command_handles_a_tool_without_an_output_pipe(sandbox):
    sandbox.process = FakeProcess(has_output=False)

    assert run_command(command_named("tool"), {}, stream=False).output == ""


def test_run_command_reports_a_signal_kill_as_a_kill_not_a_failure(sandbox):
    sandbox.process = FakeProcess(return_code=-signal.SIGKILL)

    result = run_command(command_named("tool"), {}, stream=False)

    assert result.problem == "killed by signal SIGKILL"
    assert result.return_code == -signal.SIGKILL


def test_a_signal_number_that_is_unknown_is_reported_as_the_number():
    assert check_runner.signal_name(-250) == "250"


def test_run_command_arms_a_timer_for_the_timeout_and_ends_it_when_done(sandbox):
    run_command(command_named("tool", timeout=12), {}, stream=False)

    (timer,) = sandbox.timers
    assert timer.interval == 12
    assert timer.started
    assert timer.cancelled
    assert timer.joined


def fire_timeout(sandbox: Sandbox) -> None:
    sandbox.timers[0].function()


def stop_runner(sandbox: Sandbox) -> None:
    sandbox.handlers[signal.SIGTERM](signal.SIGTERM, None)


STOP_PATHS = pytest.mark.parametrize(
    "trigger", [fire_timeout, stop_runner], ids=["timeout", "runner stopped"]
)


def run_and_stop(sandbox: Sandbox, trigger: Callable[[Sandbox], None]) -> CommandResult:
    sandbox.process = FakeProcess(
        lines=("started\n",),
        return_code=-signal.SIGTERM,
        during_output=lambda: trigger(sandbox),
    )
    return run_command(command_named("tool", timeout=1), {}, stream=False)


@STOP_PATHS
def test_a_stopped_tool_group_gets_sigterm_and_the_grace_ends_when_the_tool_exits(
    sandbox, trigger
):
    sandbox.checks_before_exit = 2
    sandbox.killpg_errors[signal.SIGKILL] = ProcessLookupError()

    run_and_stop(sandbox, trigger)

    assert sandbox.killpg_calls == [
        (TOOL_PID, signal.SIGTERM),
        (TOOL_PID, signal.SIGKILL),
    ]
    assert sandbox.sleeps == [check_runner.STOP_POLL_SECONDS] * 2


@STOP_PATHS
def test_a_stopped_tool_group_still_running_after_the_grace_gets_sigkill(
    sandbox, trigger
):
    sandbox.checks_before_exit = None

    run_and_stop(sandbox, trigger)

    assert sandbox.killpg_calls == [
        (TOOL_PID, signal.SIGTERM),
        (TOOL_PID, signal.SIGKILL),
    ]
    assert sandbox.now >= check_runner.STOP_GRACE_SECONDS


@STOP_PATHS
def test_a_tool_group_already_gone_is_not_waited_for(sandbox, trigger):
    sandbox.killpg_errors[signal.SIGTERM] = ProcessLookupError()

    run_and_stop(sandbox, trigger)

    assert sandbox.killpg_calls == [(TOOL_PID, signal.SIGTERM)]
    assert sandbox.sleeps == []


def test_a_timed_out_tool_is_reported_as_timed_out_with_its_output(sandbox):
    result = run_and_stop(sandbox, fire_timeout)

    assert result == CommandResult(-signal.SIGTERM, "started\n", "timed out after 1s")


def test_a_stopped_runner_stops_on_the_same_signal_after_the_tool_group(sandbox):
    run_and_stop(sandbox, stop_runner)

    assert sandbox.kill_calls == [(RUNNER_PID, signal.SIGTERM)]
    assert sandbox.handlers[signal.SIGTERM] == signal.SIG_DFL


def test_a_stopped_runner_ignores_repeat_stop_signals_while_the_tool_cleans_up(
    sandbox,
):
    handlers_when_signalled: list[dict[int, object]] = []

    def record_handlers(group: int, number: int) -> None:
        handlers_when_signalled.append(dict(sandbox.handlers))
        sandbox.killpg(group, number)

    check_runner.os.killpg = record_handlers
    handlers_when_runner_stopped: list[object] = []
    check_runner.os.kill = lambda _pid, number: handlers_when_runner_stopped.append(
        sandbox.handlers[number]
    )

    run_and_stop(sandbox, stop_runner)

    ignored = dict.fromkeys(stop_signals(), signal.SIG_IGN)
    assert handlers_when_signalled == [ignored, ignored]
    assert handlers_when_runner_stopped == [signal.SIG_DFL]


def test_a_stopped_runner_flushes_its_report_before_it_stops_itself(
    sandbox, monkeypatch
):
    events: list[str] = []
    monkeypatch.setattr(
        check_runner.sys,
        "stdout",
        SimpleNamespace(flush=lambda: events.append("flush")),
    )
    check_runner.os.kill = lambda _pid, _number: events.append("kill")

    run_and_stop(sandbox, stop_runner)

    assert events == ["flush", "kill"]


def test_a_stopped_runner_reaps_the_tool_so_a_zombie_ends_the_grace(sandbox):
    sandbox.checks_before_exit = 1

    run_and_stop(sandbox, stop_runner)

    assert sandbox.waitpid_calls == [(TOOL_PID, os.WNOHANG)] * 2
    assert sandbox.sleeps == [check_runner.STOP_POLL_SECONDS]


def test_a_stopped_runner_treats_a_tool_already_reaped_as_exited(sandbox):
    sandbox.checks_before_exit = None
    sandbox.waitpid_error = ChildProcessError()

    run_and_stop(sandbox, stop_runner)

    assert sandbox.sleeps == []


def test_run_command_reports_a_missing_tool(sandbox):
    sandbox.popen_error = FileNotFoundError()

    result = run_command(command_named("no-such-tool"), {}, stream=False)

    assert result == CommandResult(127, "", "tool not found: no-such-tool")


def test_the_data_segment_of_the_tool_is_capped_for_the_run_only(sandbox):
    run_command(command_named("tool"), {}, stream=False)

    assert sandbox.limits == [
        (check_runner.MEMORY_LIMIT_BYTES, resource.RLIM_INFINITY),
        (100, resource.RLIM_INFINITY),
    ]


def test_the_data_limit_never_goes_above_the_hard_limit(sandbox):
    sandbox.hard_limit = 50

    with check_runner.inherited_memory_limit():
        assert sandbox.limits == [(50, 50)]

    assert sandbox.limits == [(50, 50), (100, 50)]


def test_the_data_limit_is_restored_when_the_tool_cannot_start(sandbox):
    sandbox.popen_error = FileNotFoundError()

    run_command(command_named("tool"), {}, stream=False)

    assert sandbox.limits[-1] == (100, resource.RLIM_INFINITY)


def stop_signals() -> tuple[signal.Signals, ...]:
    return check_runner.RUNNER_STOP_SIGNALS


def test_every_stop_signal_is_handled_while_the_tool_runs_and_restored_after(sandbox):
    sandbox.handlers.update({number: f"old {number}" for number in stop_signals()})

    with check_runner.group_stopped_with_runner(sandbox.process):
        assert all(callable(sandbox.handlers[number]) for number in stop_signals())

    assert sandbox.handlers == {number: f"old {number}" for number in stop_signals()}


class ScriptedRun:
    def __init__(self, results: dict[str, CommandResult]) -> None:
        self.results = results
        self.calls: list[tuple[str, ...]] = []
        self.streams: list[bool] = []

    def __call__(self, command, _environment, *, stream) -> CommandResult:
        self.calls.append(command.argv)
        self.streams.append(stream)
        return self.results[command.argv[0]]


class FakeClock:
    def __init__(self, times: tuple[float, ...]) -> None:
        self.times = iter(times)

    def monotonic(self) -> float:
        return next(self.times)


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock((0.0, 2.5, 2.5, 2.5))
    monkeypatch.setattr(check_runner, "time", fake)
    return fake


def script(monkeypatch, **results: CommandResult) -> ScriptedRun:
    run = ScriptedRun(results)
    monkeypatch.setattr(check_runner, "run_command", run)
    return run


def invocation(tmp_path: Path, *, verbose: bool = False) -> Invocation:
    return Invocation(args=(), verbose=verbose, root=tmp_path, scratch=tmp_path)


def step_of(*names: str) -> Step:
    return Step(
        "sample", lambda _: tuple(command_named(name) for name in names), NO_HELP
    )


def test_a_passing_step_reports_the_parsed_summary_and_the_elapsed_time(
    monkeypatch, tmp_path, clock
):
    script(monkeypatch, one=CommandResult(0, "3 passed\n", None))

    outcome = execute_step(step_of("one"), invocation(tmp_path), {})

    assert outcome == Outcome(
        "sample",
        ok=True,
        summary="3 passed",
        seconds=2.5,
        details=(),
        findings=(),
        raw="3 passed\n",
    )


def test_a_failing_step_reports_the_parsed_details(monkeypatch, tmp_path, clock):
    script(monkeypatch, one=CommandResult(1, "x\n", None))

    outcome = execute_step(step_of("one"), invocation(tmp_path), {})

    assert not outcome.ok
    assert outcome.details == ("broke 1",)


def test_a_verbose_step_streams_its_commands(monkeypatch, tmp_path, clock):
    run = script(monkeypatch, one=CommandResult(0, "", None))

    execute_step(step_of("one"), invocation(tmp_path, verbose=True), {})

    assert run.streams == [True]


@pytest.mark.parametrize(
    ("output", "details"),
    [
        (
            "> pkg@1.0.0 lint\n> eslint .\nnpm error Missing script\n\n",
            ("npm error Missing script",),
        ),
        ("real reason\n", ("real reason",)),
    ],
    ids=["drops the npm banner and keeps npm errors", "shows the raw output"],
)
def test_a_failing_step_without_parsed_details_shows_the_useful_raw_output(
    monkeypatch, tmp_path, clock, output, details
):
    script(monkeypatch, one=CommandResult(1, output, None))
    step = Step(
        "sample",
        lambda _: (Command(("one",), lambda _output, _code: Parsed("failed")),),
        NO_HELP,
    )

    outcome = execute_step(step, invocation(tmp_path), {})

    assert outcome.details == details


def test_a_killed_step_is_reported_as_killed_and_shows_its_output(
    monkeypatch, tmp_path, clock
):
    script(
        monkeypatch,
        one=CommandResult(-15, "last words\n", "killed by signal SIGTERM"),
    )

    outcome = execute_step(step_of("one"), invocation(tmp_path), {})

    assert not outcome.ok
    assert outcome.summary == "killed by signal SIGTERM"
    assert outcome.details == ("last words",)
    assert outcome.raw == "last words\n"


def test_a_step_stops_at_the_first_command_that_cannot_complete(
    monkeypatch, tmp_path, clock
):
    run = script(
        monkeypatch,
        missing=CommandResult(127, "", "tool not found: missing"),
        never=CommandResult(0, "never\n", None),
    )

    outcome = execute_step(step_of("missing", "never"), invocation(tmp_path), {})

    assert outcome.summary == "tool not found: missing"
    assert run.calls == [("missing",)]


def test_every_command_of_a_step_runs_and_summaries_are_joined(
    monkeypatch, tmp_path, clock
):
    script(
        monkeypatch,
        one=CommandResult(0, "one\n", None),
        two=CommandResult(0, "two\n", None),
    )

    outcome = execute_step(step_of("one", "two"), invocation(tmp_path), {})

    assert outcome.summary == "one, two"
    assert outcome.ok
    assert outcome.raw == "one\ntwo\n"


def test_a_step_with_its_own_combination_combines_the_parsed_parts(
    monkeypatch, tmp_path, clock
):
    script(
        monkeypatch,
        one=CommandResult(0, "one\n", None),
        two=CommandResult(0, "two\n", None),
    )

    def combine(parts: tuple[Parsed, ...]) -> Parsed:
        return Parsed(f"{len(parts)} parts")

    step = Step(
        "sample",
        lambda _: (command_named("one"), command_named("two")),
        NO_HELP,
        combine=combine,
    )

    outcome = execute_step(step, invocation(tmp_path), {})

    assert outcome.summary == "2 parts"


def test_a_step_with_a_failing_second_command_fails(monkeypatch, tmp_path, clock):
    script(
        monkeypatch,
        one=CommandResult(0, "one\n", None),
        two=CommandResult(1, "two\n", None),
    )

    outcome = execute_step(step_of("one", "two"), invocation(tmp_path), {})

    assert not outcome.ok
    assert outcome.details == ("broke 1",)


@pytest.mark.parametrize(
    "error", [StepUnavailableError("no token"), check_runner.ScopeError("no token")]
)
def test_a_step_that_cannot_build_its_commands_fails_with_the_reason(
    tmp_path, clock, error
):
    def build(_: Invocation) -> tuple[Command, ...]:
        raise error

    outcome = execute_step(Step("sample", build, NO_HELP), invocation(tmp_path), {})

    assert not outcome.ok
    assert outcome.summary == "no token"
    assert outcome.seconds == 0.0


def outcome(name: str = "sample", *, ok: bool = True, **fields) -> Outcome:
    values = {
        "summary": "summary",
        "seconds": 1.2,
        "details": (),
        "findings": (),
        "raw": "raw output\n",
    }
    values.update(fields)
    return Outcome(name, ok, **values)


def test_a_passing_step_prints_one_checked_line(capsys):
    report(
        outcome(summary="3 passed  96.3% cov", seconds=196.4),
        verbose=False,
        github_actions=False,
    )

    assert capsys.readouterr().out == "[x] sample  3 passed  96.3% cov  196s\n"


@pytest.mark.parametrize("ok", [True, False], ids=["passing", "failing"])
def test_every_step_report_is_flushed_once_written(monkeypatch, *, ok):
    events: list[str] = []
    monkeypatch.setattr(
        check_runner.sys,
        "stdout",
        SimpleNamespace(
            write=lambda _text: events.append("write"),
            flush=lambda: events.append("flush"),
        ),
    )

    report(outcome(ok=ok), verbose=False, github_actions=False)

    assert events[-1] == "flush"
    assert "write" in events


def test_a_passing_step_prints_its_details_below_the_checked_line(capsys):
    report(
        outcome(summary="3 passed  1 warning", details=("warning a.py:5 Bad: x",)),
        verbose=False,
        github_actions=False,
    )

    assert capsys.readouterr().out == (
        "[x] sample  3 passed  1 warning  1.2s\n    warning a.py:5 Bad: x\n"
    )


def test_a_failing_step_prints_an_unchecked_line_and_its_details(capsys):
    report(
        outcome(ok=False, summary="1 error", details=("a.py:5 bad",)),
        verbose=False,
        github_actions=False,
    )

    assert capsys.readouterr().out == "[ ] sample  1 error  1.2s\n    a.py:5 bad\n"


def test_verbose_reports_do_not_repeat_the_details_already_streamed(capsys):
    report(
        outcome(ok=False, details=("a.py:5 bad",)), verbose=True, github_actions=False
    )

    assert capsys.readouterr().out == "[ ] sample  summary  1.2s\n"


def test_github_actions_groups_the_raw_output_and_annotates_findings(capsys):
    finding = Finding("a.py", 5, "bad thing")

    report(
        outcome(ok=False, findings=(finding,), details=("a.py:5 bad thing",)),
        verbose=False,
        github_actions=True,
    )

    lines = capsys.readouterr().out.splitlines()
    assert lines[:3] == ["::group::sample", "raw output", "::endgroup::"]
    assert "::error file=a.py,line=5::bad thing" in lines


def test_github_actions_annotates_a_failure_without_findings_with_its_summary(capsys):
    report(
        outcome(ok=False, summary="killed by signal SIGKILL"),
        verbose=False,
        github_actions=True,
    )

    assert "::error title=sample::killed by signal SIGKILL" in capsys.readouterr().out


def test_github_actions_does_not_annotate_a_passing_step(capsys):
    report(outcome(), verbose=False, github_actions=True)

    assert "::error" not in capsys.readouterr().out


def test_github_actions_closes_the_group_when_the_output_lacks_a_final_newline(capsys):
    report(outcome(raw="no newline"), verbose=False, github_actions=True)

    assert capsys.readouterr().out.startswith(
        "::group::sample\nno newline\n::endgroup::\n"
    )


def test_github_actions_closes_the_group_of_a_step_without_output(capsys):
    report(outcome(raw=""), verbose=False, github_actions=True)

    assert capsys.readouterr().out.startswith("::group::sample\n::endgroup::\n")


def test_annotations_escape_workflow_command_characters():
    finding = Finding("dir,a:b.py", 3, "50%\nnext")

    assert annotation(finding) == "::error file=dir%2Ca%3Ab.py,line=3::50%25%0Anext"


def test_an_annotation_without_a_file_has_no_properties():
    assert annotation(Finding(None, None, "plain")) == "::error::plain"


def test_an_annotation_without_a_line_names_only_the_file():
    assert annotation(Finding("a.py", None, "plain")) == "::error file=a.py::plain"


def test_durations_show_a_decimal_only_for_short_steps():
    assert format_duration(0.44) == "0.4s"
    assert format_duration(196.4) == "196s"


def test_the_final_line_counts_steps_and_names_the_failures():
    outcomes = [outcome("a"), outcome("b", ok=False), outcome("c", ok=False)]

    assert final_line(outcomes) == "result: 1 of 3 steps passed  failed: b, c"
    assert final_line([outcome("a")]) == "result: 1 of 1 steps passed"


def test_sparse_environment_is_applied_unless_verbose():
    assert environment_for(verbose=False).items() >= SPARSE_ENVIRONMENT.items()


def test_verbose_removes_the_sparse_environment(monkeypatch):
    for key, value in SPARSE_ENVIRONMENT.items():
        monkeypatch.setenv(key, value)

    environment = environment_for(verbose=True)

    assert not set(SPARSE_ENVIRONMENT) & set(environment)


def test_verbose_leaves_a_sparse_setting_that_is_not_set_alone(monkeypatch):
    for key in SPARSE_ENVIRONMENT:
        monkeypatch.delenv(key, raising=False)

    assert not set(SPARSE_ENVIRONMENT) & set(environment_for(verbose=True))


def test_only_filters_the_requested_steps_and_keeps_their_order():
    steps = select_steps(["ruff", "mypy", "test-python"], ["test-python", "ruff"])

    assert [step.name for step in steps] == ["ruff", "test-python"]


def test_a_step_brings_the_steps_it_requires_before_it():
    steps = select_steps(["test-browser-controlled"], [])

    assert [step.name for step in steps] == ["build", "test-browser-controlled"]


def test_a_required_step_is_not_run_twice():
    steps = select_steps(["build", "test-browser-controlled"], [])

    assert [step.name for step in steps] == ["build", "test-browser-controlled"]


def test_a_step_already_brought_in_as_a_requirement_is_not_run_again():
    steps = select_steps(["test-browser-controlled", "build"], [])

    assert [step.name for step in steps] == ["build", "test-browser-controlled"]


def test_unknown_step_names_are_rejected():
    with pytest.raises(ValueError, match="unknown steps: nope"):
        select_steps(["ruff"], ["nope"])


def test_only_cannot_name_a_step_the_target_does_not_run():
    with pytest.raises(ValueError, match="does not run: mypy"):
        select_steps(["ruff"], ["mypy"])


@pytest.fixture
def fake_steps(monkeypatch, tmp_path):
    def make(name: str) -> Step:
        return Step(
            name,
            lambda inv: (Command((name, *inv.args), parse_output),),
            NO_HELP,
        )

    steps = {name: make(name) for name in ("good", "bad-one", "bad-two", "echo")}
    monkeypatch.setattr(check_runner, "STEPS_BY_NAME", steps)
    monkeypatch.setattr(
        check_runner,
        "GROUPS_BY_NAME",
        {"ci": Group("ci", "", ("bad-one", "good", "bad-two"))},
    )
    monkeypatch.setattr(
        check_runner,
        "tempfile",
        SimpleNamespace(TemporaryDirectory=lambda: nullcontext(str(tmp_path))),
    )
    monkeypatch.setattr(
        check_runner,
        "run_command",
        lambda command, *_arguments, **_options: CommandResult(
            1 if command.argv[0].startswith("bad") else 0,
            " ".join(command.argv[1:]) or "fine",
            None,
        ),
    )
    monkeypatch.setattr(check_runner, "time", SimpleNamespace(monotonic=lambda: 0.0))
    for name in ("V", "ONLY", "ARGS", "GITHUB_ACTIONS"):
        monkeypatch.delenv(name, raising=False)


def test_failures_in_two_steps_are_both_reported_in_one_run(fake_steps, capsys):
    exit_code = main(["ci"])

    lines = capsys.readouterr().out.splitlines()
    assert exit_code == 1
    assert lines[0] == "[ ] bad-one  fine  0.0s"
    assert lines[1] == "    broke 1"
    assert lines[2].startswith("[x] good  fine")
    assert lines[3].startswith("[ ] bad-two")
    assert lines[-1] == "result: 1 of 3 steps passed  failed: bad-one, bad-two"


def test_a_clean_run_exits_zero_with_one_line_per_step(fake_steps, capsys):
    exit_code = main(["good", "echo"])

    lines = capsys.readouterr().out.splitlines()
    assert exit_code == 0
    assert len(lines) == 3
    assert lines[-1] == "result: 2 of 2 steps passed"


def test_args_are_forwarded_only_when_asked_to(fake_steps, monkeypatch, capsys):
    monkeypatch.setenv("ARGS", "one 'two words'")

    main(["echo"])
    without = capsys.readouterr().out
    main(["--forward-args", "echo"])
    forwarded = capsys.readouterr().out

    assert "one two words" not in without
    assert "[x] echo  one two words" in forwarded


def test_args_reach_only_the_step_the_target_names(fake_steps, monkeypatch, capsys):
    monkeypatch.setenv("ARGS", "extra")
    steps = dict(check_runner.STEPS_BY_NAME)
    steps["echo"] = Step("echo", steps["echo"].build, NO_HELP, requires=("good",))
    monkeypatch.setattr(check_runner, "STEPS_BY_NAME", steps)

    main(["--forward-args", "echo"])

    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("[x] good  fine")
    assert lines[1].startswith("[x] echo  extra")


def test_only_selects_a_subset_of_the_checks(fake_steps, monkeypatch, capsys):
    monkeypatch.setenv("ONLY", "good")

    exit_code = main(["ci"])

    assert exit_code == 0
    assert capsys.readouterr().out.splitlines()[-1] == "result: 1 of 1 steps passed"


def test_an_invalid_selection_is_a_usage_error(fake_steps, monkeypatch, capsys):
    monkeypatch.setenv("ONLY", "missing")

    exit_code = main(["ci"])

    assert exit_code == 2
    assert "unknown steps: missing" in capsys.readouterr().err


def test_verbose_runs_do_not_repeat_the_details_and_stream_the_tool(
    fake_steps, monkeypatch, capsys
):
    monkeypatch.setenv("V", "1")

    main(["bad-one"])

    assert capsys.readouterr().out.splitlines()[0] == "[ ] bad-one  fine  0.0s"


def test_github_actions_runs_wrap_each_step_in_a_group(fake_steps, monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    main(["good"])

    assert capsys.readouterr().out.startswith("::group::good\nfine\n::endgroup::\n")


def test_running_the_runner_as_a_script_exits_with_the_status_of_main(
    fake_steps, monkeypatch
):
    monkeypatch.setenv("ONLY", "missing")
    monkeypatch.setattr("sys.argv", ["check_runner.py", "ci"])

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("check_runner", run_name="__main__")

    assert stopped.value.code == 2


def test_a_group_name_runs_the_steps_of_the_group_in_order(fake_steps, capsys):
    main(["ci"])

    names = [
        line[4:].split()[0]
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("[")
    ]
    assert names == ["bad-one", "good", "bad-two"]


def test_describe_without_a_target_lists_every_target(capsys):
    exit_code = main(["--describe"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.startswith("ruff ")
    assert "\nlogs " in out


def test_describe_with_a_target_prints_the_detail_of_the_target(capsys):
    exit_code = main(["--describe", "lint"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.startswith("lint: ")
    assert "\nsteps:\n" in out


@pytest.mark.parametrize(
    ("names", "message"),
    [
        (["nope"], "unknown target: nope"),
        (["ruff", "mypy"], "describe one target at a time, got: ruff, mypy"),
    ],
)
def test_describe_rejects_an_unknown_target_or_several_targets(names, message, capsys):
    exit_code = main(["--describe", *names])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert message in captured.err
    assert captured.out == ""


def test_the_runner_needs_a_step_unless_it_describes(capsys):
    with pytest.raises(SystemExit) as stopped:
        main([])

    assert stopped.value.code == 2
    assert "name at least one step" in capsys.readouterr().err
