from dataclasses import replace

import pytest

from saj.catalogue import Register, Row, device_registers
from saj.client import ModbusError, ModbusErrorMessage
from saj.codec import BitRange, Encoding
from saj.definitions import Combination, Definition, Operation, Quantity
from saj.device import Device
from saj.health import Break, Region
from saj.models import Evidence, Shape, Span
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from saj.telemetry import (
    SETUP_KEYS,
    Readout,
    ReadRange,
    RequestOutcome,
    Telemetry,
    decode_values,
    plan_ranges,
    plan_reads,
    plan_requests,
    read_telemetry,
    setup_keys,
)
from tests.profiles import profile
from tests.saj.fakes import FakeClient, MemoryClient

DEVICE_TYPE = 1
THREE_PHASES = Shape(phases=3, strings=1)


def _register(
    key: str,
    address: int,
    *,
    encoding: Encoding = Encoding.U16,
    field: BitRange | None = None,
    scale: float = 1,
) -> Register:
    return Register(
        definition=Definition(
            key=key,
            quantity=Quantity.COUNT,
            encoding=encoding,
            field=field,
            scale=scale,
        ),
        address=address,
        evidence=Evidence.VERIFIED,
        core=False,
    )


def _device(*keys: str, shape: Shape | None = None) -> Device:
    device_profile = profile(
        base=HS3, key="alpha", device_types={DEVICE_TYPE}, keys=keys, hand_verified=True
    )
    if shape is not None:
        device_profile = replace(device_profile, device_types={DEVICE_TYPE: shape})
    return Device(
        serial="SERIAL",
        device_type=DEVICE_TYPE,
        rated_power=6000,
        profile=device_profile,
        detected=True,
    )


DECLARED = {
    register.key: register
    for register in (
        _register("alpha", 100),
        _register("beta", 101),
        _register("gamma", 102),
        _register("delta", 200),
        _register("wide", 300, encoding=Encoding.U32),
        _register("after_wide", 302),
        _register("flag_a", 400, field=BitRange(first=0, last=0)),
        _register("flag_b", 400, field=BitRange(first=1, last=1)),
        _register("inside", 107),
        _register("straddler", 107, encoding=Encoding.U32),
        _register("past_edge", 109),
        _register("far", 150),
    )
}

LARGEST_REQUEST = 8
PLANNING_PROFILE = replace(
    profile(base=HS3, key="beta", device_types={DEVICE_TYPE}, hand_verified=True),
    spans=(
        Span(name="low", first=100, last=199),
        Span(name="mid", first=200, last=299),
        Span(name="high", first=300, last=499),
    ),
    largest_request=LARGEST_REQUEST,
)


def _spans(ranges: list[ReadRange]) -> list[tuple[int, int]]:
    return [(read_range.address, read_range.count) for read_range in ranges]


def _plan(
    keys: list[str],
    *,
    narrowing: list[Region] | None = None,
    breaks: list[Break] | None = None,
) -> list[tuple[int, int]]:
    return _spans(
        plan_ranges(
            registers=[DECLARED[key] for key in keys],
            profile=PLANNING_PROFILE,
            narrowing=narrowing or [],
            breaks=breaks or [],
        )
    )


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        (["alpha", "beta", "gamma", "delta"], [(100, 3), (200, 1)]),
        (["alpha", "gamma"], [(100, 3)]),
        (["gamma", "beta"], [(101, 2)]),
        (["delta"], [(200, 1)]),
        (["alpha", "inside"], [(100, LARGEST_REQUEST)]),
        (["alpha", "past_edge"], [(100, 1), (109, 1)]),
        (["alpha", "far"], [(100, 1), (150, 1)]),
        (["alpha", "straddler"], [(100, 1), (107, 2)]),
        (["alpha", "delta"], [(100, 1), (200, 1)]),
        (["wide"], [(300, 2)]),
        (["wide", "after_wide"], [(300, 3)]),
        (["after_wide", "wide"], [(300, 3)]),
        (["flag_a", "flag_b"], [(400, 1)]),
        ([], []),
    ],
)
def test_gaps_are_bridged_inside_a_span_within_the_largest_request(
    keys: list[str], expected: list[tuple[int, int]]
):
    assert _plan(keys) == expected


