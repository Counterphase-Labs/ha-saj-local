import collections
import dataclasses
import enum
import hashlib

from .exceptions import ExceptionCode

PERCENT = 100
MILLISECONDS_PER_SECOND = 1000
DRAW_RANGE = 2**64
MAX_DELAY_MS = 60_000
MAX_SECONDS = 86_400
MAX_LOCKOUT_REQUESTS = 100_000
ADDRESS_BOUNDS = (0, 0xFFFF)
CODE_BOUNDS = (0, 0xFF)
STATUS_ONLINE = "online"
STATUS_LOCKED_OUT = "locked_out"
REFUSED_BLOCKS = "refused_blocks"


class LinkFault(enum.StrEnum):
    OFFLINE = "offline"
    UNRESPONSIVE = "unresponsive"
    LOCKOUT = "lockout"
    DROPPED_CONNECTION = "dropped_connection"
    NO_ANSWER = "no_answer"
    REFUSED_BLOCK = "refused_block"
    DEVICE_FAILURE = "device_failure"
    BUSY = "busy"


class Action(enum.StrEnum):
    ANSWER = "answer"
    EXCEPTION = "exception"
    NO_ANSWER = "no_answer"
    DROP = "drop"


class Kind(enum.StrEnum):
    WHOLE = "whole"
    PERCENT = "percent"
    FLAG = "flag"


@dataclasses.dataclass(frozen=True, slots=True)
class LinkParameter:
    name: str
    kind: Kind
    minimum: int | None = None
    maximum: int | None = None
    unit: str = ""


LINK_PARAMETERS = (
    LinkParameter(
        name="latency_ms",
        kind=Kind.WHOLE,
        minimum=0,
        maximum=MAX_DELAY_MS,
        unit="ms",
    ),
    LinkParameter(
        name="jitter_ms",
        kind=Kind.WHOLE,
        minimum=0,
        maximum=MAX_DELAY_MS,
        unit="ms",
    ),
    LinkParameter(
        name="no_answer_percent",
        kind=Kind.PERCENT,
        minimum=0,
        maximum=PERCENT,
        unit="%",
    ),
    LinkParameter(
        name="busy_percent",
        kind=Kind.PERCENT,
        minimum=0,
        maximum=PERCENT,
        unit="%",
    ),
    LinkParameter(
        name="device_failure_percent",
        kind=Kind.PERCENT,
        minimum=0,
        maximum=PERCENT,
        unit="%",
    ),
    LinkParameter(
        name="dropped_connection_percent",
        kind=Kind.PERCENT,
        minimum=0,
        maximum=PERCENT,
        unit="%",
    ),
    LinkParameter(
        name="late_duplicate_percent",
        kind=Kind.PERCENT,
        minimum=0,
        maximum=PERCENT,
        unit="%",
    ),
    LinkParameter(name="unresponsive", kind=Kind.FLAG),
    LinkParameter(name="offline", kind=Kind.FLAG),
    LinkParameter(
        name="offline_seconds",
        kind=Kind.WHOLE,
        minimum=0,
        maximum=MAX_SECONDS,
        unit="s",
    ),
    LinkParameter(
        name="offline_period_seconds",
        kind=Kind.WHOLE,
        minimum=0,
        maximum=MAX_SECONDS,
        unit="s",
    ),
    LinkParameter(
        name="lockout_requests",
        kind=Kind.WHOLE,
        minimum=0,
        maximum=MAX_LOCKOUT_REQUESTS,
    ),
    LinkParameter(
        name="lockout_window_seconds",
        kind=Kind.WHOLE,
        minimum=0,
        maximum=MAX_SECONDS,
        unit="s",
    ),
    LinkParameter(name="lockout_whole_port", kind=Kind.FLAG),
)


@dataclasses.dataclass(frozen=True, slots=True)
class RefusedBlock:
    start: int
    end: int
    code: int

    def overlaps(self, *, start: int, count: int) -> bool:
        return start <= self.end and start + count - 1 >= self.start


@dataclasses.dataclass(frozen=True, slots=True)
class LinkSettings:
    latency_ms: int = 0
    jitter_ms: int = 0
    no_answer_percent: float = 0
    busy_percent: float = 0
    device_failure_percent: float = 0
    dropped_connection_percent: float = 0
    late_duplicate_percent: float = 0
    refused_blocks: tuple[RefusedBlock, ...] = ()
    unresponsive: bool = False
    offline: bool = False
    offline_seconds: int = 0
    offline_period_seconds: int = 0
    lockout_requests: int = 0
    lockout_window_seconds: int = 0
    lockout_whole_port: bool = False


