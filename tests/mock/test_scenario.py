from datetime import UTC, datetime, time

import pytest
import yaml

from saj_local_mock.link import LinkSettings, RefusedBlock
from saj_local_mock.scenario import (
    ScenarioError,
    dump_scenario,
    load_scenario,
    parse_scenario,
)
from saj_local_mock.simulation.environment import Variation
from saj_local_mock.simulation.faults import FaultBit, FaultState, PackCodes

HS3 = {"device": {"model": "hs3"}}
H2 = {"device": {"model": "h2"}}


def test_a_scenario_stating_only_the_model_gets_working_defaults():
    scenario = parse_scenario(data=HS3)

    assert scenario.device.rated_power_w == 12000
    assert scenario.server.port == 502
    assert scenario.server.max_clients == 2
    assert scenario.simulation.start == datetime(2026, 6, 21, 5, 0, tzinfo=UTC)
    assert scenario.site.pv_strings == (6000, 6000)
    assert scenario.battery.modules == 2
    assert scenario.meters.meter_a
    assert not scenario.ev_charger.installed
    assert scenario.parallel.inverters == 1
    assert scenario.server.panel_port == 8080
    assert scenario.variation == Variation()
    assert scenario.faults == FaultState()
    assert scenario.link == LinkSettings()


def test_models_default_to_their_own_rating_and_serial():
    hs3 = parse_scenario(data=HS3)
    h2 = parse_scenario(data=H2)

    assert h2.device.rated_power_w == 6000
    assert h2.device.serial_number != hs3.device.serial_number


def test_every_section_can_be_stated():
    scenario = parse_scenario(
        data={
            "device": {"model": "hs3", "rated_power_w": 10000, "serial_number": "ABC"},
            "server": {
                "port": 1502,
                "unit_id": 3,
                "max_clients": 4,
                "panel_port": 9090,
            },
            "simulation": {
                "seed": 9,
                "start": "2026-01-02T03:04:05+02:00",
                "speed": 60,
            },
            "site": {
                "grid_connected": False,
                "pv_strings": [{"peak_power_w": 1000}],
                "load": {"base_w": 100, "peak_w": 200},
            },
            "battery": {
                "modules": 3,
                "module_capacity_ah": 60,
                "initial_soc_percent": 70,
            },
            "meters": {"meter_a": False, "meter_b": False},
            "ev_charger": {
                "installed": True,
                "phases": 3,
                "max_power_w": 9000,
                "sessions": [
                    {"plug_in": "08:15", "unplug": "17:00", "energy_needed_wh": 6000}
                ],
            },
            "parallel": {"inverters": 2},
            "variation": {"cloud_depth": 0.9, "voltage_period_s": 30},
            "faults": {
                "inverter": [
                    {"register": 0x4009, "bit": 23},
                    {"register": 0x4005, "bit": 23},
                    {"register": 0x4005, "bit": 23},
                ],
                "battery": [{"register": 0x400B, "bit": 10}],
                "ev_charger": [{"register": 0x30AD, "bit": 0}],
                "packs": [{"pack": 1, "fault": 2, "warning": 5}],
            },
        },
    )

    assert scenario.simulation.start == datetime(2026, 1, 2, 1, 4, 5, tzinfo=UTC)
    assert scenario.site.pv_strings == (1000,)
    assert not scenario.site.grid_connected
    assert scenario.ev_charger.sessions[0].plug_in == time(8, 15)
    assert scenario.faults.inverter == {
        FaultBit(register=0x4005, bit=23),
        FaultBit(register=0x4009, bit=23),
    }
    assert scenario.faults.battery == {FaultBit(register=0x400B, bit=10)}
    assert scenario.faults.ev_charger == {FaultBit(register=0x30AD, bit=0)}
    assert scenario.faults.packs == (PackCodes(pack=1, fault=2, warning=5),)
    assert scenario.server.panel_port == 9090
    assert scenario.variation == Variation(cloud_depth=0.9, voltage_period_s=30)