def test_range_keys_follow_address_order_and_a_packed_row_lists_every_field():
    ranges = plan_ranges(
        registers=[DECLARED["flag_b"], DECLARED["gamma"], DECLARED["flag_a"]],
        profile=PLANNING_PROFILE,
    )

    assert ranges == [
        ReadRange(
            address=102, count=1, keys=("gamma",), rows=(Row(address=102, words=1),)
        ),
        ReadRange(
            address=400,
            count=1,
            keys=("flag_b", "flag_a"),
            rows=(Row(address=400, words=1),),
        ),
    ]


@pytest.mark.parametrize(
    ("keys", "breaks", "expected"),
    [
        (["alpha", "gamma"], [Break(before=101, after=102)], [(100, 1), (102, 1)]),
        (["alpha", "gamma"], [Break(before=101, after=101)], [(100, 1), (102, 1)]),
        (["alpha", "gamma"], [Break(before=101, after=105)], [(100, 1), (102, 1)]),
        (
            ["alpha", "beta", "gamma"],
            [Break(before=101, after=101)],
            [(100, 1), (101, 2)],
        ),
        (["alpha", "gamma"], [Break(before=110, after=120)], [(100, 3)]),
        (["alpha", "gamma"], [Break(before=100, after=103)], [(100, 3)]),
    ],
)
def test_a_request_never_crosses_a_break(
    keys: list[str], breaks: list[Break], expected: list[tuple[int, int]]
):
    assert _plan(keys, breaks=breaks) == expected


def test_narrowed_halves_are_not_merged_with_other_rows():
    halves = [
        Region(rows=(Row(address=100, words=1),)),
        Region(rows=(Row(address=101, words=1), Row(address=102, words=1))),
    ]

    assert _plan(["alpha", "beta", "gamma"], narrowing=halves) == [(100, 1), (101, 2)]


def test_a_row_under_test_is_never_bridged_by_other_rows():
    refused = [Region(rows=(Row(address=101, words=1),))]

    assert _plan(["alpha", "gamma"], narrowing=refused) == [(100, 1), (102, 1)]


def test_a_narrowed_row_that_is_not_needed_is_not_requested():
    refused = [Region(rows=(Row(address=100, words=1), Row(address=101, words=1)))]

    assert _plan(["gamma"], narrowing=refused) == [(102, 1)]


def test_rows_of_one_region_stop_at_the_hull_of_another():
    outer_end = replace(
        DECLARED["alpha"],
        definition=replace(DECLARED["alpha"].definition, key="outer_end"),
        address=104,
    )
    outer = Region(rows=(Row(address=100, words=1), Row(address=104, words=1)))
    inner = Region(rows=(Row(address=101, words=1), Row(address=102, words=1)))

    ranges = plan_ranges(
        registers=[DECLARED["alpha"], DECLARED["beta"], DECLARED["gamma"], outer_end],
        profile=PLANNING_PROFILE,
        narrowing=[outer, inner],
    )

    assert _spans(ranges) == [(100, 1), (101, 2), (104, 1)]


SIX_ORIGINAL_KEYS = {
    "operating_mode",
    "battery_soc",
    "load_power",
    "pv_power",
    "battery_power",
    "grid_power",
}
CONTIGUOUS_POWERS = ["pv_power", "battery_power", "grid_power"]


