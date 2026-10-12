from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from custom_components.saj_local.saj.catalogue import Register
from custom_components.saj_local.saj.codec import Encoding, Range
from custom_components.saj_local.saj.definitions import (
    Access,
    Definition,
    EntityKind,
    Quantity,
)
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.models import Evidence, PowerFunction
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from custom_components.saj_local.saj.telemetry import Telemetry

if TYPE_CHECKING:
    from custom_components.saj_local.saj.codec import Value

ENTRY_ID = "logical-installation-123"
FIRST_ADDRESS = 0x1000


def register(
    *,
    key: str = "test_row",
    kind: EntityKind = EntityKind.SENSOR,
    quantity: Quantity = Quantity.COUNT,
    encoding: Encoding = Encoding.U16,
    core: bool = True,
    **definition_changes: object,
) -> Register:
    return Register(
        definition=Definition(
            key=key,
            quantity=quantity,
            encoding=encoding,
            kind=kind,
            **definition_changes,
        ),
        address=FIRST_ADDRESS,
        evidence=Evidence.VERIFIED,
        core=core,
    )


def device(*, display_name: str = "Alpha", detected: bool = True) -> Device:
    return Device(
        serial="TEST-001",
        device_type=0x1610,
        rated_power=12000,
        profile=replace(HS3, key=display_name.lower(), display_name=display_name),
        detected=detected,
    )


class FakeCoordinator:
    def __init__(
        self,
        *,
        values: dict[str, Value] | None = None,
        device_under_test: Device | None = None,
    ) -> None:
        self.device = device_under_test or device()
        self.data = Telemetry(values=values or {})
        self.entry_id = ENTRY_ID
        self.last_update_success = True
        self.unavailable_keys: frozenset[str] = frozenset()
        self.last_read: frozenset[str] = frozenset()
        self.changed_keys: frozenset[str] = frozenset()
        self.assumed: dict[str, Value] = {}
        self.write = AsyncMock()
        self.power_offered: tuple[PowerFunction, ...] = ()
        self.power_state: dict[PowerFunction, bool | None] = {}
        self.power_shown: dict[PowerFunction, int | None] = {}
        self.power_limits = Range(minimum=-1000, maximum=1000)
        self.async_power_on = AsyncMock()
        self.async_power_off = AsyncMock()
        self.async_set_power_target = AsyncMock()
        self.client = SimpleNamespace(
            read_holding_registers=AsyncMock(), write_registers=AsyncMock()
        )

    def async_add_listener(self, _listener, context=None):
        del context
        return lambda: None

    def power_running(self, *, function: PowerFunction) -> bool | None:
        return self.power_state.get(function)

    def power_target_shown(self, *, function: PowerFunction) -> int | None:
        return self.power_shown.get(function)

    def power_range(self, *, function: PowerFunction) -> Range:
        del function
        return self.power_limits

    def requests_sent(self) -> int:
        return sum(
            method.await_count + method.call_count
            for method in vars(self.client).values()
        )


def register_of(*, kind: EntityKind, **changes: object) -> Register:
    forms: dict[EntityKind, dict[str, object]] = {
        EntityKind.SENSOR: {},
        EntityKind.NUMBER: {"range": Range(minimum=0, maximum=100)},
        EntityKind.SELECT: {"options": {0: "first", 1: "second"}},
        EntityKind.SWITCH: {"range": Range(minimum=0, maximum=1)},
        EntityKind.TIME: {"encoding": Encoding.TIME_OF_DAY},
        EntityKind.TEXT: {"encoding": Encoding.ADDRESS_TEXT, "words": 8},
        EntityKind.BUTTON: {"access": Access.WRITE_ONLY, "command_value": 1},
    }
    access = {
        "access": Access.READ_ONLY if kind is EntityKind.SENSOR else Access.READ_WRITE
    }
    return register(kind=kind, **{**access, **forms[kind], **changes})