@pytest.mark.parametrize(
    ("data", "key"),
    [
        ([], ""),
        ({}, "device.model"),
        ({"device": 5}, "device"),
        ({"device": {"model": 5}}, "device.model"),
        ({"device": {"model": "x9"}}, "device.model"),
        ({"device": {"model": "hs3", "rated_power_w": 7000}}, "device.rated_power_w"),
        ({"device": {"model": "hs3", "rated_power_w": True}}, "device.rated_power_w"),
        ({"device": {"model": "hs3", "serial_number": ""}}, "device.serial_number"),
        ({**HS3, "bogus": 1}, "bogus"),
        ({**HS3, "server": {"portt": 1}}, "server.portt"),
        ({**HS3, "server": {"port": 70000}}, "server.port"),
        ({**HS3, "server": {"max_clients": 0}}, "server.max_clients"),
        ({**HS3, "simulation": {"seed": "x"}}, "simulation.seed"),
        ({**HS3, "simulation": {"speed": -1}}, "simulation.speed"),
        ({**HS3, "simulation": {"speed": "fast"}}, "simulation.speed"),
        ({**HS3, "simulation": {"start": "nonsense"}}, "simulation.start"),
        ({**HS3, "site": {"grid_connected": "yes"}}, "site.grid_connected"),
        ({**HS3, "site": {"pv_strings": 4}}, "site.pv_strings"),
        ({**HS3, "site": {"pv_strings": [{"peak_power_w": 1}] * 5}}, "site.pv_strings"),
        ({**HS3, "site": {"pv_strings": [5]}}, "site.pv_strings[0]"),
        ({**HS3, "site": {"pv_strings": [{"peak": 1}]}}, "site.pv_strings[0].peak"),
        ({**HS3, "site": {"load": {"base_w": 500, "peak_w": 100}}}, "site.load.peak_w"),
        ({**HS3, "battery": {"modules": 9}}, "battery.modules"),
        ({**H2, "battery": {"modules": 6}}, "battery.modules"),
        (
            {**HS3, "battery": {"initial_soc_percent": 101}},
            "battery.initial_soc_percent",
        ),
        ({**H2, "ev_charger": {"installed": True}}, "ev_charger.installed"),
        ({**HS3, "ev_charger": {"phases": 2}}, "ev_charger.phases"),
        (
            {
                **HS3,
                "ev_charger": {
                    "sessions": [
                        {"plug_in": "6pm", "unplug": "07:00", "energy_needed_wh": 1}
                    ]
                },
            },
            "ev_charger.sessions[0].plug_in",
        ),
        (
            {
                **HS3,
                "ev_charger": {
                    "sessions": [
                        {"plug_in": "25:00", "unplug": "07:00", "energy_needed_wh": 1}
                    ]
                },
            },
            "ev_charger.sessions[0].plug_in",
        ),
        (
            {
                **HS3,
                "ev_charger": {
                    "sessions": [
                        {"plug_in": "18:00", "unplug": 7, "energy_needed_wh": 1}
                    ]
                },
            },
            "ev_charger.sessions[0].unplug",
        ),
        (
            {
                **HS3,
                "ev_charger": {"sessions": [{"plug_in": "18:00", "unplug": "07:00"}]},
            },
            "ev_charger.sessions[0].energy_needed_wh",
        ),
        (
            {**HS3, "ev_charger": {"sessions": [{"plug_in": "18:00"}]}},
            "ev_charger.sessions[0].unplug",
        ),
        ({**HS3, "parallel": {"inverters": 3}}, "parallel.inverters"),
        ({**HS3, "server": {"response_delay_ms": 5}}, "server.response_delay_ms"),
        ({**HS3, "server": {"panel_port": 70000}}, "server.panel_port"),
        ({**HS3, "link": 5}, "link"),
        ({**HS3, "link": {"latency": 5}}, "link.latency"),
        ({**HS3, "link": {"latency_ms": -1}}, "link.latency_ms"),
        ({**HS3, "link": {"latency_ms": 60001}}, "link.latency_ms"),
        ({**HS3, "link": {"latency_ms": 1.5}}, "link.latency_ms"),
        ({**HS3, "link": {"jitter_ms": "x"}}, "link.jitter_ms"),
        ({**HS3, "link": {"busy_percent": 101}}, "link.busy_percent"),
        ({**HS3, "link": {"no_answer_percent": -0.5}}, "link.no_answer_percent"),
        (
            {**HS3, "link": {"late_duplicate_percent": "x"}},
            "link.late_duplicate_percent",
        ),
        ({**HS3, "link": {"offline": 1}}, "link.offline"),
        ({**HS3, "link": {"unresponsive": "yes"}}, "link.unresponsive"),
        ({**HS3, "link": {"lockout_whole_port": 0}}, "link.lockout_whole_port"),
        ({**HS3, "link": {"lockout_requests": 100001}}, "link.lockout_requests"),
        (
            {**HS3, "link": {"offline_seconds": 30, "offline_period_seconds": 10}},
            "link.offline_seconds",
        ),
        ({**HS3, "link": {"offline_seconds": 5}}, "link.offline_seconds"),
        ({**HS3, "link": {"lockout_requests": 5}}, "link.lockout_window_seconds"),
        ({**HS3, "link": {"refused_blocks": 5}}, "link.refused_blocks"),
        ({**HS3, "link": {"refused_blocks": [5]}}, "link.refused_blocks[0]"),
        (
            {**HS3, "link": {"refused_blocks": [{"end": 2, "code": 1}]}},
            "link.refused_blocks[0].start",
        ),
        (
            {**HS3, "link": {"refused_blocks": [{"start": 1, "code": 1}]}},
            "link.refused_blocks[0].end",
        ),
        (
            {**HS3, "link": {"refused_blocks": [{"start": 1, "end": 2}]}},
            "link.refused_blocks[0].code",
        ),
        (
            {
                **HS3,
                "link": {"refused_blocks": [{"start": 1, "end": 70000, "code": 1}]},
            },
            "link.refused_blocks[0].end",
        ),
        (
            {**HS3, "link": {"refused_blocks": [{"start": 9, "end": 2, "code": 1}]}},
            "link.refused_blocks[0].end",
        ),
        (
            {**HS3, "link": {"refused_blocks": [{"start": 1, "end": 2, "code": 256}]}},
            "link.refused_blocks[0].code",
        ),
        (
            {
                **HS3,
                "link": {"refused_blocks": [{"start": 1, "end": 2, "code": 1, "x": 1}]},
            },
            "link.refused_blocks[0].x",
        ),
        ({**HS3, "simulation": {"seed": 1 << 33}}, "simulation.seed"),
        ({**HS3, "variation": {"cloud_dept": 1}}, "variation.cloud_dept"),
        ({**HS3, "variation": {"cloud_depth": 2}}, "variation.cloud_depth"),
        ({**HS3, "variation": {"cloud_depth": "x"}}, "variation.cloud_depth"),
        ({**HS3, "variation": {"cloud_period_s": 90.5}}, "variation.cloud_period_s"),
        ({**HS3, "variation": {"cloud_period_s": 1}}, "variation.cloud_period_s"),
        ({**HS3, "variation": {"base_w": 100}}, "variation.base_w"),
        ({**HS3, "variation": 5}, "variation"),
        ({**HS3, "faults": {"inverter_fault_bits": [1]}}, "faults.inverter_fault_bits"),
        ({**HS3, "faults": {"inverter": 5}}, "faults.inverter"),
        ({**HS3, "faults": {"inverter": [5]}}, "faults.inverter[0]"),
        (
            {**HS3, "faults": {"inverter": [{"bit": 1}]}},
            "faults.inverter[0].register",
        ),
        (
            {**HS3, "faults": {"inverter": [{"register": 0x4005}]}},
            "faults.inverter[0].bit",
        ),
        (
            {**HS3, "faults": {"inverter": [{"register": 0x400B, "bit": 1}]}},
            "faults.inverter[0].register",
        ),
        (
            {**HS3, "faults": {"inverter": [{"register": 0x4005, "bit": 32}]}},
            "faults.inverter[0].bit",
        ),
        (
            {**HS3, "faults": {"inverter": [{"register": 0x4005, "bit": True}]}},
            "faults.inverter[0].bit",
        ),
        (
            {**HS3, "faults": {"inverter": [{"register": 0x4005, "bit": 1, "x": 1}]}},
            "faults.inverter[0].x",
        ),
        (
            {
                **HS3,
                "battery": {"modules": 0},
                "faults": {"battery": [{"register": 0x400B, "bit": 1}]},
            },
            "faults.battery",
        ),
        (
            {**HS3, "faults": {"ev_charger": [{"register": 0x30AB, "bit": 1}]}},
            "faults.ev_charger",
        ),
        (
            {
                **HS3,
                "ev_charger": {"installed": True},
                "faults": {"ev_charger": [{"register": 0x4005, "bit": 1}]},
            },
            "faults.ev_charger[0].register",
        ),
        (
            {**HS3, "faults": {"packs": [{"pack": 2, "fault": 1}]}},
            "faults.packs[0].pack",
        ),
        (
            {**H2, "battery": {"modules": 5}, "faults": {"packs": [{"pack": 5}]}},
            "faults.packs[0].pack",
        ),
        ({**HS3, "faults": {"packs": [{"fault": 1}]}}, "faults.packs[0].pack"),
        (
            {**HS3, "faults": {"packs": [{"pack": 1, "fault": 70000}]}},
            "faults.packs[0].fault",
        ),
        (
            {**HS3, "faults": {"packs": [{"pack": 1, "warning": -1}]}},
            "faults.packs[0].warning",
        ),
        (
            {**HS3, "battery": {"modules": 0}, "faults": {"packs": [{"pack": 1}]}},
            "faults.packs",
        ),
    ],
)
def test_invalid_scenarios_are_refused_with_the_offending_key(data, key):
    with pytest.raises(ScenarioError) as caught:
        parse_scenario(data=data)

    assert caught.value.key == key
    assert str(caught.value).startswith(f"{key}:")


