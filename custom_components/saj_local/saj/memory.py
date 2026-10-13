from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from itertools import groupby
from typing import TYPE_CHECKING

from .catalogue import Row, device_registers, private_rows

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Sequence

    from .catalogue import Fit, Register


class FailureOutcome(StrEnum):
    EXCEPTION = "exception"
    TIMEOUT = "timeout"
    CONNECTION_LOST = "connection_lost"
    MALFORMED_REPLY = "malformed_reply"


@dataclass(frozen=True)
class RegisterEntry:
    address: int
    key: str | None
    words: tuple[int, ...]
    private: bool
    age_seconds: float


@dataclass(frozen=True)
class FailureEntry:
    address: int
    count: int
    outcome: FailureOutcome
    exception_code: int | None
    age_seconds: float


@dataclass(frozen=True)
class Snapshot:
    registers: tuple[RegisterEntry, ...]
    failed: tuple[FailureEntry, ...]


@dataclass(frozen=True)
class _Remembered:
    value: int
    read_at: float


@dataclass(frozen=True)
class _Failure:
    outcome: FailureOutcome
    exception_code: int | None
    failed_at: float


class RegisterMemory:
    def __init__(self, *, clock: Callable[[], float]) -> None:
        self._clock = clock
        self._words: dict[int, _Remembered] = {}
        self._failures: dict[tuple[int, int], _Failure] = {}
        self._paused = 0

    @contextmanager
    def paused(self) -> Iterator[None]:
        self._paused += 1
        try:
            yield
        finally:
            self._paused -= 1

    def record_answer(self, *, address: int, words: Sequence[int]) -> None:
        if self._paused:
            return
        read_at = self._clock()
        for offset, value in enumerate(words):
            self._words[address + offset] = _Remembered(value=value, read_at=read_at)
        self._failures.pop((address, len(words)), None)

    def record_failure(
        self,
        *,
        address: int,
        count: int,
        outcome: FailureOutcome,
        exception_code: int | None = None,
    ) -> None:
        if self._paused:
            return
        self._failures[(address, count)] = _Failure(
            outcome=outcome, exception_code=exception_code, failed_at=self._clock()
        )

    def snapshot(self, *, fit: Fit) -> Snapshot:
        now = self._clock()
        registers = device_registers(fit=fit)
        hidden = private_rows(registers=registers)
        private_addresses = {
            address for row in hidden for address in range(row.address, row.end)
        }
        owners = _row_keys(registers=registers, private_rows=hidden)
        row_of = {
            address: row for row in owners for address in range(row.address, row.end)
        }
        grouped: dict[Row | None, list[int]] = {}
        for address in sorted(self._words):
            grouped.setdefault(row_of.get(address), []).append(address)
        entries: list[RegisterEntry] = []
        for row, addresses in grouped.items():
            runs = (
                [[address] for address in addresses]
                if row is None
                else _contiguous(addresses=addresses)
            )
            entries.extend(
                self._entry(
                    run=run,
                    key=None if row is None else owners[row],
                    private=any(address in private_addresses for address in run),
                    now=now,
                )
                for run in runs
            )
        return Snapshot(
            registers=tuple(sorted(entries, key=lambda entry: entry.address)),
            failed=tuple(
                FailureEntry(
                    address=address,
                    count=count,
                    outcome=failure.outcome,
                    exception_code=failure.exception_code,
                    age_seconds=now - failure.failed_at,
                )
                for (address, count), failure in sorted(self._failures.items())
            ),
        )

    def _entry(
        self, *, run: Sequence[int], key: str | None, private: bool, now: float
    ) -> RegisterEntry:
        return RegisterEntry(
            address=run[0],
            key=key,
            words=() if private else tuple(self._words[a].value for a in run),
            private=private,
            age_seconds=now - min(self._words[a].read_at for a in run),
        )


def _row_keys(
    *, registers: Iterable[Register], private_rows: frozenset[Row]
) -> dict[Row, str | None]:
    keys: dict[Row, str | None] = {}
    for register in registers:
        if register.row is not None:
            keys.setdefault(register.row, register.key)
    for row in private_rows:
        keys.setdefault(row, None)
    return keys


def _contiguous(*, addresses: Sequence[int]) -> list[list[int]]:
    return [
        [address for _, address in run]
        for _, run in groupby(enumerate(addresses), key=lambda item: item[1] - item[0])
    ]
