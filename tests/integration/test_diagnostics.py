from types import SimpleNamespace

import pytest

from custom_components.saj_local.diagnostics import async_get_config_entry_diagnostics
from custom_components.saj_local.saj.hs3 import Hs3Device, Hs3Telemetry


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
        ({"pv_power", "grid_power"}, Hs3Telemetry(2), ["grid_power", "pv_power"], None),
        (set(), Hs3Telemetry(31), [], 31),
        ({"battery_soc"}, Hs3Telemetry(), ["battery_soc"], None),
    ],
)
async def test_diagnostics_report_status_and_omit_endpoint_identity(
    contexts, telemetry, expected_sensors, unknown_mode
):
    entry = SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1},
        options={"scan_interval": 60},
        unique_id="PRIVATE-SERIAL",
        runtime_data=SimpleNamespace(
            device=Hs3Device("PRIVATE-SERIAL", 0x1610, 12000),
            client=FakeClient(),
            coordinator=FakeCoordinator(contexts, telemetry),
        ),
    )

    result = await async_get_config_entry_diagnostics(None, entry)

    assert result["profile"] == "HS3"
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
