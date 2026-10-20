from __future__ import annotations

from check_steps import (
    CHECK_STEP_NAMES,
    GROUPS,
    HELP_HELP,
    LOGS_HELP,
    STEPS_BY_NAME,
    Group,
    Help,
)

GROUP_SUCCESS = "one [x] line per step and a result line"
GROUP_FAILURE = (
    "a [ ] line per failed step with its details, a result line naming the failed "
    "steps, and a non-zero exit"
)
GROUP_ARGS = "not used; ONLY=<step,...> runs a subset of the steps"
MAKE_STEP_NAMES = (*CHECK_STEP_NAMES, "up", "down")
DETAIL_HINT = (
    "Run make help ARGS=<target> for the detail of one target: what the target "
    "runs, what the target prints on success and on failure, what ARGS does, and "
    "for a grouping target the steps the target runs."
)


class UnknownTargetError(Exception):
    pass


def _group_help(group: Group) -> Help:
    return Help(
        summary=group.summary,
        runs="the steps below, in order",
        success=GROUP_SUCCESS,
        failure=GROUP_FAILURE,
        args=GROUP_ARGS,
    )


def target_helps() -> dict[str, Help]:
    helps = {name: STEPS_BY_NAME[name].help for name in MAKE_STEP_NAMES}
    helps.update({group.name: _group_help(group) for group in GROUPS})
    helps["logs"] = LOGS_HELP
    helps["help"] = HELP_HELP
    return helps


def list_targets() -> str:
    helps = target_helps()
    width = max(len(name) for name in helps)
    rows = [f"{name.ljust(width)}  {help_.summary}" for name, help_ in helps.items()]
    return "\n".join([*rows, "", DETAIL_HINT])


def describe(name: str) -> str:
    helps = target_helps()
    if name not in helps:
        message = f"unknown target: {name}; make help lists every target"
        raise UnknownTargetError(message)
    help_ = helps[name]
    lines = [
        f"{name}: {help_.summary}",
        "",
        f"runs: {help_.runs}",
        f"on success: {help_.success}",
        f"on failure: {help_.failure}",
        f"ARGS: {help_.args}",
    ]
    group = next((group for group in GROUPS if group.name == name), None)
    if group:
        width = max(len(step) for step in group.steps)
        lines.extend(["", "steps:"])
        lines.extend(
            f"  {step.ljust(width)}  {STEPS_BY_NAME[step].help.summary}"
            for step in group.steps
        )
    return "\n".join(lines)