def test_a_valid_file_is_loaded(tmp_path):
    path = tmp_path / "scenario.yaml"
    path.write_text("device:\n  model: h2\nsimulation:\n  seed: 7\n", encoding="utf-8")

    scenario = load_scenario(path=path)

    assert scenario.device.model.name == "h2"
    assert scenario.simulation.seed == 7


@pytest.mark.parametrize(
    ("content", "name"), [("device: [", "broken.yaml"), (None, "missing.yaml")]
)
def test_unreadable_scenario_files_are_refused_with_the_path(tmp_path, content, name):
    path = tmp_path / name
    if content is not None:
        path.write_text(content, encoding="utf-8")

    with pytest.raises(ScenarioError) as caught:
        load_scenario(path=path)

    assert caught.value.key == str(path)


def test_an_empty_scenario_file_is_refused_for_the_missing_model(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ScenarioError) as caught:
        load_scenario(path=path)

    assert caught.value.key == "device.model"


def test_an_h2_scenario_accepts_five_battery_packs():
    scenario = parse_scenario(data={**H2, "battery": {"modules": 5}})

    assert scenario.battery.modules == 5


def test_an_h2_scenario_can_configure_a_parallel_system():
    scenario = parse_scenario(data={**H2, "parallel": {"inverters": 2}})

    assert scenario.parallel.inverters == 2


