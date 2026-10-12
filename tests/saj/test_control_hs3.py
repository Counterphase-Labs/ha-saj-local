from datetime import UTC, datetime
from itertools import count
from typing import TYPE_CHECKING

import pytest

from saj.budget import WRITE_ALLOWANCE_WINDOW
from saj.catalogue import (
    Fit,
    Register,
    device_keys,
    device_registers,
    device_unread_registers,
)
from saj.codec import Encoding, Value
from saj.control import Control
from saj.definitions import EntityKind
from saj.device import Device
from saj.errors import InvalidValueError, UnknownSettingError
from saj.guard import EndpointGuard
from saj.models import ALL_EQUIPMENT, Equipment
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from saj.telemetry import decode_values, plan_requests
from tests.saj.fakes import WritableClient

if TYPE_CHECKING:
    from collections.abc import Iterable

    from saj.models import Profile

EMS_TARGET_KEYS = frozenset(method.target_key for method in HS3.power_control.values())
EMS_LIMIT_KEYS = frozenset(
    key for method in HS3.power_control.values() for key in method.limit_keys
)
HS3_DEVICE_TYPE = 0x1610
H2_DEVICE_TYPE = 0x005A
BACKUP_RESERVE_ADDRESS = 0x3651
SLOT_ADDRESS = 0x3608
SLOT_POWER_MASK = 0x00FF
SLOT_DAYS_MASK = 0x7F00
SLOT_DAYS_SHIFT = 8
UNRELATED_BIT = 0x8000
SEEDED_POWER = 30
SEEDED_DAYS = 0b0101010
WRITTEN_POWER = 60
WRITTEN_DAYS = 0b0010101
BACKUP_RESERVE = 50
CLOCK_VALUE = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)


def _device(*, profile: Profile, device_type: int) -> Device:
    return Device(
        serial="TEST",
        device_type=device_type,
        rated_power=10000,
        profile=profile,
        detected=True,
    )


def _control(*, device: Device, link: WritableClient) -> Control:
    ticks = count(step=WRITE_ALLOWANCE_WINDOW)
    return Control(
        link=link,
        device=device,
        guard=EndpointGuard(),
        enabled=True,
        clock=lambda: float(next(ticks)),
    )


def _hs3_control(*, link: WritableClient) -> Control:
    return _control(device=_device(profile=HS3, device_type=HS3_DEVICE_TYPE), link=link)


def _slot_word(*, power: int, days: int) -> int:
    return UNRELATED_BIT | (days << SLOT_DAYS_SHIFT) | power


def _valid_value(*, register: Register) -> Value:
    if register.encoding is Encoding.CLOCK:
        return CLOCK_VALUE
    return 0


async def test_writing_the_backup_reserve_is_one_write_and_one_read_back():
    link = WritableClient({BACKUP_RESERVE_ADDRESS: 20})

    result = await _hs3_control(link=link).write(
        key="backup_reserve_soc", value=BACKUP_RESERVE
    )

    assert [request[0] for request in link.requests] == ["single", "read"]
    assert link.requests[0][1:] == (BACKUP_RESERVE_ADDRESS, (BACKUP_RESERVE,))
    assert result.values["backup_reserve_soc"] == link.memory[BACKUP_RESERVE_ADDRESS]
    assert result.values["backup_reserve_soc"] == BACKUP_RESERVE


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        (
            "charge_slot_1_power",
            WRITTEN_POWER,
            _slot_word(power=WRITTEN_POWER, days=SEEDED_DAYS),
        ),
        (
            "charge_slot_1_days",
            WRITTEN_DAYS,
            _slot_word(power=SEEDED_POWER, days=WRITTEN_DAYS),
        ),
    ],
)
async def test_writing_one_packed_field_leaves_the_other_bits_as_they_were(
    key: str, value: int, expected: int
):
    link = WritableClient(
        {SLOT_ADDRESS: _slot_word(power=SEEDED_POWER, days=SEEDED_DAYS)}
    )

    await _hs3_control(link=link).write(key=key, value=value)

    written = [request for request in link.writes if request[1] == SLOT_ADDRESS]
    assert written == [("single", SLOT_ADDRESS, (expected,))]


