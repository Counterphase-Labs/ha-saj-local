from types import SimpleNamespace

import pytest

from custom_components.saj_local.diagnostics import async_get_config_entry_diagnostics
from custom_components.saj_local.saj.budget import BUDGET_PER_MINUTE
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.health import Refusal
from custom_components.saj_local.saj.poller import CadencePlan
from custom_components.saj_local.saj.profiles import Profile
from custom_components.saj_local.saj.telemetry import Telemetry

PROFILE = Profile(
    key="alpha",
    display_name="Alpha",
    device_types=frozenset({0x0001}),
    measurement_keys=frozenset(),
    hand_verified=False,
)


NOW = 5000.0
HASS = SimpleNamespace(loop=SimpleNamespace(time=lambda: NOW))


class FakeClient:
    late_frames_discarded = 0

    def is_connected(self) -> bool:
        return True


class FakePoller:
    stale_reconnects = 0
    consecutive_failures = 0
    backoff_seconds = 0.0

    def __init__(self) -> None:
        self.refusals = {}
        self.plans = ()
        self.load = 0.0

    def cadence_plans(self):
        return self.plans

    def planned_load(self):
        return self.load


class FakeCoordinator:
    def __init__(self, contexts, telemetry) -> None:
        self._contexts = contexts
        self.data = telemetry
        self.last_update_success = True
        self.last_error = None
        self.last_read = frozenset()
        self.poller = FakePoller()

    def async_contexts(self):
        return iter(self._contexts)

    @property
    def enabled_sensor_keys(self):
        return set(self._contexts)


@pytest.mark.parametrize(
    ("contexts", "telemetry", "expected_sensors", "unknown_mode"),
    [
        (
            {"pv_power", "grid_power"},
            Telemetry(values={"operating_mode": 2}),
            ["grid_power", "pv_power"],
            None,
        ),
        (set(), Telemetry(values={"operating_mode": 31}), [], 31),
        ({"battery_soc"}, Telemetry(values={}), ["battery_soc"], None),
    ],
)
async def test_diagnostics_report_status_and_omit_endpoint_identity(
    contexts, telemetry, expected_sensors, unknown_mode
):
    entry = SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": "automatic"},
        options={"scan_interval": 60},
        unique_id="PRIVATE-SERIAL",
        runtime_data=SimpleNamespace(
            device=Device("PRIVATE-SERIAL", 0x1610, 12000, PROFILE, detected=True),
            client=FakeClient(),
            coordinator=FakeCoordinator(contexts, telemetry),
        ),
    )

    result = await async_get_config_entry_diagnostics(HASS, entry)

    assert result["model_selection"] == "automatic"
    assert result["profile"] == "alpha"
    assert result["profile_detected"] is True
    assert result["profile_hand_verified"] is False
    assert result["device_type"] == 0x1610
    assert result["rated_power_w"] == 12000
    assert result["poll_interval_seconds"] == 60
    assert result["enabled_sensors"] == expected_sensors
    assert result["connected"] is True
    assert result["last_update_success"] is True
    assert "private-host" not in str(result)
    assert "PRIVATE-SERIAL" not in str(result)
    if unknown_mode is not None:
        assert result["unknown_operating_mode"] == unknown_mode
    else:
        assert "unknown_operating_mode" not in result


@pytest.mark.parametrize(
    ("selection", "detected"), [("alpha", False), ("automatic", True)]
)
async def test_diagnostics_report_selection_and_whether_profile_was_assumed(
    selection, detected
):
    entry = SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": selection},
        options={},
        runtime_data=SimpleNamespace(
            device=Device("PRIVATE-SERIAL", 0x1610, 12000, PROFILE, detected=detected),
            client=FakeClient(),
            coordinator=FakeCoordinator(set(), None),
        ),
    )

    result = await async_get_config_entry_diagnostics(HASS, entry)

    assert result["model_selection"] == selection
    assert result["profile_detected"] is detected


