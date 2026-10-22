from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import freeze_check
import pytest

TAG = "v1.0.0"
CURRENT_TREE = "/current-tree"
FROZEN_SURFACE = {
    "hs3": {"sensor": {"battery_power": {"unit": "W", "options": ["a", "b"]}}},
    "stored": {"config_flow": {"VERSION": 1}},
}


def completed(*, stdout="", stderr="", returncode=0):
    return subprocess.CompletedProcess(
        args=(), returncode=returncode, stdout=stdout, stderr=stderr
    )


class Commands:
    def __init__(self, *, tag=TAG, archive_fails=False, frozen=None, current=None):
        self.tag = tag
        self.archive_fails = archive_fails
        self.surfaces = {"frozen": frozen, "current": current}
        self.calls = []

    def __call__(self, argv):
        self.calls.append(tuple(argv))
        if argv[0] == "git" and argv[1] == "describe":
            if self.tag is None:
                return completed(returncode=128, stderr="fatal: No names found")
            return completed(stdout=f"{self.tag}\n")
        if argv[0] == "git":
            if self.archive_fails:
                return completed(returncode=1, stderr="fatal: not a valid object\n")
            return completed()
        surface = self.surfaces["current" if argv[2] == CURRENT_TREE else "frozen"]
        if surface is None:
            return completed(returncode=1, stderr="trace\nSurfaceError: no names\n")
        return completed(stdout=json.dumps(surface))


def unpacked_nowhere(archive, destination):
    del archive, destination


@pytest.fixture
def run_main(capsys):
    def start(commands):
        status = freeze_check.main(
            run=commands, unpack=unpacked_nowhere, root=Path(CURRENT_TREE)
        )
        return status, capsys.readouterr().out

    return start


def test_with_no_release_tag_the_step_passes_and_says_so(run_main):
    commands = Commands(tag=None)

    status, printed = run_main(commands)

    assert (status, printed) == (0, "no release tag\n")
    assert len(commands.calls) == 1


def test_an_unchanged_surface_passes_naming_the_tag(run_main):
    status, printed = run_main(Commands(frozen=FROZEN_SURFACE, current=FROZEN_SURFACE))

    assert (status, printed) == (0, f"surface kept since {TAG}\n")


def test_additions_to_the_surface_pass(run_main):
    grown = {
        "hs3": {
            "sensor": {
                "battery_power": {"unit": "W", "options": ["a", "b", "c"]},
                "new_key": {"unit": "V"},
            }
        },
        "stored": {"config_flow": {"VERSION": 1}, "extra": 1},
        "cards": {},
    }

    status, _ = run_main(Commands(frozen=FROZEN_SURFACE, current=grown))

    assert status == 0


def test_each_removal_and_change_is_one_line_and_fails(run_main):
    current = {
        "hs3": {"sensor": {"battery_power": {"unit": "kW", "options": ["a"]}}},
        "stored": {},
    }

    status, printed = run_main(Commands(frozen=FROZEN_SURFACE, current=current))

    assert status == 1
    assert printed.splitlines() == [
        "hs3 sensor battery_power: unit W -> kW",
        "hs3 sensor battery_power options: missing b",
        "stored config_flow: missing",
    ]


def stored_versions(*, version, minor, store):
    return {
        "stored": {
            "config_flow": {"VERSION": version, "MINOR_VERSION": minor},
            "power_control_store": {"version": store},
        }
    }


def test_the_three_version_numbers_may_rise(run_main):
    status, _ = run_main(
        Commands(
            frozen=stored_versions(version=1, minor=1, store=1),
            current=stored_versions(version=2, minor=2, store=2),
        )
    )

    assert status == 0


def test_a_fall_of_each_version_number_fails(run_main):
    _, printed = run_main(
        Commands(
            frozen=stored_versions(version=2, minor=2, store=2),
            current=stored_versions(version=1, minor=1, store=1),
        )
    )

    assert printed.splitlines() == [
        "stored config_flow: VERSION 2 -> 1",
        "stored config_flow: MINOR_VERSION 2 -> 1",
        "stored power_control_store: version 2 -> 1",
    ]


