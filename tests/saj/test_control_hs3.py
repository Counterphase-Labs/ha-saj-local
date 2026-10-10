from datetime import UTC, datetime
from itertools import count
from typing import TYPE_CHECKING

import pytest

from saj.budget import WRITE_ALLOWANCE_WINDOW
from saj.catalogue import Register, device_unread_registers
from saj.codec import Encoding, Value
from saj.control import Control
from saj.definitions import EMS_LIMIT_KEYS, EMS_TARGET_KEYS, EntityKind
from saj.device import Device
from saj.errors import UnknownSettingError
from saj.guard import EndpointGuard
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from saj.telemetry import plan_requests
from tests.saj.fakes import WritableClient

if TYPE_CHECKING:
    from collections.abc import Iterable

    from saj.models import Profile

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
    unread = device_unread_registers(profile=profile, device_type=device_type)
    unread_addresses = _unread_addresses(registers=unread)
    planned_addresses = {
        address
        for read_range in plan_requests(profile=profile, device_type=device_type)
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
    unread = device_unread_registers(profile=profile, device_type=device_type)
    link = WritableClient()
    control = _control(
        device=_device(profile=profile, device_type=device_type), link=link
    )

    for register in unread:
        await control.write(key=register.key, value=_valid_value(register=register))

    assert len(link.writes) == len(unread)
    assert link.reads == []


async def test_the_keep_alive_read_is_accepted_for_the_three_ems_targets():
    unread = device_unread_registers(profile=HS3, device_type=HS3_DEVICE_TYPE)
    targets = [register for register in unread if register.key in EMS_TARGET_KEYS]
    link = WritableClient()
    control = _hs3_control(link=link)

    for register in targets:
        await control.keep_alive_read_ems(key=register.key)

    assert len(targets) == len(EMS_TARGET_KEYS)
    assert link.reads == [(register.address, register.words) for register in targets]
    assert link.writes == []


async def test_the_keep_alive_read_is_refused_for_every_other_write_only_register():
    unread = device_unread_registers(profile=HS3, device_type=HS3_DEVICE_TYPE)
    others = [register for register in unread if register.key not in EMS_TARGET_KEYS]
    link = WritableClient()
    control = _hs3_control(link=link)

    for register in others:
        with pytest.raises(UnknownSettingError):
            await control.keep_alive_read_ems(key=register.key)

    assert others
    assert link.requests == []


def test_the_ems_limits_and_targets_are_exactly_the_write_only_ems_numbers():
    unread = device_unread_registers(profile=HS3, device_type=HS3_DEVICE_TYPE)
    write_only_numbers = {
        register.key
        for register in unread
        if register.key.startswith("ems_") and register.kind is EntityKind.NUMBER
    }

    assert EMS_LIMIT_KEYS.isdisjoint(EMS_TARGET_KEYS)
    assert write_only_numbers == EMS_LIMIT_KEYS | EMS_TARGET_KEYS


async def test_the_limits_read_is_three_requests_covering_exactly_the_five_limits():
    unread = device_unread_registers(profile=HS3, device_type=HS3_DEVICE_TYPE)
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
    unread = device_unread_registers(profile=HS3, device_type=HS3_DEVICE_TYPE)
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
