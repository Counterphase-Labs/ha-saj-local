import pytest

from saj_modbus_mock.models import MODELS
from saj_modbus_mock.profiles import common
from saj_modbus_mock.profiles.fields import ZERO
from saj_modbus_mock.registers import Access, Encoding
from saj_modbus_mock.simulation import control as ctl
from tests.modbus_mock.builders import by_address, by_name, make_scenario
from tests.modbus_mock.profiles.fakes import isolate


@pytest.fixture(autouse=True)
def stubbed_helpers(monkeypatch):
    isolate(monkeypatch, common)


def test_ems_enable_values_are_every_combination_of_the_four_enable_bits():
    values = common.ems_combinations()

    assert 0 in values
    assert 1 | 2 | 8 | 32 in values
    assert 4 not in values
    assert len(values) == 16


def test_information_identifies_the_device_and_its_rating():
    scenario = make_scenario(model="hs3", device={"serial_number": "SERIAL1"})

    fields = by_address(
        fields=common.information_fields(scenario=scenario, spec=MODELS["hs3"])
    )

    assert fields[0x8F00].initial == MODELS["hs3"].device_type
    assert fields[0x8F01].initial == scenario.device.rated_power_w
    assert fields[0x8F03].initial == "SERIAL1"
    assert fields[0x8F03].words == 10
    assert all(not field.writable for field in fields.values())
    assert max(fields) == 0x8F1C


def test_factory_commands_are_write_only_and_restrict_their_values():
    fields = by_name(fields=common.factory_command_fields())

    assert all(field.access is Access.WRITE_ONLY for field in fields.values())
    assert fields["cmd_clear_faults"].options == {1, 2}
    assert fields["cmd_restart"].options == {1}
    assert fields["cmd_set_clock"].words == 4


@pytest.mark.parametrize("phases", [3, 1])
def test_phase_sources_are_requested_for_the_models_phase_count(phases):
    fields = by_address(
        fields=common.realtime_energy_fields(
            scenario=make_scenario(model="hs3"), phases=phases, extended=True
        )
    )

    assert fields[0x4031].source == f"phase:grid:0:v:{phases}"
    assert fields[0x4038].source == f"phase:grid:1:v:{phases}"
    assert fields[0x403F].source == f"phase:grid:2:v:{phases}"


def test_every_realtime_register_has_a_unique_address_and_name():
    fields = common.realtime_energy_fields(
        scenario=make_scenario(model="hs3"), phases=3, extended=True
    )

    assert len({field.address for field in fields}) == len(fields)
    assert len({field.name for field in fields}) == len(fields)


def test_extended_realtime_adds_the_vector_sum_counters():
    scenario = make_scenario(model="hs3")
    plain = by_address(
        fields=common.realtime_energy_fields(
            scenario=scenario, phases=3, extended=False
        )
    )
    extended = by_address(
        fields=common.realtime_energy_fields(scenario=scenario, phases=3, extended=True)
    )

    assert 0x416F not in plain
    assert extended[0x416F].source == "counter:sum_sell:True:False"
    assert extended[0x4167].source == "counter:sum_feed_in:True:False"


def test_realtime_mirrors_the_scenario_rating_and_follows_the_settings():
    scenario = make_scenario(model="hs3")

    fields = by_address(
        fields=common.realtime_energy_fields(scenario=scenario, phases=3, extended=True)
    )

    assert fields[0x4023].initial == scenario.device.rated_power_w
    assert fields[0x4022].source == "running_mode"
    assert fields[0x4022].encoding is Encoding.I16
    assert fields[0x4029].source == "mirror_charge_ceiling"


def test_all_four_pv_strings_have_voltage_current_and_power():
    fields = by_name(
        fields=common.realtime_energy_fields(
            scenario=make_scenario(model="hs3"), phases=3, extended=True
        )
    )

    for number in range(1, 5):
        assert fields[f"pv{number}_power"].source == f"pv{number}_w"
        assert fields[f"pv{number}_voltage"].source == f"pv{number}_v"
        assert fields[f"pv{number}_current"].source == f"pv{number}_a"


def test_schedule_slots_use_the_keys_the_controller_reads():
    names = {field.name for field in common.schedule_fields()}

    for kind in ("charge", "discharge"):
        for index in range(1, 8):
            for part in ("start", "end", "days_power"):
                assert ctl.slot_key(kind=kind, index=index, part=part) in names
    assert {ctl.CHARGE_ENABLE_MASK, ctl.DISCHARGE_ENABLE_MASK} <= names


def test_schedule_registers_are_consecutive_writable_words():
    fields = common.schedule_fields()

    assert all(field.writable and field.words == 1 for field in fields)
    assert sorted(field.address for field in fields) == list(
        range(0x3604, 0x3604 + 2 + 42)
    )


def test_every_setting_the_controller_reads_is_a_writable_field():
    names = by_name(
        fields=common.settings_fields(
            scenario=make_scenario(model="hs3"), modes=frozenset({0, 1}), extended=False
        )
    )

    for key in (
        ctl.APP_MODE,
        ctl.BACKUP_RESERVE,
        ctl.BACKUP_CHARGE_POWER,
        ctl.DISCHARGE_FLOOR_ON_GRID,
        ctl.DISCHARGE_FLOOR_OFF_GRID,
        ctl.CHARGE_CEILING,
        ctl.TOU_OUTSIDE_MODE,
        ctl.ANTI_REFLUX_MODE,
        ctl.ANTI_REFLUX_POWER_LIMIT,
    ):
        assert names[key].writable