@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        (None, [(0x4004, 1), (0x406F, 1), (0x40A0, 8)]),
        (
            {"pv_power", "grid_power", "unknown", "battery_power"},
            [(0x40A5, 3)],
        ),
        ({"operating_mode", "load_power"}, [(0x4004, 1), (0x40A0, 1)]),
        ({"unknown"}, []),
        (set(), []),
    ],
)
def test_the_read_plan_covers_enabled_keys_the_device_has(
    enabled: set[str] | None, expected: list[tuple[int, int]]
):
    device = _device(*SIX_ORIGINAL_KEYS)

    assert _spans(plan_reads(device=device, enabled=enabled)) == expected


def test_the_read_plan_leaves_out_keys_the_device_lacks():
    device = _device("pv_power", "battery_power")

    ranges = plan_reads(device=device, enabled={"pv_power", "grid_power"})

    assert _spans(ranges) == [(0x40A5, 1)]


def test_the_read_plan_honours_breaks_and_narrowing():
    device = _device(*CONTIGUOUS_POWERS)
    battery = Region(rows=(Row(address=0x40A6, words=1),))

    ranges = plan_reads(
        device=device,
        narrowing=[battery],
        breaks=[Break(before=0x40A7, after=0x40A7)],
    )

    assert _spans(ranges) == [(0x40A5, 1), (0x40A6, 1), (0x40A7, 1)]


def test_a_packed_register_is_planned_once_for_all_its_enabled_fields():
    device = _device("charge_slot_1_enabled", "charge_slot_2_enabled")

    ranges = plan_reads(device=device)

    assert ranges == [
        ReadRange(
            address=0x3604,
            count=1,
            keys=("charge_slot_1_enabled", "charge_slot_2_enabled"),
            rows=(Row(address=0x3604, words=1),),
        )
    ]


def test_a_combined_value_plans_the_rows_of_its_sources():
    device = _device(
        "parallel_pv_power",
        "parallel_pv_power_low_word",
        "parallel_pv_power_high_word",
    )

    ranges = plan_reads(device=device, enabled={"parallel_pv_power"})

    assert _spans(ranges) == [(0x4204, 9)]


def test_a_sum_plans_only_the_phases_the_device_has():
    keys = ("meter_a_power", "meter_a_l1_power", "meter_a_l2_power", "meter_a_l3_power")
    device = _device(*keys, shape=Shape(phases=2, strings=1))

    ranges = plan_reads(device=device, enabled={"meter_a_power"})

    assert _spans(ranges) == [(0xA03F, 7)]


FAST_POWER_KEYS = {"load_power", "pv_power", "battery_power", "grid_power"}
NEVER_READ = {
    HS3.key: [(0x8402, 0x8405), (0x840F, 0x8412), (0x8015, 0x8023), (0x8F02, 0x8F02)],
    H2.key: [(0x8015, 0x8023)],
}


def _shipped_selection(
    *, profile_key: str, selection: str
) -> tuple[list[ReadRange], int]:
    profile_data = HS3 if profile_key == HS3.key else H2
    device_type = next(iter(profile_data.device_types))
    registers = device_registers(profile=profile_data, device_type=device_type)
    keys = {
        "core": {register.key for register in registers if register.core},
        "every": {register.key for register in registers},
        "fast": FAST_POWER_KEYS,
    }[selection]
    ranges = plan_requests(profile=profile_data, device_type=device_type, enabled=keys)
    return ranges, profile_data.largest_request


@pytest.mark.parametrize(
    ("profile_key", "selection", "requests"),
    [
        (HS3.key, "core", 9),
        (HS3.key, "every", 36),
        (HS3.key, "fast", 1),
        (H2.key, "core", 5),
        (H2.key, "every", 11),
        (H2.key, "fast", 1),
    ],
)
def test_the_shipped_catalogues_read_in_few_requests_within_the_largest(
    profile_key: str, selection: str, requests: int
):
    ranges, largest = _shipped_selection(profile_key=profile_key, selection=selection)

    assert len(ranges) == requests
    assert max(read_range.count for read_range in ranges) <= largest


