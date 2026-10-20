from __future__ import annotations

import multiprocessing
import os
import signal
import sys
import time
from pathlib import Path

import check_runner
from check_parsers import Parsed
from check_runner import CommandResult, run_command
from check_steps import Command

WAIT_SECONDS = 20
TEST_GRACE_SECONDS = 5.0
SHELL_WITH_CLEANUP_TRAP = (
    """trap 'echo cleaned > "$1"; exit' TERM; sleep 60 & echo $$ $! > "$2"; wait"""
)
POLL_SECONDS = 0.05
GRANDCHILD_SLEEP = "import time; time.sleep(60)"
TOOL_WITH_GRANDCHILD = (
    "import os, subprocess, sys, time\n"
    f"grandchild = subprocess.Popen([sys.executable, '-c', {GRANDCHILD_SLEEP!r}])\n"
    "with open(sys.argv[1], 'w', encoding='utf-8') as handle:\n"
    "    handle.write(f'{os.getpid()} {grandchild.pid}')\n"
    "time.sleep(60)\n"
)


def python(code: str, *arguments: str, timeout: int = 60) -> Command:
    return Command(
        (sys.executable, "-c", code, *arguments),
        lambda output, _code: Parsed(output.strip()),
        timeout=timeout,
    )


def process_ended(pid: int) -> bool:
    deadline = time.monotonic() + WAIT_SECONDS
    while time.monotonic() < deadline:
        try:
            state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        except FileNotFoundError, ProcessLookupError:
            return True
        if state == "Z":
            return True
        time.sleep(POLL_SECONDS)
    return False


def run_tool_with_grandchild(pid_file: str) -> None:
    run_command(python(TOOL_WITH_GRANDCHILD, pid_file), {}, stream=False)


def wait_for_file_content(path: Path) -> str:
    deadline = time.monotonic() + WAIT_SECONDS
    while time.monotonic() < deadline:
        if path.exists() and path.read_text(encoding="utf-8"):
            return path.read_text(encoding="utf-8")
        time.sleep(POLL_SECONDS)
    message = f"{path} was not written"
    raise TimeoutError(message)


def test_the_output_and_exit_code_of_a_real_tool_are_captured():
    result = run_command(
        python("import sys; print('out'); sys.stderr.write('err'); sys.exit(3)"),
        {},
        stream=False,
    )

    assert result == CommandResult(3, "out\nerr", None)


def test_a_real_tool_past_its_timeout_is_reported_as_timed_out():
    result = run_command(
        python("import time; print('started', flush=True); time.sleep(60)", timeout=1),
        {},
        stream=False,
    )

    assert result.problem == "timed out after 1s"
    assert result.output == "started\n"


def test_a_real_tool_killed_by_a_signal_is_reported_as_killed():
    result = run_command(
        python("import os, signal; os.kill(os.getpid(), signal.SIGKILL)"),
        {},
        stream=False,
    )

    assert result.problem == "killed by signal SIGKILL"


def test_a_runner_stopped_with_sigterm_leaves_no_tool_process_running(tmp_path):
    pid_file = tmp_path / "pids"
    context = multiprocessing.get_context("spawn")
    runner = context.Process(target=run_tool_with_grandchild, args=(str(pid_file),))
    runner.start()

    tool_pid, grandchild_pid = (
        int(pid) for pid in wait_for_file_content(pid_file).split()
    )
    assert runner.pid is not None
    os.kill(runner.pid, signal.SIGTERM)
    runner.join(timeout=WAIT_SECONDS)

    assert runner.exitcode == -signal.SIGTERM
    assert process_ended(tool_pid)
    assert process_ended(grandchild_pid)


def test_a_timed_out_tool_runs_its_cleanup_trap_and_leaves_nothing_running(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(check_runner, "STOP_GRACE_SECONDS", TEST_GRACE_SECONDS)
    marker = tmp_path / "marker"
    pid_file = tmp_path / "pids"
    command = Command(
        ("sh", "-c", SHELL_WITH_CLEANUP_TRAP, "sh", str(marker), str(pid_file)),
        lambda output, _code: Parsed(output.strip()),
        timeout=1,
    )

    result = run_command(command, {}, stream=False)

    shell_pid, sleep_pid = (int(pid) for pid in pid_file.read_text().split())
    assert result.problem == "timed out after 1s"
    assert marker.read_text(encoding="utf-8") == "cleaned\n"
    assert process_ended(shell_pid)
    assert process_ended(sleep_pid)
