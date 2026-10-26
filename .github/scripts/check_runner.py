from __future__ import annotations

import argparse
import contextlib
import os
import resource
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import check_parsers
from check_help import UnknownTargetError, describe, list_targets
from check_parsers import Parsed
from check_steps import (
    GROUPS_BY_NAME,
    SPARSE_ENVIRONMENT,
    STEPS_BY_NAME,
    Command,
    Invocation,
    Step,
    StepUnavailableError,
)
from pytest_scope import ScopeError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence
    from types import FrameType

    from check_parsers import Finding

ANNOTATION_ESCAPES = (("%", "%25"), ("\r", "%0D"), ("\n", "%0A"))
PROPERTY_ESCAPES = (*ANNOTATION_ESCAPES, (":", "%3A"), (",", "%2C"))
DETAIL_INDENT = "    "
SLOW_STEP_SECONDS = 10
USAGE_ERROR = 2
MEMORY_LIMIT_BYTES = 8 * 1024**3
RUNNER_STOP_SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
STOP_GRACE_SECONDS = 60.0
STOP_POLL_SECONDS = 0.1


@dataclass(frozen=True)
class CommandResult:
    return_code: int
    output: str
    problem: str | None


@dataclass(frozen=True)
class Outcome:
    name: str
    ok: bool
    summary: str
    seconds: float
    details: tuple[str, ...]
    findings: tuple[Finding, ...]
    raw: str


def escape(text: str, escapes: tuple[tuple[str, str], ...]) -> str:
    for character, replacement in escapes:
        text = text.replace(character, replacement)
    return text


def annotation(finding: Finding) -> str:
    message = escape(finding.message, ANNOTATION_ESCAPES)
    properties: list[str] = []
    if finding.file:
        properties.append(f"file={escape(finding.file, PROPERTY_ESCAPES)}")
        if finding.line:
            properties.append(f"line={finding.line}")
    prefix = f"::error {','.join(properties)}::" if properties else "::error::"
    return f"{prefix}{message}"


def format_duration(seconds: float) -> str:
    if seconds >= SLOW_STEP_SECONDS:
        return f"{seconds:.0f}s"
    return f"{seconds:.1f}s"


def signal_name(return_code: int) -> str:
    try:
        return signal.Signals(-return_code).name
    except ValueError:
        return str(-return_code)


@contextlib.contextmanager
def inherited_memory_limit() -> Iterator[None]:
    soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
    limit = MEMORY_LIMIT_BYTES
    if hard != resource.RLIM_INFINITY:
        limit = min(limit, hard)
    resource.setrlimit(resource.RLIMIT_DATA, (limit, hard))
    try:
        yield
    finally:
        resource.setrlimit(resource.RLIMIT_DATA, (soft, hard))


def stop_group(process_group: int, *, exited: Callable[[], bool]) -> None:
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process_group, signal.SIGTERM)
        deadline = time.monotonic() + STOP_GRACE_SECONDS
        while not exited() and time.monotonic() < deadline:
            time.sleep(STOP_POLL_SECONDS)
        os.killpg(process_group, signal.SIGKILL)


def leader_reaped(process_id: int) -> bool:
    try:
        reaped, _ = os.waitpid(process_id, os.WNOHANG)
    except ChildProcessError:
        return True
    return reaped == process_id


@contextlib.contextmanager
def group_stopped_with_runner(process: subprocess.Popen[str]) -> Iterator[None]:
    def stop(signal_number: int, _frame: FrameType | None) -> None:
        for number in RUNNER_STOP_SIGNALS:
            signal.signal(number, signal.SIG_IGN)
        stop_group(process.pid, exited=lambda: leader_reaped(process.pid))
        sys.stdout.flush()
        signal.signal(signal_number, signal.SIG_DFL)
        os.kill(os.getpid(), signal_number)

    previous = {number: signal.signal(number, stop) for number in RUNNER_STOP_SIGNALS}
    try:
        yield
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)