def link_values(*, settings: LinkSettings) -> dict[str, object]:
    values: dict[str, object] = {
        parameter.name: getattr(settings, parameter.name)
        for parameter in LINK_PARAMETERS
    }
    values[REFUSED_BLOCKS] = [
        {"start": block.start, "end": block.end, "code": block.code}
        for block in settings.refused_blocks
    ]
    return values


def changed_link(*, settings: LinkSettings, scenario: LinkSettings) -> list[str]:
    running = link_values(settings=settings)
    return [
        name
        for name, value in link_values(settings=scenario).items()
        if running[name] != value
    ]


def check_combination(*, settings: LinkSettings) -> tuple[str, str] | None:
    if settings.offline_seconds > settings.offline_period_seconds:
        return "offline_seconds", "must be <= offline_period_seconds"
    if settings.lockout_requests and not settings.lockout_window_seconds:
        return "lockout_window_seconds", "must be >= 1 when lockout_requests is set"
    return None


@dataclasses.dataclass(frozen=True, slots=True)
class ConnectionDecision:
    fault: LinkFault | None


@dataclasses.dataclass(frozen=True, slots=True)
class RequestDecision:
    action: Action
    fault: LinkFault | None
    exception_code: int
    delay_s: float
    late_duplicate: bool


@dataclasses.dataclass(frozen=True, slots=True)
class LockoutState:
    addresses: tuple[str, ...]
    whole_port: bool


@dataclasses.dataclass(frozen=True, slots=True)
class ModuleState:
    offline: bool
    unresponsive: bool
    locked_out: bool
    locked_addresses: tuple[str, ...]
    whole_port: bool

    @property
    def status(self) -> str:
        if self.offline:
            return LinkFault.OFFLINE.value
        if self.unresponsive:
            return LinkFault.UNRESPONSIVE.value
        if self.locked_out:
            return STATUS_LOCKED_OUT
        return STATUS_ONLINE

    def to_json(self) -> dict[str, object]:
        return {
            "status": self.status,
            "offline": self.offline,
            "unresponsive": self.unresponsive,
            "locked_out": self.locked_out,
            "locked_addresses": list(self.locked_addresses),
            "whole_port": self.whole_port,
        }


_ACTIONS: dict[LinkFault | None, Action] = {
    None: Action.ANSWER,
    LinkFault.OFFLINE: Action.DROP,
    LinkFault.UNRESPONSIVE: Action.NO_ANSWER,
    LinkFault.LOCKOUT: Action.DROP,
    LinkFault.DROPPED_CONNECTION: Action.DROP,
    LinkFault.NO_ANSWER: Action.NO_ANSWER,
    LinkFault.REFUSED_BLOCK: Action.EXCEPTION,
    LinkFault.DEVICE_FAILURE: Action.EXCEPTION,
    LinkFault.BUSY: Action.EXCEPTION,
}
_EXCEPTION_CODES: dict[LinkFault | None, int] = {
    LinkFault.DEVICE_FAILURE: ExceptionCode.DEVICE_FAILURE,
    LinkFault.BUSY: ExceptionCode.BUSY,
}


