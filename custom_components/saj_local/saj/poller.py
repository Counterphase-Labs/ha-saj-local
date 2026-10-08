from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, NoReturn, Protocol

from .budget import requests_per_minute
from .client import ModbusError
from .device import identify
from .errors import ModelError
from .telemetry import plan_reads, read_telemetry

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Collection, Mapping

    from .client import ModbusTcpClient, RegisterReader
    from .device import Device
    from .guard import EndpointGuard
    from .health import ReadHealth, Refusal
    from .schedule import Schedule
    from .telemetry import Readout, ReadRange

_LOGGER = logging.getLogger(__name__)

RECONNECT_REQUESTS = 3


class IdentityChangedError(Exception):
    def __init__(self) -> None:
        message = "Device identity changed at configured endpoint"
        super().__init__(message)


CYCLE_ERRORS: tuple[type[Exception], ...] = (
    ModelError,
    ValueError,
    ModbusError,
    IdentityChangedError,
    TimeoutError,
    OSError,
)


class CycleFailedError(Exception):
    def __init__(self, *, cause: Exception, next_wakeup: float) -> None:
        super().__init__(str(cause))
        self.cause = cause
        self.next_wakeup = next_wakeup


@dataclass(frozen=True)
class CycleResult:
    values: Mapping[str, int | float | None]
    read: frozenset[str]
    refused: Mapping[str, int]
    suspended: frozenset[str]
    unavailable: frozenset[str]
    next_wakeup: float | None


@dataclass(frozen=True)
class CadencePlan:
    interval: int
    keys: frozenset[str]
    ranges: tuple[tuple[int, int], ...]
    default: bool

    @property
    def requests(self) -> int:
        return len(self.ranges)


class Bound(Protocol):
    def __call__(
        self, awaitable: Awaitable[Readout], timeout: float, /
    ) -> Awaitable[Readout]: ...


class Planner(Protocol):
    def __call__(
        self, *, device: Device, enabled: Collection[str], isolated: Collection[str]
    ) -> list[ReadRange]: ...


class Reader(Protocol):
    def __call__(
        self,
        *,
        client: RegisterReader,
        device: Device,
        enabled: Collection[str],
        isolated: Collection[str],
    ) -> Awaitable[Readout]: ...


class Identifier(Protocol):
    def __call__(
        self, *, client: RegisterReader, selection: str
    ) -> Awaitable[Device]: ...


class _CountingReader:
    def __init__(self, client: RegisterReader) -> None:
        self._client = client
        self.requests = 0

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.requests += 1
        return await self._client.read_holding_registers(address=address, count=count)


@dataclass(frozen=True)
class Target:
    client: ModbusTcpClient
    device: Device
    selection: str


@dataclass(frozen=True)
class Tracking:
    schedule: Schedule
    health: ReadHealth
    guard: EndpointGuard


@dataclass(frozen=True)
class Services:
    clock: Callable[[], float]
    bound: Bound
    plan: Planner = plan_reads
    read: Reader = read_telemetry
    identity: Identifier = identify