def run_command(
    command: Command, environment: dict[str, str], *, stream: bool
) -> CommandResult:
    merged = {**environment, **command.environment}
    try:
        with inherited_memory_limit():
            process = subprocess.Popen(
                command.argv,
                cwd=command.cwd,
                env=merged,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
    except FileNotFoundError:
        return CommandResult(127, "", f"tool not found: {command.argv[0]}")
    with group_stopped_with_runner(process):
        return wait_for(process, command, stream=stream)


def wait_for(
    process: subprocess.Popen[str], command: Command, *, stream: bool
) -> CommandResult:
    timed_out = threading.Event()

    def terminate() -> None:
        timed_out.set()
        stop_group(process.pid, exited=lambda: process.poll() is not None)

    timer = threading.Timer(command.timeout, terminate)
    timer.start()
    lines: list[str] = []
    for line in process.stdout or ():
        lines.append(line)
        if stream:
            sys.stdout.write(line)
            sys.stdout.flush()
    return_code = process.wait()
    timer.cancel()
    timer.join()
    output = "".join(lines)
    if timed_out.is_set():
        return CommandResult(return_code, output, f"timed out after {command.timeout}s")
    if return_code < 0:
        return CommandResult(
            return_code, output, f"killed by signal {signal_name(return_code)}"
        )
    return CommandResult(return_code, output, None)


def merge(parts: Sequence[Parsed]) -> Parsed:
    return Parsed(
        ", ".join(part.summary for part in parts),
        tuple(detail for part in parts for detail in part.details),
        tuple(finding for part in parts for finding in part.findings),
    )


def execute_step(
    step: Step, invocation: Invocation, environment: dict[str, str]
) -> Outcome:
    started = time.monotonic()
    try:
        commands = step.build(invocation)
    except (StepUnavailableError, ScopeError) as error:
        return Outcome(
            step.name,
            ok=False,
            summary=str(error),
            seconds=0.0,
            details=(),
            findings=(),
            raw="",
        )
    parts: list[Parsed] = []
    results: list[CommandResult] = []
    for command in commands:
        result = run_command(command, environment, stream=invocation.verbose)
        results.append(result)
        if result.problem:
            return Outcome(
                step.name,
                ok=False,
                summary=result.problem,
                seconds=time.monotonic() - started,
                details=tuple(result.output.splitlines()),
                findings=(),
                raw=result.output,
            )
        parts.append(command.parser(result.output, result.return_code))
    parsed = merge(parts)
    ok = all(result.return_code == 0 for result in results) and not parsed.findings
    details = parsed.details
    if not ok and not details:
        details = tuple(
            line
            for result in results
            for line in check_parsers.strip_npm_banner(
                [raw for raw in result.output.splitlines() if raw.strip()]
            )
        )
    return Outcome(
        step.name,
        ok=ok,
        summary=parsed.summary,
        seconds=time.monotonic() - started,
        details=details,
        findings=parsed.findings,
        raw="".join(result.output for result in results),
    )


def report(outcome: Outcome, *, verbose: bool, github_actions: bool) -> None:
    if github_actions:
        sys.stdout.write(f"::group::{outcome.name}\n{outcome.raw}")
        if outcome.raw and not outcome.raw.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.write("::endgroup::\n")
    mark = "x" if outcome.ok else " "
    sys.stdout.write(
        f"[{mark}] {outcome.name}  {outcome.summary}  "
        f"{format_duration(outcome.seconds)}\n"
    )
    if not verbose:
        for detail in outcome.details:
            sys.stdout.write(f"{DETAIL_INDENT}{detail}\n")
    if github_actions and not outcome.ok:
        findings = outcome.findings or ()
        for finding in findings:
            sys.stdout.write(f"{annotation(finding)}\n")
        if not findings:
            sys.stdout.write(
                f"::error title={escape(outcome.name, PROPERTY_ESCAPES)}::"
                f"{escape(outcome.summary, ANNOTATION_ESCAPES)}\n"
            )
    sys.stdout.flush()


def final_line(outcomes: Sequence[Outcome]) -> str:
    passed = sum(1 for outcome in outcomes if outcome.ok)
    failed = [outcome.name for outcome in outcomes if not outcome.ok]
    line = f"result: {passed} of {len(outcomes)} steps passed"
    if failed:
        line = f"{line}  failed: {', '.join(failed)}"
    return line


def environment_for(*, verbose: bool) -> dict[str, str]:
    environment = dict(os.environ)
    if verbose:
        for key in SPARSE_ENVIRONMENT:
            environment.pop(key, None)
    else:
        environment.update(SPARSE_ENVIRONMENT)
    return environment


def select_steps(requested: Sequence[str], only: Sequence[str]) -> tuple[Step, ...]:
    unknown = [name for name in (*requested, *only) if name not in STEPS_BY_NAME]
    if unknown:
        message = f"unknown steps: {', '.join(unknown)}"
        raise ValueError(message)
    outside = [name for name in only if name not in requested]
    if outside:
        message = f"ONLY names steps this target does not run: {', '.join(outside)}"
        raise ValueError(message)
    chosen = [name for name in requested if not only or name in only]
    with_requirements: list[str] = []
    for name in chosen:
        for required in STEPS_BY_NAME[name].requires:
            if required not in with_requirements:
                with_requirements.append(required)
        if name not in with_requirements:
            with_requirements.append(name)
    return tuple(STEPS_BY_NAME[name] for name in with_requirements)


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forward-args", action="store_true")
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("steps", nargs="*")
    arguments = parser.parse_args(argv)
    if not arguments.steps and not arguments.describe:
        parser.error("name at least one step")
    return arguments


def expand_groups(names: Sequence[str]) -> list[str]:
    expanded: list[str] = []
    for name in names:
        group = GROUPS_BY_NAME.get(name)
        expanded.extend(group.steps if group else (name,))
    return expanded


def print_help(names: Sequence[str]) -> int:
    if not names:
        sys.stdout.write(f"{list_targets()}\n")
        return 0
    if len(names) > 1:
        sys.stderr.write(f"describe one target at a time, got: {', '.join(names)}\n")
        return USAGE_ERROR
    try:
        sys.stdout.write(f"{describe(names[0])}\n")
    except UnknownTargetError as error:
        sys.stderr.write(f"{error}\n")
        return USAGE_ERROR
    return 0


def main(argv: Sequence[str]) -> int:
    arguments = parse_arguments(argv)
    if arguments.describe:
        return print_help(arguments.steps)
    verbose = os.environ.get("V") == "1"
    only = [name for name in os.environ.get("ONLY", "").split(",") if name]
    requested = expand_groups(arguments.steps)
    try:
        steps = select_steps(requested, only)
    except ValueError as error:
        sys.stderr.write(f"{error}\n")
        return USAGE_ERROR
    forwarded = (
        tuple(shlex.split(os.environ.get("ARGS", ""))) if arguments.forward_args else ()
    )
    github_actions = bool(os.environ.get("GITHUB_ACTIONS"))
    environment = environment_for(verbose=verbose)
    outcomes: list[Outcome] = []
    with tempfile.TemporaryDirectory() as scratch:
        for step in steps:
            invocation = Invocation(
                args=forwarded if step.name in requested else (),
                verbose=verbose,
                root=Path.cwd(),
                scratch=Path(scratch),
            )
            outcome = execute_step(step, invocation, environment)
            outcomes.append(outcome)
            report(outcome, verbose=verbose, github_actions=github_actions)
    sys.stdout.write(f"{final_line(outcomes)}\n")
    return 0 if all(outcome.ok for outcome in outcomes) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