def _entry(coordinator, client=None):
    return SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": "automatic"},
        options={},
        subentries={
            "id-1": SimpleNamespace(title="Private group name", data={}),
        },
        runtime_data=SimpleNamespace(
            device=Device("PRIVATE-SERIAL", 0x1610, 12000, PROFILE, detected=True),
            client=client or FakeClient(),
            coordinator=coordinator,
        ),
    )


async def test_diagnostics_report_cadences_and_planned_load_against_the_budget():
    coordinator = FakeCoordinator(set(), None)
    coordinator.poller.plans = (
        CadencePlan(
            interval=60,
            keys=frozenset({"pv_power", "grid_power"}),
            ranges=((0x4004, 1), (0x40A5, 3)),
            default=True,
        ),
        CadencePlan(
            interval=10,
            keys=frozenset({"battery_soc"}),
            ranges=((0x406F, 1),),
            default=False,
        ),
    )
    coordinator.poller.load = 8.0
    coordinator.last_read = frozenset({"pv_power", "battery_soc"})

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert result["cadences"] == [
        {
            "default": True,
            "interval_seconds": 60,
            "sensors": ["grid_power", "pv_power"],
            "requests_per_read": 2,
        },
        {
            "default": False,
            "interval_seconds": 10,
            "sensors": ["battery_soc"],
            "requests_per_read": 1,
        },
    ]
    assert result["planned_requests_per_minute"] == 8.0
    assert result["request_budget_per_minute"] == BUDGET_PER_MINUTE
    assert result["last_cycle_read"] == ["battery_soc", "pv_power"]


async def test_diagnostics_report_refused_and_suspended_sensors_with_retest_timing():
    coordinator = FakeCoordinator(set(), None)
    coordinator.poller.refusals = {
        "pv_power": Refusal(count=1, code=2, retest_at=None),
        "grid_power": Refusal(count=3, code=0, retest_at=NOW + 600),
        "battery_soc": Refusal(count=7, code=11, retest_at=NOW - 5),
    }

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert result["refused_sensors"] == {
        "pv_power": {
            "exception_code": 2,
            "consecutive_refusals": 1,
            "suspended": False,
            "next_retest_in_seconds": None,
        },
        "grid_power": {
            "exception_code": 0,
            "consecutive_refusals": 3,
            "suspended": True,
            "next_retest_in_seconds": 600,
        },
        "battery_soc": {
            "exception_code": 11,
            "consecutive_refusals": 7,
            "suspended": True,
            "next_retest_in_seconds": 0,
        },
    }


async def test_diagnostics_report_backoff_state_and_link_counters():
    coordinator = FakeCoordinator(set(), None)
    coordinator.poller.consecutive_failures = 3
    coordinator.poller.backoff_seconds = 40.0
    coordinator.poller.stale_reconnects = 2
    client = FakeClient()
    client.late_frames_discarded = 5

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator, client))

    assert result["consecutive_failed_cycles"] == 3
    assert result["backoff_seconds"] == 40.0
    assert result["late_frames_discarded"] == 5
    assert result["stale_reconnects"] == 2


async def test_diagnostics_omit_group_names_host_and_serial():
    coordinator = FakeCoordinator({"pv_power"}, None)
    coordinator.poller.refusals = {"pv_power": Refusal(count=1, code=2, retest_at=None)}

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert "Private group name" not in str(result)
    assert "private-host" not in str(result)
    assert "PRIVATE-SERIAL" not in str(result)


@pytest.mark.parametrize(
    ("options", "pattern"),
    [
        ({"prefix": "private-house"}, "sensor.saj_[redacted]_<key>"),
        ({"prefix": ""}, "sensor.saj_<key>"),
        ({}, "sensor.saj_<key>"),
    ],
)
async def test_diagnostics_show_whether_a_prefix_is_set_without_revealing_it(
    options, pattern
):
    entry = SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": "automatic"},
        options=options,
        runtime_data=SimpleNamespace(
            device=Device("PRIVATE-SERIAL", 0x1610, 12000, PROFILE, detected=True),
            client=FakeClient(),
            coordinator=FakeCoordinator(set(), None),
        ),
    )

    result = await async_get_config_entry_diagnostics(HASS, entry)

    assert result["entity_id_pattern"] == pattern
    assert "private-house" not in str(result)
