import collections
import dataclasses
import enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

LOG_LIMIT = 2000
QUERY_LIMIT = 500
SHORT_WINDOW_SECONDS = 10
LONG_WINDOW_SECONDS = 60
BUCKET_SECONDS = 10
HISTORY_SECONDS = 30 * 60


class Operation(enum.StrEnum):
    READ = "read"
    WRITE = "write"
    OTHER = "other"


class Answer(enum.StrEnum):
    ANSWERED = "answered"
    EXCEPTION = "exception"
    NO_ANSWER = "no_answer"
    DROPPED = "dropped"
    IGNORED = "ignored"


class ConnectionEvent(enum.StrEnum):
    OPENED = "opened"
    CLOSED_BY_CLIENT = "closed_by_client"
    CLOSED_BY_MODULE = "closed_by_module"
    REFUSED = "refused"


class ConnectionReason(enum.StrEnum):
    LINK_FAULT = "link_fault"
    LOCKOUT = "lockout"
    MALFORMED_FRAME = "malformed_frame"
    OFFLINE = "offline"
    CLIENT_LIMIT = "client_limit"


@dataclasses.dataclass(frozen=True, slots=True)
class Client:
    address: str
    port: int


@dataclasses.dataclass(frozen=True, slots=True)
class DecodedField:
    address: int
    name: str
    words: tuple[int, ...]
    value: float | str | None
    label: str | None


class FieldDecoder(Protocol):
    def decode(
        self, *, start: int, words: tuple[int, ...]
    ) -> Sequence[DecodedField]: ...


@dataclasses.dataclass(frozen=True, slots=True)
class ConnectionRecord:
    at: float
    client: Client
    connection: int
    event: ConnectionEvent
    reason: ConnectionReason | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class RequestRecord:
    at: float
    client: Client
    connection: int
    transaction_id: int
    unit_id: int
    function: int
    start: int
    count: int
    operation: Operation
    answer: Answer
    exception_code: int | None
    fault: str | None
    late_duplicate: bool
    duration_ms: float
    words: tuple[int, ...]


@dataclasses.dataclass(slots=True)
class _Bucket:
    answered: int = 0
    exception: int = 0
    unanswered: int = 0