def _unread_addresses(*, registers: Iterable[Register]) -> set[int]:
    return {
        address
        for register in registers
        for address in range(register.address, register.address + register.words)
    }


@pytest.mark.parametrize(
    ("profile", "device_type", "expected_key"),
    [
        (HS3, HS3_DEVICE_TYPE, "ems_inverter_power_target"),
        (H2, H2_DEVICE_TYPE, "restart_inverter"),
    ],
)
def test_polling_plans_never_cover_a_write_only_register(
    profile: Profile, device_type: int, expected_key: str
):
    unread = device_unread_registers(
        fit=Fit(profile=profile, device_type=device_type, equipment=ALL_EQUIPMENT)
    )
    unread_addresses = _unread_addresses(registers=unread)
    planned_addresses = {
        address
        for read_range in plan_requests(
            fit=Fit(profile=profile, device_type=device_type, equipment=ALL_EQUIPMENT)
        )
        for address in range(read_range.address, read_range.address + read_range.count)
    }

    assert next(r.address for r in unread if r.key == expected_key) in unread_addresses
    assert planned_addresses.isdisjoint(unread_addresses)


@pytest.mark.parametrize(
    ("profile", "device_type"),
    [(HS3, HS3_DEVICE_TYPE), (H2, H2_DEVICE_TYPE)],
)
async def test_writing_any_write_only_register_causes_no_read(
    profile: Profile, device_type: int
):
    unread = device_unread_registers(
        fit=Fit(profile=profile, device_type=device_type, equipment=ALL_EQUIPMENT)
    )
    link = WritableClient()
    control = _control(
        device=_device(profile=profile, device_type=device_type), link=link
    )

    for register in unread:
        await control.write(key=register.key, value=_valid_value(register=register))

    assert len(link.writes) == len(unread)
    assert link.reads == []


async def test_the_keep_alive_read_is_accepted_for_the_three_ems_targets():
    unread = device_unread_registers(
        fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
    )
    targets = [register for register in unread if register.key in EMS_TARGET_KEYS]
    link = WritableClient()
    control = _hs3_control(link=link)

    for register in targets:
        await control.keep_alive_read_ems(key=register.key)

    assert len(targets) == len(EMS_TARGET_KEYS)
    assert link.reads == [(register.address, register.words) for register in targets]
    assert link.writes == []


async def test_the_keep_alive_read_is_refused_for_every_other_write_only_register():
    unread = device_unread_registers(
        fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
    )
    others = [register for register in unread if register.key not in EMS_TARGET_KEYS]
    link = WritableClient()
    control = _hs3_control(link=link)

    for register in others:
        with pytest.raises(UnknownSettingError):
            await control.keep_alive_read_ems(key=register.key)

    assert others
    assert link.requests == []


def test_the_ems_limits_and_targets_are_exactly_the_write_only_ems_numbers():
    unread = device_unread_registers(
        fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
    )
    write_only_numbers = {
        register.key
        for register in unread
        if register.key.startswith("ems_") and register.kind is EntityKind.NUMBER
    }

    assert EMS_LIMIT_KEYS.isdisjoint(EMS_TARGET_KEYS)
    assert write_only_numbers == EMS_LIMIT_KEYS | EMS_TARGET_KEYS


async def test_the_limits_read_is_three_requests_covering_exactly_the_five_limits():
    unread = device_unread_registers(
        fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
    )
    limits = [register for register in unread if register.key in EMS_LIMIT_KEYS]
    link = WritableClient()

    values = await _hs3_control(link=link).read_ems_limits()

    assert len(limits) == len(EMS_LIMIT_KEYS)
    assert len(link.reads) == 3
    assert link.writes == []
    assert _requested_addresses(reads=link.reads) == _unread_addresses(registers=limits)
    assert set(values) == EMS_LIMIT_KEYS


