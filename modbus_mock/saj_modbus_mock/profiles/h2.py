from typing import TYPE_CHECKING

from saj_modbus_mock.device import Block
from saj_modbus_mock.exceptions import ExceptionCode
from saj_modbus_mock.models import MODELS, ModelSpec

from . import common, h2_extras
from .fields import fixed, text

if TYPE_CHECKING:
    from saj_modbus_mock.registers import Field
    from saj_modbus_mock.scenario import Scenario

SPEC: ModelSpec = MODELS["h2"]
APP_MODES = frozenset({0, 1, 2, 3, 14})
OVERRUN_CODE = ExceptionCode.ILLEGAL_DATA_ADDRESS
PERIPHERAL_START = 0x8E00
MODULE_STRIDE = 20
PERIPHERAL_MODULES = 5
SERIAL_WORDS = 8
BATTERY_TYPE_100AH = 3


def peripheral_fields(*, scenario: Scenario) -> list[Field]:
    """Per-module BMS and battery pack identity; absent modules read as unused."""
    fields: list[Field] = []
    for module in range(PERIPHERAL_MODULES):
        base = PERIPHERAL_START + MODULE_STRIDE * module
        present = module < scenario.battery.modules
        number = module + 1
        bms_serial = f"BMS{number}MOCK0001" if present else ""
        pack_serial = f"PACK{number}MOCK0001" if present else ""
        fields += [
            fixed(address=base, name=f"bms{number}_type", value=int(present)),
            text(
                address=base + 1,
                name=f"bms{number}_serial",
                value=bms_serial,
                length=SERIAL_WORDS,
            ),
            fixed(
                address=base + 9,
                name=f"bms{number}_software",
                value=common.SOFTWARE_VERSION if present else 0,
                scale=0.001,
            ),
            fixed(
                address=base + 10,
                name=f"bms{number}_hardware",
                value=common.SOFTWARE_VERSION if present else 0,
                scale=0.001,
            ),
            fixed(
                address=base + 11,
                name=f"battery{number}_type",
                value=BATTERY_TYPE_100AH if present else 0,
            ),
            text(
                address=base + 12,
                name=f"battery{number}_serial",
                value=pack_serial,
                length=SERIAL_WORDS,
            ),
        ]
    return fields


def build_blocks(*, scenario: Scenario) -> tuple[Block, ...]:
    return (
        Block(
            start=0x8F00,
            end=0x8F1C,
            fields=tuple(common.information_fields(scenario=scenario, spec=SPEC)),
        ),
        Block(
            start=PERIPHERAL_START,
            end=0x8E63,
            fields=tuple(peripheral_fields(scenario=scenario)),
        ),
        Block(
            start=0x4000,
            end=0x4166,
            fields=(
                *common.realtime_energy_fields(
                    scenario=scenario, phases=SPEC.phases, extended=False
                ),
                *h2_extras.realtime_fields(),
            ),
        ),
        Block(
            start=0x3604,
            end=0x367C,
            fields=(
                *common.settings_fields(
                    scenario=scenario, modes=APP_MODES, extended=False
                ),
                *h2_extras.settings_fields(scenario=scenario),
            ),
        ),
        Block(
            start=0xA000,
            end=0xA037,
            fields=tuple(common.battery_fields(populated=True)),
        ),
        Block(
            start=0xA03C,
            end=0xA065,
            fields=tuple(
                common.meter_fields(
                    phases=SPEC.phases, with_meter_b=False, extended=False
                )
            ),
        ),
        Block(
            start=common.FACTORY_BLOCK_START,
            end=common.FACTORY_BLOCK_END,
            fields=tuple(common.factory_command_fields()),
        ),
    )