def _draw(*, seed: int, sequence: int, label: str) -> float:
    digest = hashlib.sha256(f"{seed}:{sequence}:{label}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / DRAW_RANGE


class Link:
    def __init__(self, *, seed: int, settings: LinkSettings | None = None) -> None:
        self._seed = seed
        self._settings = settings or LinkSettings()
        self._locked_addresses: set[str] = set()
        self._port_locked = False
        self._windows: dict[str, collections.deque[float]] = {}
        self._drop_generation = 0

    @property
    def settings(self) -> LinkSettings:
        return self._settings

    @property
    def drop_generation(self) -> int:
        return self._drop_generation

    def set_seed(self, *, seed: int) -> None:
        self._seed = seed

    def refused_code(self, *, start: int, count: int) -> int | None:
        block = self._refusing_block(start=start, count=count)
        return None if block is None else block.code

    def replace_settings(self, *, settings: LinkSettings) -> None:
        self._settings = settings

    def drop_connections_now(self) -> None:
        self._drop_generation += 1

    def reset_module(self) -> None:
        self._locked_addresses.clear()
        self._port_locked = False
        self._windows.clear()

    def lockout_state(self) -> LockoutState:
        return LockoutState(
            addresses=tuple(sorted(self._locked_addresses)),
            whole_port=self._port_locked,
        )

    def restore_lockout(self, *, state: LockoutState) -> None:
        self._locked_addresses = set(state.addresses)
        self._port_locked = state.whole_port

    def is_offline(self, *, now: float) -> bool:
        settings = self._settings
        if settings.offline:
            return True
        if settings.offline_period_seconds <= 0:
            return False
        return now % settings.offline_period_seconds < settings.offline_seconds

    def module_state(self, *, now: float) -> ModuleState:
        return ModuleState(
            offline=self.is_offline(now=now),
            unresponsive=self._settings.unresponsive,
            locked_out=self._port_locked or bool(self._locked_addresses),
            locked_addresses=tuple(sorted(self._locked_addresses)),
            whole_port=self._port_locked,
        )

    def decide_connection(self, *, client: str, now: float) -> ConnectionDecision:
        if self.is_offline(now=now):
            return ConnectionDecision(fault=LinkFault.OFFLINE)
        if self._is_locked(client=client):
            return ConnectionDecision(fault=LinkFault.LOCKOUT)
        return ConnectionDecision(fault=None)

    def decide_request(
        self,
        *,
        client: str,
        sequence: int,
        start: int,
        count: int,
        now: float,
    ) -> RequestDecision:
        checks = (
            (LinkFault.OFFLINE, lambda: self.is_offline(now=now)),
            (LinkFault.UNRESPONSIVE, lambda: self._settings.unresponsive),
            (LinkFault.LOCKOUT, lambda: self._locks_out(client=client, now=now)),
            (
                LinkFault.DROPPED_CONNECTION,
                lambda: self._rolls(
                    sequence=sequence, fault=LinkFault.DROPPED_CONNECTION
                ),
            ),
            (
                LinkFault.NO_ANSWER,
                lambda: self._rolls(sequence=sequence, fault=LinkFault.NO_ANSWER),
            ),
            (
                LinkFault.REFUSED_BLOCK,
                lambda: self._refusing_block(start=start, count=count) is not None,
            ),
            (
                LinkFault.DEVICE_FAILURE,
                lambda: self._rolls(sequence=sequence, fault=LinkFault.DEVICE_FAILURE),
            ),
            (
                LinkFault.BUSY,
                lambda: self._rolls(sequence=sequence, fault=LinkFault.BUSY),
            ),
        )
        fault = next((fault for fault, applies in checks if applies()), None)
        return RequestDecision(
            action=_ACTIONS[fault],
            fault=fault,
            exception_code=self._exception_code(fault=fault, start=start, count=count),
            delay_s=self._delay_s(sequence=sequence),
            late_duplicate=self._chance(
                percent=self._settings.late_duplicate_percent,
                sequence=sequence,
                label="late_duplicate",
            ),
        )

    def _refusing_block(self, *, start: int, count: int) -> RefusedBlock | None:
        return next(
            (
                block
                for block in self._settings.refused_blocks
                if block.overlaps(start=start, count=count)
            ),
            None,
        )

    def _exception_code(
        self, *, fault: LinkFault | None, start: int, count: int
    ) -> int:
        block = self._refusing_block(start=start, count=count)
        if fault is LinkFault.REFUSED_BLOCK and block is not None:
            return block.code
        return _EXCEPTION_CODES.get(fault, 0)

    def _is_locked(self, *, client: str) -> bool:
        return self._port_locked or client in self._locked_addresses

    def _locks_out(self, *, client: str, now: float) -> bool:
        settings = self._settings
        if self._is_locked(client=client):
            return True
        if settings.lockout_requests <= 0:
            return False
        window = self._windows.setdefault(client, collections.deque())
        window.append(now)
        while window[0] < now - settings.lockout_window_seconds:
            window.popleft()
        if len(window) <= settings.lockout_requests:
            return False
        if settings.lockout_whole_port:
            self._port_locked = True
        else:
            self._locked_addresses.add(client)
        return True

    def _chance(self, *, percent: float, sequence: int, label: str) -> bool:
        draw = _draw(seed=self._seed, sequence=sequence, label=label)
        return draw * PERCENT < percent

    def _rolls(self, *, sequence: int, fault: LinkFault) -> bool:
        percent = {
            LinkFault.DROPPED_CONNECTION: self._settings.dropped_connection_percent,
            LinkFault.NO_ANSWER: self._settings.no_answer_percent,
            LinkFault.DEVICE_FAILURE: self._settings.device_failure_percent,
            LinkFault.BUSY: self._settings.busy_percent,
        }[fault]
        return self._chance(percent=percent, sequence=sequence, label=fault.value)

    def _delay_s(self, *, sequence: int) -> float:
        settings = self._settings
        spread = _draw(seed=self._seed, sequence=sequence, label="jitter") * 2 - 1
        delay_ms = settings.latency_ms + settings.jitter_ms * spread
        return max(delay_ms, 0) / MILLISECONDS_PER_SECOND
