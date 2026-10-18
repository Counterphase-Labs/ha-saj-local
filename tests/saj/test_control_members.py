import pytest

from saj.catalogue import Fit, device_registers
from saj.definitions import (
    BATTERY_PACK,
    CHARGE_SLOTS,
    CHARGE_SLOTS_ENABLED,
    DISCHARGE_SLOTS,
    DISCHARGE_SLOTS_ENABLED,
    EV_SLOTS,
)
from saj.models import ALL_EQUIPMENT
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3

SLOT_FAMILIES = (
    CHARGE_SLOTS,
    CHARGE_SLOTS_ENABLED,
    DISCHARGE_SLOTS,
    DISCHARGE_SLOTS_ENABLED,
    EV_SLOTS,
)


def _registers(*, profile):
    return device_registers(
        fit=Fit(
            profile=profile,
            device_type=next(iter(profile.device_types)),
            equipment=ALL_EQUIPMENT,
        )
    )


def _keys_of(*, families):
    return {
        definition.key for family in families for definition in family.definitions()
    }


@pytest.mark.parametrize("profile", [HS3, H2], ids=["hs3", "h2"])
def test_every_schedule_slot_register_the_model_has_is_a_control_member(profile):
    registers = _registers(profile=profile)
    slot_keys = _keys_of(families=SLOT_FAMILIES)

    slot_registers = [register for register in registers if register.key in slot_keys]

    assert slot_registers
    assert all(register.control for register in slot_registers)


@pytest.mark.parametrize("profile", [HS3, H2], ids=["hs3", "h2"])
def test_a_control_member_can_be_changed(profile):
    members = [register for register in _registers(profile=profile) if register.control]

    assert members
    assert all(register.writable for register in members)


@pytest.mark.parametrize("profile", [HS3, H2], ids=["hs3", "h2"])
def test_a_register_that_cannot_be_changed_is_not_a_control_member(profile):
    read_only = [
        register for register in _registers(profile=profile) if not register.writable
    ]

    assert read_only
    assert not any(register.control for register in read_only)


@pytest.mark.parametrize("profile", [HS3, H2], ids=["hs3", "h2"])
def test_a_reading_outside_the_control_set_is_not_a_control_member(profile):
    reading_keys = _keys_of(families=(BATTERY_PACK,))

    readings = [
        register
        for register in _registers(profile=profile)
        if register.key in reading_keys
    ]

    assert readings
    assert not any(register.control for register in readings)
