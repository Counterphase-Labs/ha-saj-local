from itertools import count

import pytest

from saj.budget import WRITE_ALLOWANCE_WINDOW
from saj.catalogue import CATALOGUES, Fit, device_keys, device_registers
from saj.codec import decode, option_name
from saj.control import Control, ControlEnvironment
from saj.definitions import COMMISSIONING_KEYS, PROTECTED_KEYS
from saj.device import Device
from saj.errors import InvalidValueError, ProtectedSettingError
from saj.guard import EndpointGuard
from saj.models import ALL_EQUIPMENT, Equipment
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from tests.saj.fakes import WritableClient

H2_DEVICE_TYPE = 0x005A
HS3_DEVICE_TYPE = 0x1610
PACK_COUNT = 5
IDENTITY_NAMES = (
    "bms_type",
    "bms_serial_number",
    "bms_software_version",
    "bms_hardware_version",
    "type",
    "serial_number",
)
PRIVATE_IDENTITY_NAMES = ("bms_serial_number", "serial_number")
ALLOWED_NEW_WRITES = {"buzzer", "battery_forced_charge_power_limit"}
FULL_POWER = 100
OVER_POWER = 101
UNDER_POWER = 9
BUZZER_ENABLED = 0
BUZZER_FORBIDDEN = 1


def _fit(*, pack_limit: int | None = None) -> Fit:
    return Fit(
        profile=H2,
        device_type=H2_DEVICE_TYPE,
        equipment=ALL_EQUIPMENT,
        pack_limit=pack_limit,
    )


def _registers() -> dict:
    return {register.key: register for register in device_registers(fit=_fit())}


def _control(*, link: WritableClient) -> Control:
    ticks = count(step=WRITE_ALLOWANCE_WINDOW)
    return Control(
        link=link,
        device=Device(
            serial="TEST",
            device_type=H2_DEVICE_TYPE,
            rated_power=10000,
            profile=H2,
            detected=True,
        ),
        guard=EndpointGuard(),
        enabled=True,
        environment=ControlEnvironment(
            clock=lambda: float(next(ticks)), label="control"
        ),
    )


def _only_on_the_h2() -> set[str]:
    return {
        register.key
        for register in CATALOGUES["h2"].registers
        if register.key not in {other.key for other in CATALOGUES["hs3"].registers}
    }


PROTECTED_ON_THE_H2 = sorted(
    register.key
    for register in CATALOGUES["h2"].registers
    if register.key in COMMISSIONING_KEYS
    and register.key not in {other.key for other in CATALOGUES["hs3"].registers}
)


def test_the_new_writable_h2_settings_are_protected_apart_from_the_ones_allowed():
    writable = {
        register.key
        for register in CATALOGUES["h2"].registers
        if register.writable and register.key in _only_on_the_h2()
    }

    assert writable - PROTECTED_KEYS == ALLOWED_NEW_WRITES
    assert PROTECTED_ON_THE_H2


@pytest.mark.parametrize("key", PROTECTED_ON_THE_H2)
async def test_a_protected_h2_setting_is_refused_and_the_inverter_is_not_touched(
    key: str,
):
    link = WritableClient()

    with pytest.raises(ProtectedSettingError):
        await _control(link=link).write(key=key, value=0)

    assert link.requests == []


@pytest.mark.parametrize(
    ("held", "shown"), [(BUZZER_ENABLED, 1), (BUZZER_FORBIDDEN, 0)]
)
def test_the_buzzer_is_on_when_the_register_forbids_nothing(held: int, shown: int):
    register = _registers()["buzzer"]

    assert decode(words=(held,), encoding_format=register.format) == shown


async def test_switching_the_buzzer_on_writes_the_enabled_word_and_reads_it_back():
    register = _registers()["buzzer"]
    link = WritableClient({register.address: BUZZER_FORBIDDEN})

    result = await _control(link=link).write(key="buzzer", value=1)

    assert link.writes == [("single", register.address, (BUZZER_ENABLED,))]
    assert result.values["buzzer"] == 1


async def test_the_battery_forced_charge_power_is_written_and_shown_as_read_back():
    register = _registers()["battery_forced_charge_power_limit"]
    link = WritableClient({register.address: 0})

    result = await _control(link=link).write(
        key="battery_forced_charge_power_limit", value=FULL_POWER
    )

    assert len(link.writes) == 1
    assert result.values["battery_forced_charge_power_limit"] == FULL_POWER


@pytest.mark.parametrize("value", [UNDER_POWER, OVER_POWER])
async def test_the_battery_forced_charge_power_stays_inside_its_documented_range(
    value: int,
):
    link = WritableClient()

    with pytest.raises(InvalidValueError):
        await _control(link=link).write(
            key="battery_forced_charge_power_limit", value=value
        )

    assert link.requests == []


def test_peak_shaving_is_an_application_mode_of_the_h2_only():
    def modes(profile_key: str) -> dict:
        catalogue = CATALOGUES[profile_key]
        register = next(r for r in catalogue.registers if r.key == "application_mode")
        return register.options

    h2 = modes("h2")
    code = next(code for code, name in h2.items() if name == "peak_shaving")

    assert option_name(code=code, options=h2) == "peak_shaving"
    assert "peak_shaving" not in modes("hs3").values()


def test_the_application_mode_in_effect_reads_the_modes_the_h2_can_select():
    rows = _registers()

    assert rows["application_mode_active"].options == rows["application_mode"].options


@pytest.mark.parametrize("name", IDENTITY_NAMES)
def test_every_pack_has_each_identity_row(name: str):
    keys = device_keys(fit=_fit())

    assert {f"battery_pack{pack}_{name}" for pack in range(1, PACK_COUNT + 1)} <= keys


@pytest.mark.parametrize("pack_limit", [1, 2, 3])
def test_the_identity_rows_follow_the_pack_count_the_battery_reports(pack_limit: int):
    keys = device_keys(fit=_fit(pack_limit=pack_limit))

    for pack in range(1, PACK_COUNT + 1):
        assert (f"battery_pack{pack}_bms_type" in keys) is (pack <= pack_limit)


def test_the_identity_rows_exist_only_with_a_battery():
    fit = Fit(
        profile=H2,
        device_type=H2_DEVICE_TYPE,
        equipment=ALL_EQUIPMENT - {Equipment.BATTERY},
    )

    assert not {
        key
        for key in device_keys(fit=fit)
        if key.startswith("battery_pack") and key.endswith(IDENTITY_NAMES)
    }


@pytest.mark.parametrize("name", PRIVATE_IDENTITY_NAMES)
def test_the_serial_rows_of_every_pack_are_private(name: str):
    rows = _registers()

    assert all(rows[f"battery_pack{pack}_{name}"].private for pack in range(1, 6))


def test_the_battery_voltage_and_current_are_enabled_by_default_on_the_h2():
    rows = _registers()

    assert rows["battery_voltage"].core
    assert rows["battery_current"].core


def test_the_identity_rows_are_created_disabled():
    rows = _registers()

    assert not any(
        row.core
        for key, row in rows.items()
        if key.startswith("battery_pack") and key.endswith(IDENTITY_NAMES)
    )


def test_the_hs3_is_not_given_the_h2_only_rows():
    hs3 = {
        register.key
        for register in device_registers(
            fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
        )
    }

    assert not {"buzzer", "battery_pack1_bms_type", "grid_type"} & hs3
