import pytest

from saj.catalogue import catalogue_of
from saj.codec import encode
from saj.device import Device
from saj.models import ALL_EQUIPMENT, PowerFunction, ems_rows
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from saj.power_control import power_controls, power_functions

BATTERY = PowerFunction.BATTERY
HS3_DEVICE = Device(
    serial="S",
    device_type=0x1610,
    rated_power=12000,
    profile=HS3,
    detected=True,
    equipment=ALL_EQUIPMENT,
)
H2_DEVICE = Device(
    serial="S",
    device_type=0x005A,
    rated_power=8000,
    profile=H2,
    detected=True,
    equipment=ALL_EQUIPMENT,
)
SELF_USE = 0


def _sent(device: Device, writes) -> list[tuple[int, int | None, tuple[int, ...]]]:
    registers = {
        register.key: register
        for register in catalogue_of(profile=device.profile).registers
    }
    sent = []
    for write in writes:
        register = registers[write.key]
        field = register.field
        sent.append(
            (
                register.address,
                None if field is None else field.first,
                encode(value=write.value, encoding_format=register.format),
            )
        )
    return sent


def test_an_hs3_has_the_three_functions_and_an_h2_has_the_battery():
    assert power_functions(fit=HS3_DEVICE.fit) == tuple(PowerFunction)
    assert power_functions(fit=H2_DEVICE.fit) == (BATTERY,)


def test_the_hs3_battery_target_goes_to_its_target_row_then_its_enable_bit_is_set():
    control = power_controls(device=HS3_DEVICE)[BATTERY]

    start = control.start(watts=-600, prior=None)

    assert _sent(HS3_DEVICE, start.writes) == [
        (0x8405, None, (0xFE0C,)),
        (0x8400, 1, (0b10,)),
    ]


def test_the_hs3_battery_enable_bit_is_cleared_to_stop():
    control = power_controls(device=HS3_DEVICE)[BATTERY]

    assert _sent(HS3_DEVICE, control.stop(remembered=None)) == [(0x8400, 1, (0,))]


@pytest.mark.parametrize(
    ("function", "target", "bit"),
    [
        (PowerFunction.BATTERY, 0x8405, 1),
        (PowerFunction.GRID, 0x8411, 5),
        (PowerFunction.INVERTER, 0x8402, 3),
    ],
)
def test_each_hs3_function_uses_its_own_target_row_and_enable_bit(
    function: PowerFunction, target: int, bit: int
):
    control = power_controls(device=HS3_DEVICE)[function]

    start = control.start(watts=0, prior=None)

    assert [
        (address, field) for address, field, _ in _sent(HS3_DEVICE, start.writes)
    ] == [
        (target, None),
        (0x8400, bit),
    ]


def test_the_h2_battery_is_charged_through_passive_mode_and_put_back_to_self_use():
    control = power_controls(device=H2_DEVICE)[BATTERY]

    start = control.start(watts=-600, prior=SELF_USE)
    stop = control.stop(remembered=start.remember)

    assert _sent(H2_DEVICE, start.writes) == [
        (0x3639, None, (75,)),
        (0x3647, None, (3,)),
        (0x3636, None, (2,)),
    ]
    assert _sent(H2_DEVICE, stop) == [(0x3636, None, (0,)), (0x3647, None, (0,))]


def test_the_hs3_states_the_rows_of_its_enable_bit_functions():
    rows = ems_rows(profile=HS3)

    assert rows.functions == {
        "ems_battery_control": PowerFunction.BATTERY,
        "ems_grid_control": PowerFunction.GRID,
        "ems_inverter_control_with_timeout_exit": PowerFunction.INVERTER,
        "ems_inverter_control": PowerFunction.INVERTER,
    }
    assert rows.forms["ems_inverter_control"] == (
        "ems_inverter_control_with_timeout_exit",
        "ems_inverter_control",
    )
    assert rows.timeouts == {"ems_timeout"}
    assert len(rows.limits) == 5


def test_the_h2_states_no_enable_bit_rows():
    rows = ems_rows(profile=H2)

    assert (rows.functions, rows.targets) == ({}, {})