@pytest.mark.parametrize("shipped", [HS3, H2])
def test_no_request_leaves_its_span_or_touches_a_never_read_address(shipped):
    device_type = next(iter(shipped.device_types))
    ranges = plan_requests(profile=shipped, device_type=device_type)

    for read_range in ranges:
        assert any(
            span.contains(address=read_range.address, words=read_range.count)
            for span in shipped.spans
        )
        words = range(read_range.address, read_range.address + read_range.count)
        for first, last in NEVER_READ[shipped.key]:
            assert not set(words) & set(range(first, last + 1))


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        (SIX_ORIGINAL_KEYS, SIX_ORIGINAL_KEYS),
        ({"pv_power", "inverter_power"}, {"pv_power"}),
        (set(), set()),
    ],
)
def test_setup_keys_are_the_original_sensors_the_device_has(
    keys: set[str], expected: set[str]
):
    assert setup_keys(_device(*keys)) == expected
    assert expected <= SETUP_KEYS


def test_decoding_applies_each_registers_encoding_scale_and_width():
    registers = [
        _register("alpha", 100, scale=10),
        _register("wide", 300, encoding=Encoding.I32),
        _register("flag_b", 400, field=BitRange(first=1, last=1)),
    ]

    values = decode_values(
        registers=registers,
        raw={"alpha": [4], "wide": [0xFFFF, 0xFFFE], "flag_b": [0b10]},
    )

    assert values == {"alpha": 40, "wide": -2, "flag_b": 1}


def test_decoding_skips_registers_that_were_not_read():
    values = decode_values(registers=[_register("alpha", 100)], raw={})

    assert values == {}


def _combined(key: str, operation: Operation, *sources: str) -> Register:
    return Register(
        definition=Definition(
            key=key,
            quantity=Quantity.POWER,
            encoding=Encoding.I32,
            combination=Combination(operation=operation, sources=sources),
        ),
        address=None,
        evidence=Evidence.VERIFIED,
        core=False,
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ({"high": [0xFFFF], "low": [0xFFFE]}, -2),
        ({"high": [1], "low": [2]}, 65538),
        ({"high": [0], "low": [0]}, 0),
        ({"high": [1]}, None),
    ],
)
def test_two_words_combine_into_one_signed_value_most_significant_first(
    raw: dict[str, list[int]], expected: int | None
):
    combined = _combined("total", Operation.WORDS, "high", "low")

    values = decode_values(registers=[combined], raw=raw)

    assert values.get("total") == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ({"a": [5], "b": [7]}, 12),
        ({"a": [0xFFFF], "b": [7]}, 6),
        ({"a": [0xFFFF], "b": [0xFFFF]}, -2),
    ],
)
def test_a_sum_adds_the_decoded_sources(raw: dict[str, list[int]], expected: int):
    sources = [
        replace(_register(key, address, encoding=Encoding.I16))
        for key, address in (("a", 1), ("b", 2))
    ]
    total = _combined("total", Operation.SUM, "a", "b")

    values = decode_values(registers=[*sources, total], raw=raw)

    assert values["total"] == expected


def test_a_sum_is_unknown_when_a_source_is_invalid():
    sources = [
        replace(
            _register(key, address),
            definition=Definition(
                key=key,
                quantity=Quantity.COUNT,
                encoding=Encoding.U16,
                invalid=frozenset({0xFFFF}),
            ),
        )
        for key, address in (("a", 1), ("b", 2))
    ]
    total = _combined("total", Operation.SUM, "a", "b")

    values = decode_values(registers=[*sources, total], raw={"a": [1], "b": [0xFFFF]})

    assert values["total"] is None


def test_telemetry_lookup_returns_none_for_absent_key():
    telemetry = Telemetry(values={"alpha": 3, "gamma": None})

    assert telemetry.get("alpha") == 3
    assert telemetry.get("gamma") is None
    assert telemetry.get("beta") is None


def _memory(**words: int) -> dict[int, int]:
    return {int(address, 16): value for address, value in words.items()}