def test_the_application_modes_offered_are_those_of_the_model():
    fields = by_name(
        fields=common.settings_fields(
            scenario=make_scenario(model="hs3"), modes=frozenset({0, 6}), extended=False
        )
    )

    assert fields[ctl.APP_MODE].options == {0, 6}


@pytest.mark.parametrize(("meter_a", "mode"), [(True, 3), (False, 0)])
def test_the_meter_mode_follows_the_installed_meter(meter_a, mode):
    scenario = make_scenario(model="hs3", meters={"meter_a": meter_a})

    fields = by_name(
        fields=common.settings_fields(
            scenario=scenario, modes=frozenset({0}), extended=False
        )
    )

    assert fields["meter_enable"].initial == mode


def test_extended_settings_add_the_protocol_header_and_slave_port():
    scenario = make_scenario(model="hs3")
    plain = by_address(
        fields=common.settings_fields(
            scenario=scenario, modes=frozenset({0}), extended=False
        )
    )
    extended = by_address(
        fields=common.settings_fields(
            scenario=scenario, modes=frozenset({0}), extended=True
        )
    )

    assert 0x3680 not in plain
    assert {0x3602, 0x3603, 0x3680, 0x3681} <= set(extended)
    assert not extended[0x3603].writable


def test_percent_settings_carry_one_decimal_and_a_ceiling_above_full_power():
    fields = by_address(
        fields=common.settings_fields(
            scenario=make_scenario(model="hs3"), modes=frozenset({0}), extended=False
        )
    )

    assert fields[0x3639].scale == 0.1
    assert fields[0x3639].maximum == 1100
    assert fields[0x3639].initial == 4.2


@pytest.mark.parametrize("phases", [3, 1])
def test_meter_values_exist_only_for_the_phases_of_the_model(phases):
    fields = by_address(fields=common.meter_fields(phases=phases, extended=False))

    assert fields[0xA03D].source == "meter_a_r_v"
    assert fields[0xA043].source == ("meter_a_s_v" if phases == 3 else ZERO)
    assert fields[0xA054].source == "meter_b_r_v"
    assert fields[0xA05A].source == ("meter_b_s_v" if phases == 3 else ZERO)
    assert fields[0xA03C].source == "meter_a_status"
    assert fields[0xA053].source == "meter_b_status"


def test_a_single_phase_meter_b_serves_its_status_and_first_phase_readings():
    fields = by_address(fields=common.meter_fields(phases=1, extended=False))

    first_phase = [fields[address] for address in range(0xA054, 0xA05A)]
    assert all(field.source.startswith("meter_b_r_") for field in first_phase)
    assert fields[0xA053].source == "meter_b_status"
    assert not any(field.address > 0xA065 for field in fields.values())


def test_extended_meters_add_the_high_word_and_reactive_registers():
    plain = by_address(fields=common.meter_fields(phases=3, extended=False))
    extended = by_address(fields=common.meter_fields(phases=3, extended=True))

    assert 0xA066 not in plain
    assert extended[0xA066].words == 1
    assert extended[0xA06C].words == 2
    assert extended[0xA072].words == 2


def test_an_unpopulated_battery_block_reads_zero_everywhere():
    fields = common.battery_fields(populated=False)

    assert {field.source for field in fields if field.source} == {ZERO}


def test_a_populated_battery_block_reads_the_module_quantities():
    fields = by_name(fields=common.battery_fields(populated=True))

    assert fields["battery_count"].source == "battery_modules"
    assert fields["battery2_soc"].source == "module2_soc_percent"
    assert (
        fields["battery1_discharged_high"].address + 1
        == fields["battery1_discharged_low"].address
    )
    assert fields["battery3_voltage"].address == 0xA00C + 6 * 2 + 2


@pytest.mark.parametrize(("phases", "present"), [(3, True), (1, False)])
def test_phase_share_counters_are_requested_only_for_phases_the_model_has(
    phases, present
):
    fields = by_address(
        fields=common.realtime_energy_fields(
            scenario=make_scenario(model="hs3"), phases=phases, extended=False
        )
    )

    assert fields[0x4147].source == f"counter:sell_phase2:{present}:False"
    assert fields[0x415F].source == f"counter:feed_in_phase3:{present}:False"


@pytest.mark.parametrize("model", ["hs3", "h2"])
@pytest.mark.parametrize("modules", [0, 1, 3])
def test_both_battery_protocol_registers_read_not_in_use_without_battery_modules(
    model, modules
):
    spec = MODELS[model]
    scenario = make_scenario(model=model, battery={"modules": modules})
    realtime = by_address(
        fields=common.realtime_energy_fields(
            scenario=scenario, phases=spec.phases, extended=False
        )
    )
    settings = by_name(
        fields=common.settings_fields(
            scenario=scenario, modes=frozenset({0}), extended=False
        )
    )

    expected = (
        (spec.battery_protocol_active, spec.battery_protocol_setting)
        if modules
        else (0, 0)
    )
    assert (realtime[0x4028].initial, settings["battery_protocol"].initial) == expected
    assert settings["battery_protocol"].options == {0, spec.battery_protocol_setting}
