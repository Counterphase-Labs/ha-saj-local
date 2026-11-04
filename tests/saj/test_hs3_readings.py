import pytest

from saj.catalogue import CATALOGUES, device_keys
from saj.device import Device
from saj.models import ALL_EQUIPMENT, Equipment, Evidence, FunctionCode
from saj.models.hs3 import PROFILE as HS3
from saj.telemetry import plan_reads, read_telemetry
from tests.saj.fakes import MemoryClient

HS3_TYPE = 0x1610
EV_DATA_FIRST = 0x3024
EV_DATA_LAST = 0x30BB
METER_A_POWER_WORDS = {0xA03F: 100, 0xA045: 200, 0xA04B: 0xFFCE}
GRID_OUTPUT_POWER_WORDS = {0x4090: 100, 0x4092: 200, 0x4094: 300}
GRID_PHASE_KEYS = ("power", "apparent_power", "current", "power_factor")


def _device(*, equipment: frozenset[Equipment] = ALL_EQUIPMENT) -> Device:
    return Device(
        serial="SERIAL",
        device_type=HS3_TYPE,
        rated_power=12000,
        profile=HS3,
        detected=True,
        equipment=equipment,
    )


def test_only_the_charger_data_span_is_planned_as_an_input_register_read():
    ranges = plan_reads(device=_device())

    functions = {
        read_range.function
        for read_range in ranges
        if EV_DATA_FIRST <= read_range.address <= EV_DATA_LAST
    }
    others = {
        read_range.function
        for read_range in ranges
        if not EV_DATA_FIRST <= read_range.address <= EV_DATA_LAST
    }

    assert functions == {FunctionCode.INPUT}
    assert others == {FunctionCode.HOLDING}


async def test_the_charger_data_is_read_as_input_registers_and_the_rest_as_holding():
    client = MemoryClient()

    await read_telemetry(
        client=client,
        device=_device(),
        enabled={"ev_status", "ev_charge_power", "pv_power"},
    )

    assert client.input_reads == [(0x309D, 1)]
    assert sorted(client.reads) == [(0x40A5, 1), (0x4B14, 2)]


async def test_a_refused_input_request_refuses_the_charger_rows_with_their_function():
    client = MemoryClient(bad_addresses=frozenset({0x309D}), code=48)

    readout = await read_telemetry(
        client=client, device=_device(), enabled={"ev_status", "pv_power"}
    )

    assert readout.refusals == {"ev_status": 48}
    assert readout.outcomes[0].rows[0].function is FunctionCode.INPUT
    assert readout.outcomes[1].rows[0].function is FunctionCode.HOLDING
    assert "pv_power" in readout.values


async def test_the_control_pilot_voltage_uses_a_factor_of_one_tenth():
    readout = await read_telemetry(
        client=MemoryClient({0x30AF: 122}),
        device=_device(),
        enabled={"ev_control_pilot_voltage"},
    )

    assert readout.values["ev_control_pilot_voltage"] == pytest.approx(12.2)


async def test_grid_power_is_the_meter_a_total_with_the_grid_sign():
    readout = await read_telemetry(
        client=MemoryClient(METER_A_POWER_WORDS),
        device=_device(),
        enabled={"grid_power", "meter_a_power"},
    )

    assert readout.values["grid_power"] == readout.values["meter_a_power"] == -250


async def test_the_grid_phase_values_come_from_the_matching_meter_a_phase():
    client = MemoryClient(
        {0x4038: 2300, 0xA044: 150, 0xA045: 200, 0xA046: 345, 0xA047: 950}
    )

    readout = await read_telemetry(
        client=client,
        device=_device(),
        enabled={f"grid_l2_{name}" for name in (*GRID_PHASE_KEYS, "voltage")},
    )

    assert readout.values == {
        "grid_l2_voltage": 230,
        "grid_l2_current": 1.5,
        "grid_l2_power": -200,
        "grid_l2_apparent_power": 345,
        "grid_l2_power_factor": 0.95,
    }


async def test_home_power_is_the_sum_of_the_on_grid_output_phase_powers():
    readout = await read_telemetry(
        client=MemoryClient(GRID_OUTPUT_POWER_WORDS),
        device=_device(),
        enabled={"load_power"},
    )

    assert readout.values["load_power"] == 600


@pytest.mark.parametrize("key", ["grid_power", "load_power"])
async def test_a_failed_source_read_makes_the_combined_power_unavailable(key: str):
    failing = {
        "grid_power": frozenset({0xA045}),
        "load_power": frozenset({0x4092}),
    }[key]

    readout = await read_telemetry(
        client=MemoryClient(bad_addresses=failing, code=48),
        device=_device(),
        enabled={key},
    )

    assert key not in readout.values
    assert key in readout.refusals


def test_grid_power_and_the_grid_phase_measurements_need_meter_a():
    without = device_keys(fit=_device(equipment=frozenset({Equipment.BATTERY})).fit)
    with_meter = device_keys(fit=_device().fit)

    derived = {"grid_power"} | {
        f"grid_l{phase}_{name}" for phase in (1, 2, 3) for name in GRID_PHASE_KEYS
    }
    assert derived <= with_meter
    assert not derived & without
    assert {"grid_l1_voltage", "grid_l1_frequency", "load_power"} <= without


def test_the_dc_input_and_the_inverter_power_registers_are_not_read():
    addresses = {
        read_range.address + offset
        for read_range in plan_reads(device=_device())
        for offset in range(read_range.count)
    }
    rows = {
        register.row.address
        for register in CATALOGUES["hs3"].registers
        if register.row is not None
    }

    assert not {0x40A0, 0x40A7} & rows
    assert {0x40A5, 0x40A6, 0x40A9} <= addresses


VERIFIED_EV_KEYS = {
    "ev_serial_number",
    "ev_model",
    "ev_software_version",
    "ev_hardware_version",
    "ev_phase_count",
    "ev_minimum_power",
    "ev_work_mode",
    "ev_status",
    "ev_l1_voltage",
    "ev_l2_voltage",
    "ev_l3_voltage",
    "ev_total_energy",
    "ev_remote_control",
    "ev_current_setpoint",
    "ev_control_pilot_voltage",
}
RESPONDING_EV_KEYS = {
    "ev_maximum_power",
    "ev_power",
    "ev_charge_duration",
    "ev_session_energy",
    "ev_duty_cycle",
    "ev_session_start",
    "ev_session_end",
    "ev_l1_current",
    "ev_l2_current",
    "ev_l3_current",
    "ev_fault_word_1",
    "ev_fault_word_2",
}


def test_the_hs3_evidence_of_the_charger_and_power_rows_follows_the_live_test():
    evidence = {
        register.key: register.evidence for register in CATALOGUES["hs3"].registers
    }

    assert {key: evidence[key] for key in VERIFIED_EV_KEYS} == dict.fromkeys(
        VERIFIED_EV_KEYS, Evidence.VERIFIED
    )
    assert {key: evidence[key] for key in RESPONDING_EV_KEYS} == dict.fromkeys(
        RESPONDING_EV_KEYS, Evidence.RESPONDS_UNCHECKED
    )
    assert evidence["grid_power"] is Evidence.VERIFIED
    assert evidence["load_power"] is Evidence.VERIFIED