async def test_the_limits_read_on_a_device_without_ems_rows_reads_nothing():
    link = WritableClient()
    control = _control(
        device=_device(profile=H2, device_type=H2_DEVICE_TYPE), link=link
    )

    assert await control.read_ems_limits() == {}
    assert link.requests == []


async def test_no_read_covers_a_command_register_that_holds_no_readable_setting():
    unread = device_unread_registers(
        fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
    )
    readable_by_ems = EMS_LIMIT_KEYS | EMS_TARGET_KEYS
    commands = _unread_addresses(
        registers=[r for r in unread if r.kind is EntityKind.BUTTON]
    ) - _unread_addresses(registers=[r for r in unread if r.key in readable_by_ems])
    link = WritableClient()
    control = _hs3_control(link=link)

    for key in EMS_TARGET_KEYS:
        await control.keep_alive_read_ems(key=key)
    await control.read_ems_limits()

    assert commands
    assert _requested_addresses(reads=link.reads).isdisjoint(commands)


def _requested_addresses(*, reads: Iterable[tuple[int, int]]) -> set[int]:
    return {
        address for start, count in reads for address in range(start, start + count)
    }


UNFITTED_OPTIONAL_RANGES = (
    (0x3024, 0x30BB),
    (0x4204, 0x427C),
    (0x4B05, 0x4B47),
)


def _planned_with_everything_enabled(*, fitted: frozenset[Equipment]):
    fit = Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=fitted)
    return plan_requests(fit=fit, enabled=device_keys(fit=fit))


def _keys_of(equipment: set[Equipment]) -> set[str]:
    return {
        register.key
        for register in device_registers(
            fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
        )
        if register.equipment in equipment
    }


def test_no_request_carries_a_row_of_equipment_that_is_not_fitted():
    unfitted = _keys_of({Equipment.METER_B, Equipment.EV_CHARGER, Equipment.PARALLEL})
    planned = _planned_with_everything_enabled(fitted=frozenset({Equipment.BATTERY}))

    assert unfitted
    assert {key for read_range in planned for key in read_range.keys}.isdisjoint(
        unfitted
    )


def test_no_request_overlaps_the_registers_of_unfitted_optional_equipment():
    planned = _planned_with_everything_enabled(fitted=frozenset({Equipment.BATTERY}))

    for read_range in planned:
        last = read_range.address + read_range.count - 1
        assert all(
            last < first or read_range.address > end
            for first, end in UNFITTED_OPTIONAL_RANGES
        )


def test_no_battery_row_is_planned_when_nothing_is_fitted():
    battery_keys = {
        register.key
        for register in device_registers(
            fit=Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
        )
        if register.equipment is Equipment.BATTERY
    }

    planned = {
        key
        for read_range in _planned_with_everything_enabled(fitted=frozenset())
        for key in read_range.keys
    }

    assert battery_keys
    assert planned.isdisjoint(battery_keys)


EV_EMS_COMMAND_ADDRESS = 0x4B46
EV_EMS_CURRENT_ADDRESS = 0x4B47
SINGLE_PHASE_BITS = 0b010
THREE_PHASE_BITS = 0b000
CHARGING_OFF_BIT = 0b001


@pytest.mark.parametrize(
    ("before", "value", "after"),
    [
        (CHARGING_OFF_BIT | SINGLE_PHASE_BITS, 1, SINGLE_PHASE_BITS),
        (SINGLE_PHASE_BITS, 0, CHARGING_OFF_BIT | SINGLE_PHASE_BITS),
        (CHARGING_OFF_BIT | THREE_PHASE_BITS, 1, THREE_PHASE_BITS),
        (UNRELATED_BIT | CHARGING_OFF_BIT, 1, UNRELATED_BIT),
    ],
)
async def test_switching_ev_charging_on_writes_a_zero_bit_and_keeps_the_phase_bits(
    before: int, value: int, after: int
):
    link = WritableClient({EV_EMS_COMMAND_ADDRESS: before})

    result = await _hs3_control(link=link).write(key="ev_ems_charging", value=value)

    assert link.memory[EV_EMS_COMMAND_ADDRESS] == after
    assert result.values["ev_ems_charging"] == value


