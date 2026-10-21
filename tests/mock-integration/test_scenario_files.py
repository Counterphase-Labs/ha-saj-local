"""Every shipped scenario, built into a real machine with nothing stubbed."""

from pathlib import Path

import pytest

from saj_local_mock.exceptions import ControlError
from saj_local_mock.machine import Machine
from saj_local_mock.scenario import load_scenario

SCENARIO_DIRECTORY = Path(__file__).parents[2] / "mock" / "scenarios"
SCENARIO_FILES = sorted(SCENARIO_DIRECTORY.glob("*.yaml"))


def build_machine(*, path: Path) -> Machine:
    return Machine(scenario=load_scenario(path=path), monotonic=lambda: 0.0)


def scenario_ids() -> list[str]:
    return [path.stem for path in SCENARIO_FILES]


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=scenario_ids())
def test_every_setting_a_scenario_starts_with_is_one_a_write_would_accept(path):
    machine = build_machine(path=path)

    for name, value in machine.settings.items():
        machine.device.check_stored(name=name, value=value)


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=scenario_ids())
def test_a_snapshot_of_a_scenario_restores_into_a_fresh_machine_of_it(path):
    saved = build_machine(path=path)
    saved.set_settings(values={"app_mode": 2})
    snapshot = saved.snapshot()
    fresh = build_machine(path=path)

    fresh.restore(snapshot=snapshot)

    assert fresh.settings == saved.settings
    assert fresh.settings["app_mode"] == 2


NO_BATTERY_FILES = [path for path in SCENARIO_FILES if "no-battery" in path.name]


@pytest.mark.parametrize("path", NO_BATTERY_FILES, ids=lambda path: path.stem)
def test_an_empty_pack_mapping_is_accepted_without_a_battery(path):
    machine = build_machine(path=path)

    machine.set_faults(values={"packs": {}})


@pytest.mark.parametrize("path", NO_BATTERY_FILES, ids=lambda path: path.stem)
def test_pack_codes_are_refused_without_a_battery_in_a_real_machine(path):
    machine = build_machine(path=path)

    with pytest.raises(ControlError) as caught:
        machine.set_faults(values={"packs": {"1": {"fault": 1}}})

    assert (caught.value.key, caught.value.reason) == ("packs", "no battery fitted")


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=scenario_ids())
def test_every_option_of_every_enumerated_setting_has_a_label(path):
    settings = build_machine(path=path).describe()["settings"]

    unlabelled = [
        (setting["name"], option["value"])
        for setting in settings
        for option in setting["options"] or []
        if option["label"] is None
    ]

    assert unlabelled == []
