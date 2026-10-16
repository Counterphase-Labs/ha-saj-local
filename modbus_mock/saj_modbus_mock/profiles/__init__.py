from typing import TYPE_CHECKING

from saj_modbus_mock.models import HS3

from . import h2, hs3
from .fault_tables import build_fault_map

if TYPE_CHECKING:
    from saj_modbus_mock.device import Block
    from saj_modbus_mock.exceptions import ExceptionCode
    from saj_modbus_mock.scenario import Scenario


def build_blocks(*, scenario: Scenario) -> tuple[Block, ...]:
    if scenario.device.model.name == HS3:
        return hs3.build_blocks(scenario=scenario)
    return h2.build_blocks(scenario=scenario)


def overrun_code(*, scenario: Scenario) -> ExceptionCode:
    return hs3.OVERRUN_CODE if scenario.device.model.name == HS3 else h2.OVERRUN_CODE


__all__ = ["build_blocks", "build_fault_map", "overrun_code"]