def test_an_h2_scenario_can_fit_a_meter_b():
    scenario = parse_scenario(data={**H2, "meters": {"meter_b": True}})

    assert scenario.meters.meter_b


def test_the_pack_faults_of_an_h2_are_limited_by_its_battery_count():
    scenario = parse_scenario(
        data={
            **H2,
            "battery": {"modules": 5},
            "faults": {"packs": [{"pack": 4, "fault": 9}]},
        }
    )

    assert scenario.faults.packs == (PackCodes(pack=4, fault=9),)


FULL_SCENARIO = {
    "device": {"model": "hs3", "rated_power_w": 10000, "serial_number": "ABC"},
    "server": {"port": 1502, "unit_id": 3, "panel_port": 9090},
    "simulation": {"seed": 9, "start": "2026-01-02T03:04:05", "speed": 60},
    "site": {
        "grid_connected": False,
        "pv_strings": [{"peak_power_w": 1000}, {"peak_power_w": 2000}],
        "load": {"base_w": 100, "peak_w": 200},
    },
    "battery": {"modules": 3, "module_capacity_ah": 50, "initial_soc_percent": 80},
    "meters": {"meter_a": False, "meter_b": True},
    "ev_charger": {
        "installed": True,
        "phases": 1,
        "max_power_w": 7000,
        "sessions": [{"plug_in": "08:15", "unplug": "17:00", "energy_needed_wh": 5000}],
    },
    "parallel": {"inverters": 2},
    "variation": {"cloud_depth": 0.9, "voltage_period_s": 30, "phase_imbalance": 0},
    "faults": {
        "inverter": [{"register": 0x4005, "bit": 23}],
        "battery": [{"register": 0x400B, "bit": 10}],
        "ev_charger": [{"register": 0x30AB, "bit": 2}],
        "packs": [{"pack": 1, "fault": 2, "warning": 3}],
    },
    "link": {
        "latency_ms": 800,
        "jitter_ms": 400,
        "no_answer_percent": 5,
        "busy_percent": 10.5,
        "device_failure_percent": 1,
        "dropped_connection_percent": 2,
        "late_duplicate_percent": 100,
        "refused_blocks": [
            {"start": 0x4000, "end": 0x40FF, "code": 0},
            {"start": 0x5000, "end": 0x5000, "code": 255},
        ],
        "unresponsive": True,
        "offline": True,
        "offline_seconds": 20,
        "offline_period_seconds": 60,
        "lockout_requests": 120,
        "lockout_window_seconds": 60,
        "lockout_whole_port": True,
    },
}


