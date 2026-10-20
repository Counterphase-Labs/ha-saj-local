from __future__ import annotations

import check_help
import pytest
from check_steps import GROUPS, GROUPS_BY_NAME, STEPS, STEPS_BY_NAME, SUPPORT_STEPS

EVERY_TARGET = (
    "setup",
    "up",
    "down",
    "logs",
    "help",
    "lint",
    "test",
    "python-ci",
    "frontend-check",
    "frontend-ci",
    "ci",
    *(step.name for step in STEPS),
)


def test_every_make_target_has_help():
    assert set(check_help.target_helps()) == set(EVERY_TARGET)


@pytest.mark.parametrize("step", [*STEPS, *SUPPORT_STEPS], ids=lambda step: step.name)
def test_every_step_describes_what_it_runs_prints_and_takes(step):
    help_ = step.help

    assert all((help_.summary, help_.runs, help_.success, help_.failure, help_.args))


def test_every_group_runs_only_known_steps():
    assert all(step in STEPS_BY_NAME for group in GROUPS for step in group.steps)


def test_the_ci_group_runs_every_check_step():
    assert GROUPS_BY_NAME["ci"].steps == tuple(step.name for step in STEPS)


def test_the_list_has_a_line_per_target_with_the_summary_after_the_name():
    lines = check_help.list_targets().splitlines()[: len(EVERY_TARGET)]

    assert all(line.split(maxsplit=1)[0] in EVERY_TARGET for line in lines)
    assert lines[0].split(maxsplit=1) == ["ruff", STEPS_BY_NAME["ruff"].help.summary]


def test_the_list_ends_by_saying_how_to_get_the_detail_of_one_target():
    lines = check_help.list_targets().splitlines()

    assert lines[-2:] == ["", check_help.DETAIL_HINT]
    assert "make help ARGS=<target>" in check_help.DETAIL_HINT


def test_a_step_target_is_described_with_what_it_runs_prints_and_takes():
    help_ = STEPS_BY_NAME["mypy"].help

    assert check_help.describe("mypy") == "\n".join(
        [
            f"mypy: {help_.summary}",
            "",
            f"runs: {help_.runs}",
            f"on success: {help_.success}",
            f"on failure: {help_.failure}",
            f"ARGS: {help_.args}",
        ]
    )


def test_a_group_target_is_described_with_the_summary_of_each_step():
    lines = check_help.describe("lint").splitlines()

    assert lines[0].startswith("lint: ")
    assert lines[2] == "runs: the steps below, in order"
    assert lines[5] == "ARGS: not used; ONLY=<step,...> runs a subset of the steps"
    assert lines[7] == "steps:"
    assert lines[8:] == [
        f"  {name.ljust(len('import-lint'))}  {STEPS_BY_NAME[name].help.summary}"
        for name in GROUPS_BY_NAME["lint"].steps
    ]


def test_an_unknown_target_is_an_error_naming_the_target():
    with pytest.raises(check_help.UnknownTargetError, match="unknown target: nope"):
        check_help.describe("nope")
