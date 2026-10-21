from typing import TYPE_CHECKING

from saj_local_mock.device import Block
from saj_local_mock.exceptions import ExceptionCode
from saj_local_mock.models import MODELS, ModelSpec

from . import common, h2_extras, parallel
from .fields import fixed, text

if TYPE_CHECKING:
    from saj_local_mock.registers import Field
    from saj_local_mock.scenario import Scenario

SPEC: ModelSpec = MODELS["h2"]
APP_MODES = {
    0: "Self-use",
    1: "Time",
    2: "Backup",
    3: "Passive",
    10: "Peak shaving",
    14: "Old mode",
}
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
            name="Identity",
        ),
        Block(
            start=PERIPHERAL_START,
            end=0x8E63,
            fields=tuple(peripheral_fields(scenario=scenario)),
            name="Battery modules",
        ),
        Block(
            start=0x4000,
            end=0x4176,
            fields=(
                *common.realtime_energy_fields(
                    scenario=scenario, phases=SPEC.phases, extended=True
                ),
                *h2_extras.realtime_fields(),
            ),
            name="Realtime data",
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
            name="Settings",
        ),
        Block(
            start=0x4200,
            end=0x4264,
            fields=tuple(parallel.parallel_fields(scenario=scenario, extended=False)),
            name="Parallel system",
        ),
        Block(
            start=0xA000,
            end=0xA037,
            fields=tuple(common.battery_fields(populated=True)),
            name="Battery",
        ),
        Block(
            start=0xA03C,
            end=0xA065,
            fields=tuple(common.meter_fields(phases=SPEC.phases, extended=False)),
            name="Meters",
        ),
        Block(
            start=common.FACTORY_BLOCK_START,
            end=common.FACTORY_BLOCK_END,
            fields=tuple(common.factory_command_fields()),
            name="Commands",
        ),
    )