async def test_ev_charging_already_in_the_requested_state_is_not_written():
    link = WritableClient({EV_EMS_COMMAND_ADDRESS: SINGLE_PHASE_BITS})

    result = await _hs3_control(link=link).write(key="ev_ems_charging", value=1)

    assert link.writes == []
    assert result.written is False
    assert result.values["ev_ems_charging"] == 1


@pytest.mark.parametrize(
    ("before", "value", "after"),
    [
        (CHARGING_OFF_BIT, 1, CHARGING_OFF_BIT | SINGLE_PHASE_BITS),
        (CHARGING_OFF_BIT | SINGLE_PHASE_BITS, 0, CHARGING_OFF_BIT),
    ],
)
async def test_the_phase_mode_writes_only_its_two_bits(
    before: int, value: int, after: int
):
    link = WritableClient({EV_EMS_COMMAND_ADDRESS: before})

    await _hs3_control(link=link).write(key="ev_ems_phase_mode", value=value)

    assert link.memory[EV_EMS_COMMAND_ADDRESS] == after


@pytest.mark.parametrize("code", [2, 3, 4, -1])
async def test_the_phase_mode_can_never_write_a_reserved_or_repeated_code(code: int):
    link = WritableClient({EV_EMS_COMMAND_ADDRESS: CHARGING_OFF_BIT})

    with pytest.raises(InvalidValueError):
        await _hs3_control(link=link).write(key="ev_ems_phase_mode", value=code)

    assert link.requests == []


@pytest.mark.parametrize(("amps", "raw"), [(6, 60), (16.5, 165), (32, 320)])
async def test_the_ems_charge_current_is_written_in_tenths_of_an_ampere(
    amps: float, raw: int
):
    link = WritableClient({EV_EMS_CURRENT_ADDRESS: 60})

    result = await _hs3_control(link=link).write(
        key="ev_ems_charge_current", value=amps
    )

    assert link.writes == [("single", EV_EMS_CURRENT_ADDRESS, (raw,))]
    assert result.values["ev_ems_charge_current"] == amps


@pytest.mark.parametrize("amps", [5.9, 32.1, 0])
async def test_an_ems_charge_current_outside_six_to_thirty_two_amperes_is_refused(
    amps: float,
):
    link = WritableClient({EV_EMS_CURRENT_ADDRESS: 60})

    with pytest.raises(InvalidValueError):
        await _hs3_control(link=link).write(key="ev_ems_charge_current", value=amps)

    assert link.requests == []


@pytest.mark.parametrize("code", [2, 3])
def test_a_reserved_phase_mode_code_reads_as_a_code_the_row_does_not_offer(code: int):
    fit = Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
    registers = [
        register
        for register in device_registers(fit=fit)
        if register.key == "ev_ems_phase_mode"
    ]

    values = decode_values(
        registers=registers,
        raw={"ev_ems_phase_mode": [code << 1 | CHARGING_OFF_BIT]},
    )

    assert values["ev_ems_phase_mode"] == code
    assert code not in registers[0].options


@pytest.mark.parametrize("fitted", [frozenset({Equipment.BATTERY}), frozenset()])
async def test_the_ev_ems_settings_cannot_be_written_without_a_charger(
    fitted: frozenset[Equipment],
):
    device = Device(
        serial="TEST",
        device_type=HS3_DEVICE_TYPE,
        rated_power=10000,
        profile=HS3,
        detected=True,
        equipment=fitted,
    )

    for key in ("ev_ems_charging", "ev_ems_phase_mode", "ev_ems_charge_current"):
        with pytest.raises(UnknownSettingError):
            await _control(device=device, link=WritableClient()).write(key=key, value=1)
