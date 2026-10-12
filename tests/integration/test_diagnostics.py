from types import SimpleNamespace

import pytest

from custom_components.saj_local.const import PowerSchedule
from custom_components.saj_local.coordinator import LastWrite, WriteStatistics
from custom_components.saj_local.diagnostics import async_get_config_entry_diagnostics
from custom_components.saj_local.equipment import (
    EquipmentReport,
    PackReport,
    report_summary,
)
from custom_components.saj_local.errors import WriteOutcome
from custom_components.saj_local.saj.budget import BUDGET_PER_MINUTE
from custom_components.saj_local.saj.catalogue import Row
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.ems import EmsOwnership
from custom_components.saj_local.saj.equipment import Detection, Setting
from custom_components.saj_local.saj.health import Break, Refusal, Region
from custom_components.saj_local.saj.models import Equipment, PowerFunction
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from custom_components.saj_local.saj.poller import CadencePlan
from custom_components.saj_local.saj.telemetry import Telemetry
from tests.profiles import profile

PRIVATE_KEYS = (
    "product_code",
    "ethernet_mac_address",
    "ethernet_ip_address",
    "ethernet_subnet_mask",
    "ethernet_gateway",
    "ethernet_dns_primary",
    "ethernet_dns_secondary",
    "ev_serial_number",
)
PROFILE = profile(
    base=HS3,
    key="alpha",
    device_types={0x1610},
    keys={"operating_mode", "ethernet_mode", "pv_power", *PRIVATE_KEYS},
    hand_verified=False,
)
DEVICE = Device("PRIVATE-SERIAL", 0x1610, 12000, PROFILE, detected=True)


NOW = 5000.0
SCHEDULE_STATES: dict[str, SimpleNamespace] = {}
HASS = SimpleNamespace(
    loop=SimpleNamespace(time=lambda: NOW),
    states=SimpleNamespace(get=SCHEDULE_STATES.get),
)


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
        self.narrowing = ()
        self.breaks = frozenset()
        self.plans = ()
        self.load = 0.0

    def cadence_plans(self):
        return self.plans

    def planned_load(self):
        return self.load


class FakeAllowance:
    limit = 10
    window = 60.0

    def used(self, *, now):
        assert now == NOW
        return 4


class FakeCoordinator:
    def __init__(self, contexts, telemetry) -> None:
        self._contexts = contexts
        self.data = telemetry
        self.last_update_success = True
        self.last_error = None
        self.last_read = frozenset()
        self.device = DEVICE
        self.poller = FakePoller()
        self.guard = SimpleNamespace(allowance=FakeAllowance())
        self.writes = WriteStatistics()
        self.ems = EmsOwnership()
        self.heartbeat_interval = 60
        self.power_offered = ()
        self.power_controls = {}
        self.power_state = {}
        self.schedules = ()
        self.outstanding = {}

    def power_running(self, *, function):
        return self.power_state.get(function)

    def async_contexts(self):
        return iter(self._contexts)

    @property
    def enabled_keys(self):
        return set(self._contexts)


