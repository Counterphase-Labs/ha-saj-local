import pytest

from saj.telemetry import (
    Measurement,
    ReadRange,
    Telemetry,
    decode_percent,
    decode_signed,
    decode_telemetry,
    decode_unsigned,
    plan_ranges,
    read_telemetry,
)
from tests.saj.fakes import FakeClient


class FakeProfile:
    def __init__(self, measurement_keys: set[str]) -> None:
        self.measurement_keys = frozenset(measurement_keys)


class FakeDevice:
    def __init__(self, supported: set[str]) -> None:
        self.profile = FakeProfile(supported)


def _measurement(key: str, address: int, *, scale: int = 1) -> Measurement:
    return Measurement(key=key, address=address, decoder=lambda raw: raw * scale)


DECLARED = {
    measurement.key: measurement
    for measurement in (
        _measurement("alpha", 100),
        _measurement("beta", 101, scale=10),
        _measurement("gamma", 102),
        _measurement("delta", 200),
    )
}
ALL_KEYS = set(DECLARED)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(0, 0), (1, 1), (0xFFFF, 0xFFFF)],
)
def test_unsigned_decoder_keeps_the_word(raw: int, expected: int):
    assert decode_unsigned(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(0, 0), (0x7FFF, 32767), (0x8000, -32768), (0xFFFF, -1), (0xFFFE, -2)],
)
def test_signed_decoder_applies_twos_complement(raw: int, expected: int):
    assert decode_signed(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(0, 0.0), (7250, 72.5), (10000, 100.0), (10001, None), (-1, None)],
)
def test_percent_decoder_scales_valid_values_and_rejects_out_of_range(
    raw: int, expected: float | None
):
    assert decode_percent(raw) == expected


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        (["alpha", "beta", "gamma", "delta"], [(100, 3, 3), (200, 1, 1)]),
        (["alpha", "gamma"], [(100, 1, 1), (102, 1, 1)]),
        (["gamma", "beta"], [(101, 2, 2)]),
        (["delta"], [(200, 1, 1)]),
        ([], []),
    ],
)
def test_ranges_merge_adjacent_addresses_and_split_gaps(
    keys: list[str], expected: list[tuple[int, int, int]]
):
    ranges = plan_ranges(measurements=[DECLARED[key] for key in keys])

    assert [
        (read_range.address, read_range.count, len(read_range.keys))
        for read_range in ranges
    ] == expected


def test_range_keys_follow_address_order():
    ranges = plan_ranges(measurements=[DECLARED["gamma"], DECLARED["alpha"]])

    assert ranges == [
        ReadRange(address=100, count=1, keys=("alpha",)),
        ReadRange(address=102, count=1, keys=("gamma",)),
    ]


def test_decoding_applies_each_declared_decoder():
    telemetry = decode_telemetry(raw={"alpha": 3, "beta": 4}, measurements=DECLARED)

    assert telemetry == Telemetry(values={"alpha": 3, "beta": 40})


def test_telemetry_lookup_returns_none_for_absent_key():
    telemetry = Telemetry(values={"alpha": 3, "gamma": None})

    assert telemetry.get("alpha") == 3
    assert telemetry.get("gamma") is None
    assert telemetry.get("beta") is None


@pytest.mark.parametrize(
    ("enabled", "supported", "expected_reads"),
    [
        (None, ALL_KEYS, [(100, 3), (200, 1)]),
        (ALL_KEYS, ALL_KEYS, [(100, 3), (200, 1)]),
        ({"alpha", "delta"}, ALL_KEYS, [(100, 1), (200, 1)]),
        (ALL_KEYS, {"alpha", "beta"}, [(100, 2)]),
        ({"alpha", "gamma"}, {"alpha", "beta"}, [(100, 1)]),
        ({"unknown"}, ALL_KEYS, []),
        (set(), ALL_KEYS, []),
    ],
)
async def test_read_requests_only_enabled_and_supported_measurements(
    enabled: set[str] | None,
    supported: set[str],
    expected_reads: list[tuple[int, int]],
):
    client = FakeClient(
        {
            (100, 3): (1, 2, 3),
            (100, 2): (1, 2),
            (100, 1): (1,),
            (200, 1): (9,),
        }
    )

    telemetry = await read_telemetry(
        client=client,
        device=FakeDevice(supported),
        enabled=enabled,
        measurements=DECLARED,
    )

    assert client.reads == expected_reads
    requested = ALL_KEYS if enabled is None else enabled
    assert set(telemetry.values) == requested & supported & ALL_KEYS


async def test_read_decodes_returned_words_by_key():
    client = FakeClient({(100, 3): (1, 2, 3), (200, 1): (9,)})

    telemetry = await read_telemetry(
        client=client,
        device=FakeDevice(ALL_KEYS),
        measurements=DECLARED,
    )

    assert telemetry.values == {"alpha": 1, "beta": 20, "gamma": 3, "delta": 9}
