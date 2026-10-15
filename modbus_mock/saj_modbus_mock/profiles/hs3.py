from typing import TYPE_CHECKING

from saj_modbus_mock.device import Block
from saj_modbus_mock.exceptions import ExceptionCode
from saj_modbus_mock.models import MODELS, ModelSpec

from . import common, hs3_equipment, parallel
from .fields import fixed
from .undocumented import UNDOCUMENTED_SETTINGS

if TYPE_CHECKING:
    from saj_modbus_mock.registers import Field
    from saj_modbus_mock.scenario import Scenario

SPEC: ModelSpec = MODELS["hs3"]
APP_MODES = frozenset({0, 1, 2, 6, 11})
SETTINGS_CHECKSUM = 58591
SETTINGS_LENGTH = 240
DEVICE_TYPE_MIRROR = 0x366C
RATED_POWER_MIRROR = 0x366D
OVERRUN_CODE = ExceptionCode.BLOCK_OVERRUN


def _undocumented(*, scenario: Scenario) -> list[Field]:
    mirrors = {
        DEVICE_TYPE_MIRROR: SPEC.device_type,
        RATED_POWER_MIRROR: scenario.device.rated_power_w,
    }
    fields = [
        fixed(address=address, name=f"undocumented_{address:04x}", value=value)
        for first, last, value in UNDOCUMENTED_SETTINGS
        for address in range(first, last + 1)
    ]
    fields += [
        fixed(address=address, name=f"undocumented_{address:04x}", value=value)
        for address, value in mirrors.items()
    ]
    return fields


def _settings_block_fields(*, scenario: Scenario) -> list[Field]:
    return [
        fixed(address=0x3600, name="settings_checksum", value=SETTINGS_CHECKSUM),
        fixed(address=0x3601, name="settings_length", value=SETTINGS_LENGTH),
        *common.settings_fields(scenario=scenario, modes=APP_MODES, extended=True),
        *_undocumented(scenario=scenario),
    ]


def build_blocks(*, scenario: Scenario) -> tuple[Block, ...]:
    charger_gate = (
        None if scenario.ev_charger.installed else ExceptionCode.CHARGER_UNAVAILABLE
    )
    return (
        Block(
            start=0x8F00,
            end=0x8F1C,
            fields=tuple(common.information_fields(scenario=scenario, spec=SPEC)),
        ),
        Block(
            start=0x4000,
            end=0x4176,
            fields=tuple(
                common.realtime_energy_fields(
                    scenario=scenario, phases=SPEC.phases, extended=True
                ),
            ),
        ),
        Block(
            start=0x3600,
            end=0x36EF,
            fields=tuple(_settings_block_fields(scenario=scenario)),
        ),
        Block(start=0x0F00, end=0x0F2F, fields=tuple(hs3_equipment.ethernet_fields())),
        Block(
            start=0x4B00,
            end=0x4B47,
            fields=tuple(hs3_equipment.ev_settings_fields(scenario=scenario)),
        ),
        Block(
            start=0x3024,
            end=0x30BB,
            fields=tuple(hs3_equipment.ev_data_fields()),
            unavailable=charger_gate,
        ),
        Block(
            start=0x4200,
            end=0x427C,
            fields=tuple(parallel.parallel_fields(scenario=scenario, extended=True)),
        ),
        Block(start=0x513E, end=0x51BE, fields=tuple(hs3_equipment.average_fields())),
        Block(
            start=0xA000,
            end=0xA077,
            fields=(
                *common.battery_fields(populated=False),
                *common.meter_fields(phases=SPEC.phases, extended=True),
            ),
        ),
        Block(start=0x8400, end=0x8412, fields=tuple(hs3_equipment.ems_fields())),
        Block(
            start=common.FACTORY_BLOCK_START,
            end=common.FACTORY_BLOCK_END,
            fields=tuple(common.factory_command_fields()),
        ),
    )
