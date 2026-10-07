class FakeClient:
    def __init__(self, responses: dict[tuple[int, int], tuple[int, ...]]) -> None:
        self.responses = responses
        self.reads: list[tuple[int, int]] = []

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.reads.append((address, count))
        return self.responses[(address, count)]