class Poller:
    def __init__(
        self, *, target: Target, tracking: Tracking, services: Services
    ) -> None:
        self._client = target.client
        self._device = target.device
        self._selection = target.selection
        self._schedule = tracking.schedule
        self._health = tracking.health
        self._guard = tracking.guard
        self._services = services
        self.stale_reconnects = 0

    @property
    def consecutive_failures(self) -> int:
        return self._guard.consecutive_failures

    @property
    def backoff_seconds(self) -> float:
        return self._guard.backoff_delay

    @property
    def refusals(self) -> Mapping[str, Refusal]:
        return self._health.refusals

    def cadence_plans(self) -> tuple[CadencePlan, ...]:
        return tuple(
            CadencePlan(
                interval=cadence.interval,
                keys=cadence.keys,
                ranges=tuple(
                    (read_range.address, read_range.count)
                    for read_range in self._services.plan(
                        device=self._device,
                        enabled=cadence.keys,
                        isolated=frozenset(),
                    )
                ),
                default=cadence.default,
            )
            for cadence in self._schedule.cadences
        )

    def planned_load(self) -> float:
        return requests_per_minute(
            reads=((plan.interval, plan.requests) for plan in self.cadence_plans())
        )

    async def run(self, *, enabled: Collection[str]) -> CycleResult:
        now = self._services.clock()
        reconnect = not self._client.is_connected()
        if reconnect:
            self._schedule.require_full_read()
        enabled_keys = frozenset(enabled)
        keys = (
            (self._schedule.due(now=now) & enabled_keys) - self._health.suspended()
        ) | (self._health.retests_due(now=now) & enabled_keys)
        if not keys:
            self._schedule.mark_read(now=now)
            return self._result(enabled=enabled_keys, readout=None)
        isolated = self._health.refused()
        full_keys = (enabled_keys - self._health.suspended()) | (
            self._health.retests_due(now=now) & enabled_keys
        )
        planned = max(
            len(
                self._services.plan(
                    device=self._device, enabled=planned_keys, isolated=isolated
                )
            )
            for planned_keys in (keys, full_keys)
        )
        deadline = self._client.worst_case_duration(
            requests=planned + RECONNECT_REQUESTS
        )
        try:
            readout = await self._services.bound(
                self._cycle(
                    reconnect=reconnect,
                    keys=keys,
                    full_keys=full_keys,
                    isolated=isolated,
                ),
                deadline,
            )
        except asyncio.CancelledError:
            await self._client.close()
            raise
        except CYCLE_ERRORS as err:
            await self._fail(error=err)
        self._record(readout=readout, now=now)
        self._schedule.mark_read(now=now)
        self._guard.succeeded()
        return self._result(enabled=enabled_keys, readout=readout)

    async def _cycle(
        self,
        *,
        reconnect: bool,
        keys: Collection[str],
        full_keys: Collection[str],
        isolated: Collection[str],
    ) -> Readout:
        if reconnect:
            await self._reopen()
        counter = _CountingReader(self._client)
        try:
            return await self._services.read(
                client=counter, device=self._device, enabled=keys, isolated=isolated
            )
        except ModbusError as err:
            if reconnect or not err.peer_closed or counter.requests != 1:
                raise
        self.stale_reconnects += 1
        _LOGGER.debug("Reopening a stale connection")
        await self._reopen()
        return await self._services.read(
            client=self._client,
            device=self._device,
            enabled=full_keys,
            isolated=isolated,
        )

    async def _reopen(self) -> None:
        await self._client.close()
        await self._client.connect()
        current = await self._services.identity(
            client=self._client, selection=self._selection
        )
        if current.serial != self._device.serial:
            raise IdentityChangedError

    async def _fail(self, *, error: Exception) -> NoReturn:
        if not (isinstance(error, ModbusError) and error.device_unavailable):
            await self._client.close()
        now = self._services.clock()
        delay = self._guard.failed(now=now, base_delay=self._schedule.shortest_interval)
        self._schedule.require_full_read()
        raise CycleFailedError(cause=error, next_wakeup=now + delay) from error

    def _record(self, *, readout: Readout, now: float) -> None:
        for key in readout.values:
            if self._health.record_success(key=key):
                _LOGGER.info(
                    "SAJ sensor %s answers again and is no longer suspended", key
                )
        for key, code in readout.refusals.items():
            if self._health.record_refusal(key=key, code=code, now=now):
                _LOGGER.warning(
                    "SAJ sensor %s suspended after repeated refusals (code %s)",
                    key,
                    code,
                )

    def _result(
        self, *, enabled: frozenset[str], readout: Readout | None
    ) -> CycleResult:
        return CycleResult(
            values={} if readout is None else readout.values,
            read=frozenset() if readout is None else frozenset(readout.values),
            refused={} if readout is None else readout.refusals,
            suspended=self._health.suspended(),
            unavailable=self._health.refused(),
            next_wakeup=self._schedule.next_due(
                now=self._services.clock(), enabled=enabled
            ),
        )
