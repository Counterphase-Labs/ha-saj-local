from __future__ import annotations

from typing import TYPE_CHECKING

from saj.client import ModbusError, ModbusErrorMessage

if TYPE_CHECKING:
    from collections.abc import Sequence


class FakeClient:
    def __init__(
        self, responses: dict[tuple[int, int], tuple[int, ...] | Exception]
    ) -> None:
        self.responses = responses
        self.reads: list[tuple[int, int]] = []

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.reads.append((address, count))
        response = self.responses[(address, count)]
        if isinstance(response, Exception):
            raise response
        return response


class MemoryClient:
    def __init__(
        self,
        memory: dict[int, int] | None = None,
        *,
        bad_addresses: frozenset[int] = frozenset(),
        code: int = 2,
    ) -> None:
        self.memory = memory or {}
        self.bad_addresses = bad_addresses
        self.code = code
        self.reads: list[tuple[int, int]] = []
        self.input_reads: list[tuple[int, int]] = []

    async def read_input_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.input_reads.append((address, count))
        return await self._answer(address=address, count=count)

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.reads.append((address, count))
        return await self._answer(address=address, count=count)

    async def _answer(self, *, address: int, count: int) -> tuple[int, ...]:
        if self.bad_addresses & set(range(address, address + count)):
            raise ModbusError(
                ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=self.code
            )
        return tuple(
            self.memory.get(word, 0) for word in range(address, address + count)
        )


class WritableClient:
    def __init__(
        self,
        memory: dict[int, int] | None = None,
        *,
        connected: bool = True,
        failures: dict[int, Exception] | None = None,
        applies_writes: bool = True,
    ) -> None:
        self.memory = memory or {}
        self.connected = connected
        self.failures = failures or {}
        self.applies_writes = applies_writes
        self.requests: list[tuple[str, int, tuple[int, ...]]] = []
        self.on_write = lambda: None

    @property
    def reads(self) -> list[tuple[int, int]]:
        return [
            (address, len(words))
            for kind, address, words in self.requests
            if kind == "read"
        ]

    @property
    def writes(self) -> list[tuple[str, int, tuple[int, ...]]]:
        return [request for request in self.requests if request[0] != "read"]

    def is_connected(self) -> bool:
        return self.connected

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self._record("read", address, (0,) * count)
        return tuple(
            self.memory.get(word, 0) for word in range(address, address + count)
        )

    async def write_single_register(self, address: int, value: int) -> None:
        self._record("single", address, (value,))
        self._apply(address, (value,))

    async def write_multiple_registers(
        self, address: int, values: Sequence[int]
    ) -> None:
        self._record("multiple", address, tuple(values))
        self._apply(address, tuple(values))

    def _record(self, kind: str, address: int, words: tuple[int, ...]) -> None:
        self.requests.append((kind, address, words))
        failure = self.failures.get(len(self.requests))
        if failure is not None:
            raise failure

    def _apply(self, address: int, words: tuple[int, ...]) -> None:
        if self.applies_writes:
            self.memory.update(
                {address + offset: word for offset, word in enumerate(words)}
            )
        self.on_write()