def test_the_link_section_states_every_link_setting():
    link = parse_scenario(data=FULL_SCENARIO).link

    assert link == LinkSettings(
        latency_ms=800,
        jitter_ms=400,
        no_answer_percent=5,
        busy_percent=10.5,
        device_failure_percent=1,
        dropped_connection_percent=2,
        late_duplicate_percent=100,
        refused_blocks=(
            RefusedBlock(start=0x4000, end=0x40FF, code=0),
            RefusedBlock(start=0x5000, end=0x5000, code=255),
        ),
        unresponsive=True,
        offline=True,
        offline_seconds=20,
        offline_period_seconds=60,
        lockout_requests=120,
        lockout_window_seconds=60,
        lockout_whole_port=True,
    )


@pytest.mark.parametrize("data", [HS3, H2, FULL_SCENARIO])
def test_an_exported_scenario_parses_back_to_the_same_scenario(data):
    scenario = parse_scenario(data=data)

    exported = dump_scenario(scenario=scenario)

    assert parse_scenario(data=yaml.safe_load(exported)) == scenario


def test_an_exported_scenario_writes_registers_in_hex_like_the_fault_tables():
    exported = dump_scenario(scenario=parse_scenario(data=FULL_SCENARIO))

    assert "register: 0x4005" in exported
    assert "register: 0x400B" in exported
    assert "register: 0x30AB" in exported