@pytest.mark.parametrize(
    ("enabled", "expected_reads"),
    [
        (None, [(0x4004, 1), (0x406F, 1), (0x40A0, 8)]),
        (SIX_ORIGINAL_KEYS, [(0x4004, 1), (0x406F, 1), (0x40A0, 8)]),
        ({"pv_power", "operating_mode"}, [(0x4004, 1), (0x40A5, 1)]),
        ({"unknown"}, []),
        (set(), []),
    ],
)
async def test_read_requests_only_enabled_keys_the_device_has(
    enabled: set[str] | None, expected_reads: list[tuple[int, int]]
):
    client = MemoryClient()

    telemetry = await read_telemetry(
        client=client, device=_device(*SIX_ORIGINAL_KEYS), enabled=enabled
    )

    assert client.reads == expected_reads
    requested = SIX_ORIGINAL_KEYS if enabled is None else enabled
    assert set(telemetry.values) == requested & SIX_ORIGINAL_KEYS
    assert telemetry.refusals == {}


async def test_read_decodes_returned_words_by_key_ignoring_the_gap_words():
    client = MemoryClient(
        _memory(
            **{
                "0x4004": 2,
                "0x406F": 7250,
                "0x40A0": 0xFFFF,
                "0x40A1": 999,
                "0x40A5": 10,
                "0x40A6": 0xFFF6,
                "0x40A7": 3,
            }
        )
    )

    telemetry = await read_telemetry(client=client, device=_device(*SIX_ORIGINAL_KEYS))

    assert telemetry.values == {
        "operating_mode": 2,
        "battery_soc": 72.5,
        "load_power": -1,
        "pv_power": 10,
        "battery_power": -10,
        "grid_power": 3,
    }


async def test_read_slices_each_wide_row_and_packed_field_from_its_range():
    client = MemoryClient(_memory(**{"0x3604": 0b101, "0x40BF": 1, "0x40C0": 2}))
    device = _device(
        "charge_slot_1_enabled",
        "charge_slot_2_enabled",
        "charge_slot_3_enabled",
        "pv_energy_today",
    )

    telemetry = await read_telemetry(client=client, device=device)

    assert telemetry.values == {
        "charge_slot_1_enabled": 1,
        "charge_slot_2_enabled": 0,
        "charge_slot_3_enabled": 1,
        "pv_energy_today": 655.38,
    }


PARALLEL_KEYS = (
    "parallel_pv_power",
    "parallel_pv_power_low_word",
    "parallel_pv_power_high_word",
)


async def test_read_combines_sources_and_reports_only_the_requested_keys():
    client = MemoryClient(_memory(**{"0x4204": 2, "0x420C": 1}))

    telemetry = await read_telemetry(
        client=client, device=_device(*PARALLEL_KEYS), enabled={"parallel_pv_power"}
    )

    assert client.reads == [(0x4204, 9)]
    assert telemetry.values == {"parallel_pv_power": 65538}


async def test_narrowed_regions_and_breaks_shape_the_requests_made():
    client = MemoryClient()
    device = _device(*CONTIGUOUS_POWERS)

    await read_telemetry(
        client=client,
        device=device,
        narrowing=[Region(rows=(Row(address=0x40A5, words=1),))],
        breaks=[Break(before=0x40A7, after=0x40A7)],
    )

    assert client.reads == [(0x40A5, 1), (0x40A6, 1), (0x40A7, 1)]


@pytest.mark.parametrize("code", [0, 1, 2, 3, 5, 0x0B, 0x7F])
async def test_a_refused_request_yields_refusals_and_the_rest_is_still_read(
    code: int,
):
    client = MemoryClient(
        _memory(**{"0x4004": 2}), bad_addresses=frozenset({0x40A6}), code=code
    )

    telemetry = await read_telemetry(
        client=client, device=_device("operating_mode", *CONTIGUOUS_POWERS)
    )

    assert client.reads == [(0x4004, 1), (0x40A5, 3)]
    assert telemetry.values == {"operating_mode": 2}
    assert telemetry.refusals == dict.fromkeys(CONTIGUOUS_POWERS, code)