@pytest.mark.parametrize(
    ("contexts", "telemetry", "expected_keys"),
    [
        (
            {"pv_power", "grid_power"},
            Telemetry(values={"operating_mode": 2}),
            ["grid_power", "pv_power"],
        ),
        (set(), Telemetry(values={"operating_mode": 31}), []),
        ({"battery_soc", "ev_mode"}, Telemetry(values={}), ["battery_soc", "ev_mode"]),
    ],
)
async def test_diagnostics_report_status_and_omit_endpoint_identity(
    contexts, telemetry, expected_keys
):
    entry = SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": "automatic"},
        options={"scan_interval": 60},
        unique_id="PRIVATE-SERIAL",
        runtime_data=SimpleNamespace(
            device=DEVICE,
            client=FakeClient(),
            equipment={},
            packs=PackReport(count_read=None, limit=None),
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
    assert result["enabled_keys"] == expected_keys
    assert result["connected"] is True
    assert result["last_update_success"] is True
    assert "private-host" not in str(result)
    assert "PRIVATE-SERIAL" not in str(result)


@pytest.mark.parametrize(
    ("selection", "detected"), [("alpha", False), ("automatic", True)]
)
async def test_diagnostics_report_selection_and_whether_profile_was_assumed(
    selection, detected
):
    entry = SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": selection},
        options={},
        runtime_data=_runtime(
            coordinator=FakeCoordinator(set(), None),
            device=Device("PRIVATE-SERIAL", 0x1610, 12000, PROFILE, detected=detected),
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
            device=DEVICE,
            client=client or FakeClient(),
            equipment={},
            packs=PackReport(count_read=None, limit=None),
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
            "keys": ["grid_power", "pv_power"],
            "requests_per_read": 2,
        },
        {
            "default": False,
            "interval_seconds": 10,
            "keys": ["battery_soc"],
            "requests_per_read": 1,
        },
    ]
    assert result["planned_requests_per_minute"] == 8.0
    assert result["request_budget_per_minute"] == BUDGET_PER_MINUTE
    assert result["last_cycle_read"] == ["battery_soc", "pv_power"]


async def test_diagnostics_report_refused_and_suspended_keys_with_retest_timing():
    coordinator = FakeCoordinator(set(), None)
    coordinator.poller.refusals = {
        "pv_power": Refusal(count=1, code=2, retest_at=None),
        "grid_power": Refusal(count=3, code=0, retest_at=NOW + 600),
        "battery_soc": Refusal(count=7, code=11, retest_at=NOW - 5),
    }

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert result["refused_keys"] == {
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
        ({"prefix": "private-house"}, "<domain>.saj_[redacted]_<key>"),
        ({"prefix": ""}, "<domain>.saj_<key>"),
        ({}, "<domain>.saj_<key>"),
    ],
)
async def test_diagnostics_show_whether_a_prefix_is_set_without_revealing_it(
    options, pattern
):
    entry = _entry_of(FakeCoordinator(set(), None), **options)

    result = await async_get_config_entry_diagnostics(HASS, entry)

    assert result["entity_id_pattern"] == pattern
    assert "private-house" not in str(result)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ({"operating_mode": 31}, {"operating_mode": 31}),
        ({"operating_mode": 2}, {}),
        (
            {"operating_mode": 31.0, "ethernet_mode": 9},
            {"operating_mode": 31.0, "ethernet_mode": 9},
        ),
        ({"operating_mode": None, "pv_power": 99999}, {}),
        ({"operating_mode": "text"}, {}),
    ],
)
async def test_diagnostics_report_the_unknown_codes_of_enumerated_rows_by_key(
    values, expected
):
    coordinator = FakeCoordinator(set(), Telemetry(values=values))

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert result["unknown_codes"] == expected


async def test_diagnostics_report_no_unknown_codes_before_any_data_was_read():
    result = await async_get_config_entry_diagnostics(
        HASS, _entry(FakeCoordinator(set(), None))
    )

    assert result["unknown_codes"] == {}


async def test_diagnostics_report_the_breaks_found_in_address_order():
    coordinator = FakeCoordinator(set(), None)
    coordinator.poller.breaks = frozenset(
        {Break(before=0x4100, after=0x4104), Break(before=0x4010, after=0x4012)}
    )

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert result["breaks"] == [
        {"before": "0x4010", "after": "0x4012"},
        {"before": "0x4100", "after": "0x4104"},
    ]


async def test_diagnostics_report_the_requests_being_narrowed():
    coordinator = FakeCoordinator(set(), None)
    coordinator.poller.narrowing = (
        Region(rows=(Row(address=0x4000, words=2), Row(address=0x4005, words=1))),
    )

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert result["narrowing"] == [{"before": "0x4000", "after": "0x4006", "rows": 2}]


