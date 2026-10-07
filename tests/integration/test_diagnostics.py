from types import SimpleNamespace

import pytest

from custom_components.saj_local.diagnostics import async_get_config_entry_diagnostics
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.profiles import Profile
from custom_components.saj_local.saj.telemetry import Telemetry

PROFILE = Profile(
    key="alpha",
    display_name="Alpha",
    device_types=frozenset({0x0001}),
    measurement_keys=frozenset(),
    hand_verified=False,
)


class FakeClient:
    def is_connected(self) -> bool:
        return True


class FakeCoordinator:
    def __init__(self, contexts, telemetry) -> None:
        self._contexts = contexts
        self.data = telemetry
        self.last_update_success = True
        self.last_error = None

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

    result = await async_get_config_entry_diagnostics(None, entry)

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

    result = await async_get_config_entry_diagnostics(None, entry)

    assert result["model_selection"] == selection
    assert result["profile_detected"] is detected
