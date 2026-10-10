from saj.client import ModbusError, ModbusErrorMessage


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

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.reads.append((address, count))
        if self.bad_addresses & set(range(address, address + count)):
            raise ModbusError(
                ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=self.code
            )
        return tuple(
            self.memory.get(word, 0) for word in range(address, address + count)
        )