async def test_diagnostics_report_no_breaks_or_narrowing_when_there_are_none():
    result = await async_get_config_entry_diagnostics(
        HASS, _entry(FakeCoordinator(set(), None))
    )

    assert result["breaks"] == []
    assert result["narrowing"] == []


PRIVATE_VALUES = {
    "product_code": "PRIVATE-PRODUCT",
    "ethernet_mac_address": "AA:BB:CC:DD:EE:FF",
    "ethernet_ip_address": "192.0.2.10",
    "ethernet_subnet_mask": "255.255.255.0",
    "ethernet_gateway": "192.0.2.1",
    "ethernet_dns_primary": "198.51.100.1",
    "ethernet_dns_secondary": "198.51.100.2",
    "ev_serial_number": "PRIVATE-EV-SERIAL",
}


@pytest.mark.parametrize("key", sorted(PRIVATE_VALUES))
async def test_diagnostics_never_include_the_value_of_a_private_row(key):
    coordinator = FakeCoordinator(
        set(PRIVATE_VALUES), Telemetry(values={**PRIVATE_VALUES, "operating_mode": 31})
    )
    coordinator.last_read = frozenset(PRIVATE_VALUES)

    result = await async_get_config_entry_diagnostics(HASS, _entry(coordinator))

    assert PRIVATE_VALUES[key] not in str(result)
    assert "PRIVATE-SERIAL" not in str(result)


def _runtime(*, coordinator, device=DEVICE):
    return SimpleNamespace(
        device=device,
        client=FakeClient(),
        equipment={},
        packs=PackReport(count_read=None, limit=None),
        coordinator=coordinator,
    )


def _entry_of(coordinator, **options):
    return SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": "automatic"},
        options=options,
        runtime_data=_runtime(coordinator=coordinator),
    )


@pytest.mark.parametrize("allowed", [True, False])
async def test_diagnostics_say_whether_control_is_on_and_how_much_allowance_is_used(
    *, allowed
):
    coordinator = FakeCoordinator(set(), None)

    result = await async_get_config_entry_diagnostics(
        HASS, _entry_of(coordinator, allow_control=allowed)
    )

    assert result["control_enabled"] is allowed
    assert result["write_allowance"] == {
        "limit": 10,
        "window_seconds": 60.0,
        "used": 4,
    }


async def test_diagnostics_default_to_control_off_and_no_write_history():
    result = await async_get_config_entry_diagnostics(
        HASS, _entry_of(FakeCoordinator(set(), None))
    )

    assert result["control_enabled"] is False
    assert result["last_write"] is None
    assert result["writes_acknowledged"] == 0
    assert result["ems_functions_owned"] == []


async def test_diagnostics_count_writes_beats_and_name_the_last_write_without_a_value():
    coordinator = FakeCoordinator(set(), None)
    coordinator.writes = WriteStatistics(
        acknowledged=5,
        rejected=2,
        unconfirmed=1,
        last=LastWrite(
            key="backup_reserve_soc",
            outcome=WriteOutcome.REJECTED,
            exception_code=3,
        ),
        beats_sent=7,
        beats_dropped=1,
    )
    coordinator.heartbeat_interval = 90
    coordinator.ems.acquire(function=PowerFunction.GRID)
    coordinator.ems.acquire(function=PowerFunction.BATTERY)

    result = await async_get_config_entry_diagnostics(
        HASS, _entry_of(coordinator, allow_control=True)
    )

    assert result["writes_acknowledged"] == 5
    assert result["writes_rejected"] == 2
    assert result["writes_unconfirmed"] == 1
    assert result["last_write"] == {
        "key": "backup_reserve_soc",
        "outcome": "rejected",
        "exception_code": 3,
    }
    assert result["ems_heartbeat_interval_seconds"] == 90
    assert result["ems_functions_owned"] == ["battery", "grid"]
    assert result["ems_beats_sent"] == 7
    assert result["ems_beats_dropped"] == 1