def test_a_version_number_changed_to_nothing_fails(run_main):
    status, printed = run_main(
        Commands(
            frozen=stored_versions(version=1, minor=1, store=1),
            current=stored_versions(version=1, minor=None, store=1),
        )
    )

    assert status == 1
    assert printed == "stored config_flow: MINOR_VERSION 1 -> null\n"


def test_another_number_stays_exact_when_it_rises(run_main):
    frozen = {"stored": {"config_flow": {"OTHER": 1}}}
    current = {"stored": {"config_flow": {"OTHER": 2}}}

    _, printed = run_main(Commands(frozen=frozen, current=current))

    assert printed == "stored config_flow: OTHER 1 -> 2\n"


def test_a_removed_entity_is_reported_missing_under_its_platform(run_main):
    current = {"hs3": {"sensor": {}}, "stored": FROZEN_SURFACE["stored"]}

    _, printed = run_main(Commands(frozen=FROZEN_SURFACE, current=current))

    assert printed == "hs3 sensor battery_power: missing\n"


def test_a_value_changed_to_nothing_is_shown_as_json(run_main):
    frozen = {"hs3": {"sensor": {"soc": {"unit": "%"}}}}
    current = {"hs3": {"sensor": {"soc": {"unit": None}}}}

    _, printed = run_main(Commands(frozen=frozen, current=current))

    assert printed == "hs3 sensor soc: unit % -> null\n"


def test_a_failed_archive_is_reported_as_an_error(run_main):
    status, printed = run_main(Commands(archive_fails=True))

    assert status == 1
    assert printed == f"error git archive of {TAG} failed: fatal: not a valid object\n"


def test_a_failed_surface_script_is_reported_with_its_last_line(run_main):
    status, printed = run_main(Commands(frozen=None, current=FROZEN_SURFACE))

    assert status == 1
    assert printed.startswith("error surface of ")
    assert printed.endswith("failed: SurfaceError: no names\n")


def test_a_failed_surface_script_with_no_output_says_so(run_main):
    def silent(argv):
        if argv[0] == "git":
            return completed(stdout=f"{TAG}\n")
        return completed(returncode=1)

    status, printed = run_main(silent)

    assert status == 1
    assert printed.endswith("failed: no output\n")


def test_the_tagged_tree_runs_its_own_script_and_the_working_tree_the_current_one(
    run_main,
):
    commands = Commands(frozen=FROZEN_SURFACE, current=FROZEN_SURFACE)

    run_main(commands)

    frozen_call, current_call = commands.calls[-2:]
    assert frozen_call[1].endswith("tree/.github/scripts/freeze_surface.py")
    assert frozen_call[2].endswith("tree")
    assert current_call[1] == str(
        Path(freeze_check.__file__).with_name("freeze_surface.py")
    )
    assert current_call[2] == CURRENT_TREE


def test_the_default_tree_is_the_working_directory(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    commands = Commands(frozen=FROZEN_SURFACE, current=FROZEN_SURFACE)

    freeze_check.main(run=commands, unpack=unpacked_nowhere)

    assert commands.calls[-1][2] == str(tmp_path)
    capsys.readouterr()


def test_the_real_runner_captures_text_output(monkeypatch):
    captured = {}

    def fake_run(argv, **options):
        captured.update(argv=argv, **options)
        return completed(stdout="out")

    monkeypatch.setattr(freeze_check.subprocess, "run", fake_run)

    result = freeze_check.run_command(("git", "status"))

    assert result.stdout == "out"
    assert captured["argv"] == ("git", "status")
    assert captured["capture_output"] is True
    assert captured["text"] is True
    assert captured["check"] is False
    assert captured["timeout"] == freeze_check.COMMAND_TIMEOUT_SECONDS


def test_running_the_check_as_a_script_exits_with_the_status_of_main(monkeypatch):
    def no_tag(argv, **options):
        del argv, options
        return completed(returncode=128)

    monkeypatch.setattr(subprocess, "run", no_tag)
    monkeypatch.setattr(sys, "argv", ["freeze_check.py"])

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("freeze_check", run_name="__main__")

    assert stopped.value.code == 0
