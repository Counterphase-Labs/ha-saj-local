import pytest

from saj.hs3 import (
    Hs3Device,
    Hs3Telemetry,
    UnsupportedDeviceError,
    decode_hs3,
    identify,
    read_telemetry,
)


class FakeClient:
    def __init__(self, responses: dict[tuple[int, int], tuple[int, ...]]) -> None:
        self.responses = responses
        self.reads: list[tuple[int, int]] = []

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.reads.append((address, count))
        return self.responses[(address, count)]


def _words(text: bytes) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(text[index : index + 2], "big") for index in range(0, 20, 2)
    )


def _identity(serial: bytes = b"HS3-UNIT-0001") -> FakeClient:
    return FakeClient(
        {
            (0x8F00, 2): (0x1610, 12000),
            (0x8F03, 10): _words(serial.ljust(20, b"\0")),
        }
    )


async def test_identify_reads_hs3_metadata_without_intervening_word():
    client = _identity()

    assert await identify(client) == Hs3Device("HS3-UNIT-0001", 0x1610, 12000)
    assert client.reads == [(0x8F00, 2), (0x8F03, 10)]


async def test_identify_rejects_unsupported_type_before_serial_read():
    client = FakeClient({(0x8F00, 2): (0x1234, 1000)})

    with pytest.raises(UnsupportedDeviceError):
        await identify(client)
    assert client.reads == [(0x8F00, 2)]


@pytest.mark.parametrize(
    ("serial", "message"),
    [
        (b"\0" * 20, "Invalid serial number"),
        (b"BAD\0ID", "Invalid serial number"),
        (b"   ", "Invalid serial number"),
    ],
)
async def test_identify_rejects_empty_or_invalid_serial(serial: bytes, message: str):
    client = _identity(serial)

    with pytest.raises(ValueError, match=message):
        await identify(client)


async def test_identify_rejects_non_ascii_serial():
    client = _identity(b"\xff")

    with pytest.raises(ValueError, match="Invalid serial number encoding"):
        await identify(client)


def test_decode_preserves_signed_values_and_valid_percent():
    value = decode_hs3(
        {
            "operating_mode": 2,
            "pv_power": 3200,
            "battery_power": 0xFFFF,
            "battery_soc": 7250,
            "grid_power": 0x8000,
            "load_power": 900,
        }
    )

    assert value == Hs3Telemetry(2, 3200, -1, 72.5, -32768, 900)


@pytest.mark.parametrize("soc", [-1, 10001])
def test_decode_marks_out_of_range_battery_charge_unknown(soc: int):
    assert decode_hs3({"battery_soc": soc}).battery_soc is None


def test_decode_keeps_unknown_mode_code_for_diagnostics():
    assert decode_hs3({"operating_mode": 23}).operating_mode == 23


async def test_read_telemetry_uses_bounded_ranges_and_returns_complete_snapshot():
    client = FakeClient(
        {
            (0x4004, 1): (2,),
            (0x406F, 1): (9000,),
            (0x40A0, 1): (1500,),
            (0x40A5, 3): (2500, 500, 0xFFFE),
        }
    )
    value = await read_telemetry(client=client)

    assert client.reads == [(0x4004, 1), (0x406F, 1), (0x40A0, 1), (0x40A5, 3)]
    assert value == Hs3Telemetry(2, 2500, 500, 90, -2, 1500)


@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        ({"pv_power", "grid_power"}, [(0x40A5, 1), (0x40A7, 1)]),
        ({"battery_power", "pv_power"}, [(0x40A5, 2)]),
        (set(), []),
        ({"unknown"}, []),
    ],
)
async def test_read_telemetry_splits_runs_and_omits_disabled_values(
    enabled: set[str], expected: list[tuple[int, int]]
):
    responses = {
        (0x40A5, 1): (120,),
        (0x40A7, 1): (130,),
        (0x40A5, 2): (120, 110),
    }
    client = FakeClient(responses)
    value = await read_telemetry(client, enabled)

    assert client.reads == expected
    if enabled == {"pv_power", "grid_power"}:
        assert value.pv_power == 120
        assert value.grid_power == 130
    elif enabled == {"battery_power", "pv_power"}:
        assert value.pv_power == 120
        assert value.battery_power == 110
    else:
        assert value == Hs3Telemetry()
