from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from functools import partial
from typing import TYPE_CHECKING, NoReturn, Protocol

from .client import ConnectionReason, ModbusError
from .device import identify
from .errors import ModelError
from .health import halves
from .load import planned_load
from .log import LabelledLogger
from .memory import FailureOutcome
from .models import FunctionCode
from .telemetry import plan_reads, read_telemetry

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Collection, Mapping, Sequence

    from .catalogue import Row
    from .client import ModbusTcpClient, RegisterReader
    from .codec import Value
    from .device import Device
    from .guard import EndpointGuard
    from .health import Break, ReadHealth, Refusal, Region
    from .schedule import Schedule
    from .telemetry import Readout, ReadRange

_LOGGER = logging.getLogger(__name__)

RECONNECT_REQUESTS = 3
REQUEST_ANSWERED = "ok"


class IdentityChangedError(Exception):
    def __init__(self, *, serial: str) -> None:
        message = "Device identity changed at configured endpoint"
        super().__init__(message)
        self.serial = serial


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
    values: Mapping[str, Value]
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
        self,
        *,
        device: Device,
        enabled: Collection[str],
        narrowing: Collection[Region],
        breaks: Collection[Break],
    ) -> list[ReadRange]: ...


class Reader(Protocol):
    def __call__(
        self,
        *,
        client: RegisterReader,
        device: Device,
        enabled: Collection[str],
        narrowing: Collection[Region],
        breaks: Collection[Break],
    ) -> Awaitable[Readout]: ...


class Identifier(Protocol):
    def __call__(
        self, *, client: RegisterReader, selection: str
    ) -> Awaitable[Device]: ...


def _failure_label(error: ModbusError) -> str:
    if error.exception_code is not None:
        return f"exception {error.exception_code}"
    return error.failure_outcome.value


@dataclass(frozen=True)
class _Request:
    address: int
    count: int
    function: FunctionCode
    outcome: str

    def describe(self) -> str:
        return (
            f"{self.address:#06x}+{self.count} "
            f"function {self.function:#04x} {self.outcome}"
        )


@dataclass
class _Poll:
    due: tuple[int, ...]
    started: float
    reconnect: bool
    requests: list[_Request] = field(default_factory=list)