def _bucket_start(*, at: float) -> int:
    return int(at // BUCKET_SECONDS) * BUCKET_SECONDS


class _Stats:
    def __init__(self) -> None:
        self._connections_opened = 0
        self._connections_closed = 0
        self._connections_refused = 0
        self._requests = 0
        self._reads = 0
        self._writes = 0
        self._registers_read = 0
        self._registers_written = 0
        self._exceptions: collections.Counter[int] = collections.Counter()
        self._no_answers = 0
        self._dropped_connections = 0
        self._recent: collections.deque[tuple[float, int]] = collections.deque()
        self._peak = 0
        self._last_request_at: float | None = None
        self._buckets: dict[int, _Bucket] = {}

    def connection(self, *, event: ConnectionEvent) -> None:
        if event is ConnectionEvent.OPENED:
            self._connections_opened += 1
        elif event is ConnectionEvent.REFUSED:
            self._connections_refused += 1
        else:
            self._connections_closed += 1

    def request(self, *, record: RequestRecord) -> None:
        self._requests += 1
        self._last_request_at = record.at
        answered_words = len(record.words) if record.answer is Answer.ANSWERED else 0
        if record.operation is Operation.READ:
            self._reads += 1
            self._registers_read += answered_words
        elif record.operation is Operation.WRITE:
            self._writes += 1
            self._registers_written += answered_words
        if record.exception_code is not None:
            self._exceptions[record.exception_code] += 1
        if record.answer in {Answer.NO_ANSWER, Answer.IGNORED}:
            self._no_answers += 1
        if record.answer is Answer.DROPPED:
            self._dropped_connections += 1
        moved = 0 if record.operation is Operation.OTHER else answered_words
        self._slide(record=record, registers=moved)
        self._bucket(record=record)

    def _slide(self, *, record: RequestRecord, registers: int) -> None:
        self._recent.append((record.at, registers))
        while self._recent[0][0] <= record.at - LONG_WINDOW_SECONDS:
            self._recent.popleft()
        self._peak = max(self._peak, len(self._recent))

    def _bucket(self, *, record: RequestRecord) -> None:
        start = _bucket_start(at=record.at)
        for expired in [
            key for key in self._buckets if key <= record.at - HISTORY_SECONDS
        ]:
            del self._buckets[expired]
        bucket = self._buckets.setdefault(start, _Bucket())
        if record.answer is Answer.ANSWERED:
            bucket.answered += 1
        elif record.answer is Answer.EXCEPTION:
            bucket.exception += 1
        else:
            bucket.unanswered += 1

    def _within(self, *, now: float, window: int) -> int:
        return sum(1 for moment, _ in self._recent if moment > now - window)

    def _registers_within(self, *, now: float, window: int) -> int:
        return sum(
            registers for moment, registers in self._recent if moment > now - window
        )

    def counters(self, *, now: float) -> dict[str, object]:
        return {
            "connections_opened": self._connections_opened,
            "connections_closed": self._connections_closed,
            "connections_refused": self._connections_refused,
            "requests": self._requests,
            "reads": self._reads,
            "writes": self._writes,
            "registers_read": self._registers_read,
            "registers_written": self._registers_written,
            "exceptions": {
                str(code): total for code, total in sorted(self._exceptions.items())
            },
            "no_answers": self._no_answers,
            "dropped_connections": self._dropped_connections,
            "requests_last_10_seconds": self._within(
                now=now, window=SHORT_WINDOW_SECONDS
            ),
            "requests_last_60_seconds": self._within(
                now=now, window=LONG_WINDOW_SECONDS
            ),
            "registers_last_60_seconds": self._registers_within(
                now=now, window=LONG_WINDOW_SECONDS
            ),
            "peak_requests_per_60_seconds": self._peak,
            "last_request_at": self._last_request_at,
        }

    def history(self, *, now: float) -> list[dict[str, object]]:
        return [
            {
                "start": start,
                "answered": bucket.answered,
                "exception": bucket.exception,
                "unanswered": bucket.unanswered,
            }
            for start, bucket in sorted(self._buckets.items())
            if start > now - HISTORY_SECONDS
        ]


@dataclasses.dataclass(frozen=True, slots=True)
class _OpenConnection:
    client: Client
    since: float


class Recorder:
    def __init__(self, *, decoder: FieldDecoder | None = None) -> None:
        self._decoder = decoder
        self._sequence = 0
        self._log: collections.deque[dict[str, object]] = collections.deque(
            maxlen=LOG_LIMIT
        )
        self._total = _Stats()
        self._clients: dict[str, _Stats] = {}
        self._open: dict[int, _OpenConnection] = {}
        self._last_reads: dict[int, float] = {}

    def record_connection(self, *, record: ConnectionRecord) -> None:
        for stats in self._scopes(address=record.client.address):
            stats.connection(event=record.event)
        if record.event is ConnectionEvent.OPENED:
            self._open[record.connection] = _OpenConnection(
                client=record.client, since=record.at
            )
        elif record.event is not ConnectionEvent.REFUSED:
            self._open.pop(record.connection, None)
        self._append(
            entry={
                "kind": "connection",
                "at": record.at,
                "client": record.client.address,
                "port": record.client.port,
                "connection": record.connection,
                "event": record.event.value,
                "reason": record.reason.value if record.reason else None,
            }
        )

    def record_request(self, *, record: RequestRecord) -> None:
        for stats in self._scopes(address=record.client.address):
            stats.request(record=record)
        if record.operation is Operation.READ and record.answer is Answer.ANSWERED:
            for address in range(record.start, record.start + len(record.words)):
                self._last_reads[address] = record.at
        self._append(
            entry={
                "kind": "request",
                "at": record.at,
                "client": record.client.address,
                "port": record.client.port,
                "connection": record.connection,
                "transaction_id": record.transaction_id,
                "unit_id": record.unit_id,
                "function": record.function,
                "start": record.start,
                "count": record.count,
                "operation": record.operation.value,
                "answer": record.answer.value,
                "exception_code": record.exception_code,
                "fault": record.fault,
                "late_duplicate": record.late_duplicate,
                "duration_ms": record.duration_ms,
                "detail": self._detail(record=record),
            }
        )

    def entries_after(self, *, after: int) -> list[dict[str, object]]:
        later = [entry for entry in self._log if int(str(entry["sequence"])) > after]
        return later[:QUERY_LIMIT]

    def counters(self, *, now: float) -> dict[str, object]:
        return {
            "total": self._total.counters(now=now),
            "clients": {
                address: stats.counters(now=now)
                for address, stats in sorted(self._clients.items())
            },
            "connected": [
                {
                    "connection": number,
                    "client": opened.client.address,
                    "port": opened.client.port,
                    "since": opened.since,
                }
                for number, opened in sorted(self._open.items())
            ],
        }

    def history(self, *, now: float) -> dict[str, object]:
        return {
            "bucket_seconds": BUCKET_SECONDS,
            "total": self._total.history(now=now),
            "clients": {
                address: stats.history(now=now)
                for address, stats in sorted(self._clients.items())
            },
        }

    def traffic(self, *, after: int, now: float) -> dict[str, object]:
        return {
            "entries": self.entries_after(after=after),
            "latest": self._sequence,
            "counters": self.counters(now=now),
            "history": self.history(now=now),
        }

    def last_read(self, *, address: int) -> float | None:
        return self._last_reads.get(address)

    def last_read_times(self) -> dict[int, float]:
        return dict(self._last_reads)

    def reset(self) -> None:
        self._log.clear()
        self._total = _Stats()
        self._clients.clear()
        self._last_reads.clear()

    def _scopes(self, *, address: str) -> tuple[_Stats, _Stats]:
        return self._total, self._clients.setdefault(address, _Stats())

    def _append(self, *, entry: dict[str, object]) -> None:
        self._sequence += 1
        self._log.append({"sequence": self._sequence, **entry})

    def _detail(self, *, record: RequestRecord) -> dict[str, object]:
        fields: Sequence[DecodedField] = ()
        if self._decoder is not None and record.words:
            fields = self._decoder.decode(start=record.start, words=record.words)
        return {
            "words": list(record.words),
            "fields": [
                {
                    "address": field.address,
                    "name": field.name,
                    "words": list(field.words),
                    "value": field.value,
                    "label": field.label,
                }
                for field in fields
            ],
        }
