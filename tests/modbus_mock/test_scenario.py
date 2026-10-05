from datetime import UTC, datetime, time

import pytest

from saj_modbus_mock.scenario import ScenarioError, load_scenario, parse_scenario

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
                "response_delay_ms": 5,
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
                "module_capacity_ah": 50,
                "initial_soc_percent": 80,
            },
            "meters": {"meter_a": False, "meter_b": True},
            "ev_charger": {
                "installed": True,
                "phases": 1,
                "max_power_w": 7000,
                "sessions": [
                    {"plug_in": "08:15", "unplug": "17:00", "energy_needed_wh": 5000}
                ],
            },
            "parallel": {"inverters": 2},
            "faults": {"inverter_fault_bits": [3, 1, 3]},
        },
    )

    assert scenario.simulation.start == datetime(2026, 1, 2, 1, 4, 5, tzinfo=UTC)
    assert scenario.site.pv_strings == (1000,)
    assert not scenario.site.grid_connected
    assert scenario.ev_charger.sessions[0].plug_in == time(8, 15)
    assert scenario.faults.inverter_fault_bits == (1, 3)
    assert scenario.server.response_delay_ms == 5


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
        ({**H2, "battery": {"modules": 5}}, "battery.modules"),
        (
            {**HS3, "battery": {"initial_soc_percent": 101}},
            "battery.initial_soc_percent",
        ),
        ({**H2, "meters": {"meter_b": True}}, "meters.meter_b"),
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
        ({**H2, "parallel": {"inverters": 2}}, "parallel.inverters"),
        (
            {**HS3, "faults": {"inverter_fault_bits": [32]}},
            "faults.inverter_fault_bits[0]",
        ),
        (
            {**HS3, "faults": {"inverter_fault_bits": ["a"]}},
            "faults.inverter_fault_bits[0]",
        ),
        (
            {**HS3, "faults": {"inverter_fault_bits": [True]}},
            "faults.inverter_fault_bits[0]",
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