class _CountingReader:
    def __init__(self, client: RegisterReader, *, poll: _Poll) -> None:
        self._client = client
        self._poll = poll
        self.requests = 0

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        return await self._read(
            function=FunctionCode.HOLDING,
            read=self._client.read_holding_registers,
            address=address,
            count=count,
        )

    async def read_input_registers(self, address: int, count: int) -> tuple[int, ...]:
        return await self._read(
            function=FunctionCode.INPUT,
            read=self._client.read_input_registers,
            address=address,
            count=count,
        )

    async def _read(
        self,
        *,
        function: FunctionCode,
        read: Callable[..., Awaitable[tuple[int, ...]]],
        address: int,
        count: int,
    ) -> tuple[int, ...]:
        self.requests += 1
        request = partial(_Request, address=address, count=count, function=function)
        try:
            words = await read(address=address, count=count)
        except ModbusError as err:
            self._poll.requests.append(request(outcome=_failure_label(err)))
            raise
        except asyncio.CancelledError:
            self._poll.requests.append(request(outcome=FailureOutcome.TIMEOUT.value))
            raise
        self._poll.requests.append(request(outcome=REQUEST_ANSWERED))
        return words


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
        self,
        *,
        target: Target,
        tracking: Tracking,
        services: Services,
        enabled: Collection[str],
        label: str,
    ) -> None:
        self._log = LabelledLogger(logger=_LOGGER, label=label)
        self._client = target.client
        self._device = target.device
        self._selection = target.selection
        self._schedule = tracking.schedule
        self._health = tracking.health
        self._guard = tracking.guard
        self._services = services
        self.stale_reconnects = 0
        self._enabled = frozenset(enabled)

    @property
    def consecutive_failures(self) -> int:
        return self._guard.consecutive_failures

    @property
    def backoff_seconds(self) -> float:
        return self._guard.backoff_delay

    @property
    def refusals(self) -> Mapping[str, Refusal]:
        return self._health.refusals

    @property
    def narrowing(self) -> tuple[Region, ...]:
        return self._health.narrowing

    @property
    def breaks(self) -> frozenset[Break]:
        return self._health.breaks

    def cadence_plans(self) -> tuple[CadencePlan, ...]:
        plans = []
        for cadence in self._schedule.cadences:
            keys = cadence.keys & self._enabled
            plans.append(
                CadencePlan(
                    interval=cadence.interval,
                    keys=keys,
                    ranges=tuple(
                        (read_range.address, read_range.count)
                        for read_range in self._services.plan(
                            device=self._device,
                            enabled=keys,
                            narrowing=(),
                            breaks=self._health.breaks,
                        )
                    ),
                    default=cadence.default,
                )
            )
        return tuple(plans)

    def planned_load(self) -> float:
        return planned_load(
            fit=self._device.fit,
            enabled=self._enabled,
            cadences=self._schedule.cadences,
            breaks=self._health.breaks,
        )

    async def run(self, *, enabled: Collection[str]) -> CycleResult:
        now = self._services.clock()
        reconnect = not self._client.is_connected()
        if reconnect:
            self._schedule.require_full_read()
        enabled_keys = frozenset(enabled)
        self._enabled = enabled_keys
        poll = _Poll(
            due=tuple(
                cadence.interval for cadence in self._schedule.due_cadences(now=now)
            ),
            started=now,
            reconnect=reconnect,
        )
        keys = (
            (self._schedule.due(now=now) & enabled_keys) - self._health.suspended()
        ) | (self._health.retests_due(now=now) & enabled_keys)
        if not keys:
            self._schedule.mark_read(now=now)
            return self._result(enabled=enabled_keys, readout=None)
        narrowing = self._health.narrowing
        breaks = self._health.breaks
        full_keys = (enabled_keys - self._health.suspended()) | (
            self._health.retests_due(now=now) & enabled_keys
        )
        planned = max(
            len(
                self._services.plan(
                    device=self._device,
                    enabled=planned_keys,
                    narrowing=narrowing,
                    breaks=breaks,
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
                    poll=poll,
                    keys=keys,
                    full_keys=full_keys,
                    narrowing=narrowing,
                    breaks=breaks,
                ),
                deadline,
            )
        except asyncio.CancelledError:
            await self._client.close(reason=ConnectionReason.RECONNECT)
            raise
        except CYCLE_ERRORS as err:
            await self._fail(error=err, poll=poll)
        self._record(readout=readout, now=now)
        self._schedule.mark_read(now=now)
        self._guard.succeeded()
        result = self._result(enabled=enabled_keys, readout=readout)
        self._log_poll(poll=poll, next_wakeup=result.next_wakeup)
        return result

    async def _cycle(
        self,
        *,
        poll: _Poll,
        keys: Collection[str],
        full_keys: Collection[str],
        narrowing: Collection[Region],
        breaks: Collection[Break],
    ) -> Readout:
        if poll.reconnect:
            await self._reopen(poll=poll, reason=ConnectionReason.RECONNECT)
        counter = _CountingReader(self._client, poll=poll)
        try:
            return await self._services.read(
                client=counter,
                device=self._device,
                enabled=keys,
                narrowing=narrowing,
                breaks=breaks,
            )
        except ModbusError as err:
            if poll.reconnect or not err.peer_closed or counter.requests != 1:
                raise
        self.stale_reconnects += 1
        self._log.debug("Reopening a stale connection")
        await self._reopen(poll=poll, reason=ConnectionReason.STALE)
        return await self._services.read(
            client=_CountingReader(self._client, poll=poll),
            device=self._device,
            enabled=full_keys,
            narrowing=narrowing,
            breaks=breaks,
        )

    async def _reopen(self, *, poll: _Poll, reason: ConnectionReason) -> None:
        await self._client.close(reason=reason)
        await self._client.connect()
        current = await self._services.identity(
            client=_CountingReader(self._client, poll=poll),
            selection=self._selection,
        )
        self._log.debug("Identity read: %s", current.description)
        if current.serial != self._device.serial:
            raise IdentityChangedError(serial=current.serial)

    async def _fail(self, *, error: Exception, poll: _Poll) -> NoReturn:
        if isinstance(error, ModbusError) and error.device_unavailable:
            next_wakeup = self._back_off()
        else:
            next_wakeup = await self.link_failed()
        self._log_poll(poll=poll, next_wakeup=next_wakeup)
        raise CycleFailedError(cause=error, next_wakeup=next_wakeup) from error

    async def link_failed(self) -> float:
        await self._client.close(reason=ConnectionReason.RECONNECT)
        return self._back_off()

    def _back_off(self) -> float:
        now = self._services.clock()
        delay = self._guard.failed(now=now, base_delay=self._schedule.shortest_interval)
        self._schedule.require_full_read()
        self._log.debug(
            "Backing off for %s s after %s consecutive failed polls",
            delay,
            self._guard.consecutive_failures,
        )
        return now + delay

    def _log_poll(self, *, poll: _Poll, next_wakeup: float | None) -> None:
        now = self._services.clock()
        self._log.debug(
            "Poll of cadences %s: %s; took %.1f s; next wake-up %s",
            [f"{interval} s" for interval in poll.due],
            ", ".join(request.describe() for request in poll.requests) or "no requests",
            now - poll.started,
            "never"
            if next_wakeup is None
            else f"in {max(0.0, next_wakeup - now):.1f} s",
        )

    def _record(self, *, readout: Readout, now: float) -> None:
        recovered = sorted(
            key for key in readout.values if self._health.record_success(key=key)
        )
        if recovered:
            self._log.info(
                "Sensors %s answer again and are no longer suspended",
                ", ".join(recovered),
            )
        for outcome in readout.outcomes:
            if outcome.code is None:
                self._health.record_request_read(rows=outcome.rows)
                continue
            suspended = self._health.record_request_refused(
                rows=outcome.rows, keys=outcome.keys, code=outcome.code, now=now
            )
            if len(outcome.rows) > 1:
                lower, upper = halves(outcome.rows)
                self._log.debug(
                    "Narrowing refused request %s of function %#04x"
                    " (exception %s) into %s and %s",
                    _span(rows=outcome.rows),
                    outcome.rows[0].function,
                    outcome.code,
                    _span(rows=lower),
                    _span(rows=upper),
                )
            if suspended:
                self._log.warning(
                    "Sensors %s suspended after repeated refusals of function %#04x"
                    " (code %s)",
                    ", ".join(sorted(suspended)),
                    outcome.rows[0].function,
                    outcome.code,
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


def _span(*, rows: Sequence[Row]) -> str:
    return f"{rows[0].address:#06x}+{rows[-1].end - rows[0].address}"