async def test_diagnostics_report_each_equipment_with_its_probe_values_and_result():
    entry = SimpleNamespace(
        data={"host": "private-host", "port": 502, "unit_id": 1, "model": "automatic"},
        options={},
        unique_id="PRIVATE-SERIAL",
        runtime_data=SimpleNamespace(
            device=DEVICE,
            client=FakeClient(),
            equipment={
                Equipment.BATTERY: EquipmentReport(
                    setting=Setting.AUTOMATIC,
                    detection=Detection(
                        equipment=Equipment.BATTERY,
                        fitted=True,
                        answered=True,
                        values={"battery_protocol": 24},
                    ),
                    remembered=True,
                    lapsed=False,
                    fitted=True,
                ),
                Equipment.METER_B: EquipmentReport(
                    setting=Setting.FITTED,
                    detection=None,
                    remembered=False,
                    lapsed=False,
                    fitted=True,
                ),
            },
            packs=PackReport(count_read=3, limit=2),
            coordinator=FakeCoordinator(set(), None),
        ),
    )

    result = await async_get_config_entry_diagnostics(HASS, entry)

    assert result["battery_packs"] == {"count_read": 3, "limit_in_use": 2}
    assert result["equipment"] == report_summary(reports=entry.runtime_data.equipment)
    assert result["equipment"]["battery"]["probe_values"] == {"battery_protocol": 24}
    assert result["equipment"]["meter_b"]["probe_values"] is None


class FakeMethod:
    def __init__(self, name: str) -> None:
        self.method_name = name


@pytest.fixture
def schedule_states():
    SCHEDULE_STATES.clear()
    yield SCHEDULE_STATES
    SCHEDULE_STATES.clear()


async def test_diagnostics_list_power_control_functions_schedules_and_outstanding(
    schedule_states,
):
    coordinator = FakeCoordinator(set(), Telemetry(values={}))
    coordinator.power_offered = (PowerFunction.BATTERY, PowerFunction.GRID)
    coordinator.power_controls = {
        PowerFunction.BATTERY: FakeMethod("operating_mode"),
        PowerFunction.GRID: FakeMethod("enable_bit"),
    }
    coordinator.power_state = {PowerFunction.BATTERY: True, PowerFunction.GRID: None}
    coordinator.ems.acquire(function=PowerFunction.BATTERY)
    coordinator.schedules = (
        PowerSchedule(function=PowerFunction.BATTERY, entity_id="schedule.night"),
        PowerSchedule(function=PowerFunction.GRID, entity_id="schedule.gone"),
    )
    coordinator.outstanding = {PowerFunction.GRID: "no_target"}
    schedule_states["schedule.night"] = SimpleNamespace(state="on")

    result = await async_get_config_entry_diagnostics(HASS, _entry_for(coordinator))

    assert result["power_control"] == {
        "functions": {
            "battery": {"method": "operating_mode", "running": True, "owned": True},
            "grid": {"method": "enable_bit", "running": None, "owned": False},
        },
        "schedules": [
            {
                "function": "battery",
                "schedule": "schedule.night",
                "on": True,
                "outstanding": None,
            },
            {
                "function": "grid",
                "schedule": "schedule.gone",
                "on": False,
                "outstanding": "no_target",
            },
        ],
    }


async def test_diagnostics_have_no_power_control_where_a_system_has_none():
    coordinator = FakeCoordinator(set(), Telemetry(values={}))

    result = await async_get_config_entry_diagnostics(HASS, _entry_for(coordinator))

    assert result["power_control"] == {"functions": {}, "schedules": []}


def _entry_for(coordinator):
    return SimpleNamespace(
        data={"model": "automatic"},
        options={},
        unique_id="PRIVATE-SERIAL",
        runtime_data=SimpleNamespace(
            device=DEVICE,
            client=FakeClient(),
            equipment={},
            packs=PackReport(count_read=None, limit=None),
            coordinator=coordinator,
        ),
    )
