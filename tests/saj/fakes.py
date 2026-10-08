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