async def test_each_request_reports_its_rows_keys_and_refusal_code():
    client = MemoryClient(bad_addresses=frozenset({0x4004}), code=3)

    telemetry = await read_telemetry(
        client=client, device=_device("operating_mode", *CONTIGUOUS_POWERS)
    )

    assert telemetry.outcomes == (
        RequestOutcome(
            rows=(Row(address=0x4004, words=1),),
            keys=frozenset({"operating_mode"}),
            code=3,
        ),
        RequestOutcome(
            rows=tuple(Row(address=0x40A5 + offset, words=1) for offset in range(3)),
            keys=frozenset(CONTIGUOUS_POWERS),
            code=None,
        ),
    )


async def test_a_combined_value_is_refused_with_its_refused_source():
    client = MemoryClient(bad_addresses=frozenset({0x4204}))

    telemetry = await read_telemetry(
        client=client, device=_device(*PARALLEL_KEYS), enabled={"parallel_pv_power"}
    )

    assert telemetry.values == {}
    assert telemetry.refusals == {"parallel_pv_power": 2}


@pytest.mark.parametrize(
    "failure",
    [
        ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=4),
        ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=6),
        ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT),
        ModbusError(ModbusErrorMessage.MALFORMED_REGISTERS),
    ],
)
async def test_busy_device_failure_and_link_errors_stop_the_read(failure: ModbusError):
    client = FakeClient({(0x4004, 1): failure, (0x40A5, 3): (1, 2, 3)})

    with pytest.raises(ModbusError) as caught:
        await read_telemetry(
            client=client, device=_device("operating_mode", *CONTIGUOUS_POWERS)
        )

    assert caught.value is failure
    assert client.reads == [(0x4004, 1)]


def test_a_readout_without_refusals_is_complete():
    Readout(values={"alpha": 1}, refusals={}).require_complete()


def test_an_incomplete_readout_reports_the_refusal_code():
    readout = Readout(values={}, refusals={"alpha": 0, "beta": 2})

    with pytest.raises(ModbusError) as caught:
        readout.require_complete()

    assert caught.value.exception_code == 0


WRITE_ONLY_KEYS = {"ems_grid_power_target", "ems_pv_power_limit", "clear_fault_history"}


@pytest.mark.parametrize(
    ("enabled", "planned"),
    [
        (None, [("pv_power",)]),
        (WRITE_ONLY_KEYS, []),
        (WRITE_ONLY_KEYS | {"pv_power"}, [("pv_power",)]),
        ({"ems_grid_power_target"}, []),
    ],
)
def test_an_enabled_write_only_key_is_never_planned_for_reading(
    enabled: set[str] | None, planned: list[tuple[str, ...]]
):
    device = _device("pv_power", *WRITE_ONLY_KEYS)

    assert [r.keys for r in plan_reads(device, enabled)] == planned


@pytest.mark.parametrize("enabled", [None, WRITE_ONLY_KEYS | {"pv_power"}])
async def test_an_enabled_write_only_key_causes_no_read_request(
    enabled: set[str] | None,
):
    client = MemoryClient()
    device = _device("pv_power", *WRITE_ONLY_KEYS)

    telemetry = await read_telemetry(client=client, device=device, enabled=enabled)

    assert client.reads == [(0x40A5, 1)]
    assert set(telemetry.values) == {"pv_power"}


async def test_only_write_only_keys_enabled_means_nothing_is_read():
    client = MemoryClient()

    telemetry = await read_telemetry(
        client=client, device=_device(*WRITE_ONLY_KEYS), enabled=WRITE_ONLY_KEYS
    )

    assert client.reads == []
    assert telemetry.values == {}
