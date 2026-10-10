from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .catalogue import device_registers
from .client import ModbusError, ModbusErrorMessage
from .codec import Value, decode
from .definitions import Combination, Operation

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping, Sequence

    from .catalogue import Register, Row
    from .client import RegisterReader
    from .device import Device
    from .health import Break, Region
    from .models import Profile

OPERATING_MODE = "operating_mode"
BATTERY_SOC = "battery_soc"
LOAD_POWER = "load_power"
PV_POWER = "pv_power"
BATTERY_POWER = "battery_power"
GRID_POWER = "grid_power"
SETUP_KEYS = frozenset(
    {OPERATING_MODE, BATTERY_SOC, LOAD_POWER, PV_POWER, BATTERY_POWER, GRID_POWER}
)


def setup_keys(device: Device) -> frozenset[str]:
    registers = device_registers(profile=device.profile, device_type=device.device_type)
    return SETUP_KEYS & {register.key for register in registers}


@dataclass(frozen=True)
class ReadRange:
    address: int
    count: int
    keys: tuple[str, ...]
    rows: tuple[Row, ...] = ()


@dataclass(frozen=True)
class Telemetry:
    values: Mapping[str, Value]

    def get(self, key: str) -> Value:
        return self.values.get(key)


@dataclass(frozen=True)
class RequestOutcome:
    rows: tuple[Row, ...]
    keys: frozenset[str]
    code: int | None


@dataclass(frozen=True)
class Readout:
    values: Mapping[str, Value]
    refusals: Mapping[str, int]
    outcomes: tuple[RequestOutcome, ...] = ()

    def require_complete(self) -> None:
        if self.refusals:
            raise ModbusError(
                ModbusErrorMessage.EXCEPTION_RESPONSE,
                exception_code=next(iter(self.refusals.values())),
            )


def _keys_by_row(registers: Iterable[Register]) -> dict[Row, tuple[str, ...]]:
    keys_by_row: dict[Row, list[str]] = {}
    for register in registers:
        if register.row is not None:
            keys_by_row.setdefault(register.row, []).append(register.key)
    return {
        row: tuple(keys_by_row[row])
        for row in sorted(keys_by_row, key=lambda row: (row.address, row.words))
    }


def _fits(*, profile: Profile, blocks: Iterable[Break], start: int, end: int) -> bool:
    return (
        end - start <= profile.largest_request
        and any(
            span.contains(address=start, words=end - start) for span in profile.spans
        )
        and not any(block.crossed_by(start=start, end=end) for block in blocks)
    )


def _request(
    *, members: Sequence[Row], keys_by_row: Mapping[Row, tuple[str, ...]]
) -> ReadRange:
    return ReadRange(
        address=members[0].address,
        count=members[-1].end - members[0].address,
        keys=tuple(key for row in members for key in keys_by_row[row]),
        rows=tuple(members),
    )


def _pack(
    *,
    rows: Iterable[Row],
    keys_by_row: Mapping[Row, tuple[str, ...]],
    profile: Profile,
    blocks: Collection[Break],
) -> list[ReadRange]:
    ranges: list[ReadRange] = []
    members: list[Row] = []
    for row in sorted(rows, key=lambda row: (row.address, row.words)):
        if members and _fits(
            profile=profile, blocks=blocks, start=members[0].address, end=row.end
        ):
            members.append(row)
            continue
        if members:
            ranges.append(_request(members=members, keys_by_row=keys_by_row))
        members = [row]
    if members:
        ranges.append(_request(members=members, keys_by_row=keys_by_row))
    return ranges


def plan_ranges(
    *,
    registers: Iterable[Register],
    profile: Profile,
    narrowing: Collection[Region] = (),
    breaks: Collection[Break] = (),
) -> list[ReadRange]:
    keys_by_row = _keys_by_row(registers)
    regions = tuple(narrowing)
    ranges: list[ReadRange] = []
    claimed: set[Row] = set()
    for region in regions:
        rows = [row for row in region.rows if row in keys_by_row]
        claimed.update(rows)
        others = [other.hull for other in regions if other is not region]
        ranges.extend(
            _pack(
                rows=rows,
                keys_by_row=keys_by_row,
                profile=profile,
                blocks=[*breaks, *others],
            )
        )
    ranges.extend(
        _pack(
            rows=[row for row in keys_by_row if row not in claimed],
            keys_by_row=keys_by_row,
            profile=profile,
            blocks=[*breaks, *(region.hull for region in regions)],
        )
    )
    return sorted(ranges, key=lambda read_range: read_range.address)


def _needed(
    registers: Sequence[Register], enabled: Collection[str] | None
) -> list[Register]:
    by_key = {register.key: register for register in registers}
    wanted = set(by_key) if enabled is None else set(enabled) & set(by_key)
    for key in tuple(wanted):
        wanted.update(by_key[key].sources)
    return [register for register in registers if register.key in wanted]


def plan_requests(
    *,
    profile: Profile,
    device_type: int,
    enabled: Collection[str] | None = None,
    narrowing: Collection[Region] = (),
    breaks: Collection[Break] = (),
) -> list[ReadRange]:
    registers = device_registers(profile=profile, device_type=device_type)
    return plan_ranges(
        registers=_needed(registers, enabled),
        profile=profile,
        narrowing=narrowing,
        breaks=breaks,
    )


def plan_reads(
    device: Device,
    enabled: Collection[str] | None = None,
    narrowing: Collection[Region] = (),
    breaks: Collection[Break] = (),
) -> list[ReadRange]:
    return plan_requests(
        profile=device.profile,
        device_type=device.device_type,
        enabled=enabled,
        narrowing=narrowing,
        breaks=breaks,
    )


def _combined_value(
    *,
    register: Register,
    combination: Combination,
    raw: Mapping[str, Sequence[int]],
    decoded: Mapping[str, Value],
) -> Value:
    if combination.operation is Operation.WORDS:
        words = [word for source in combination.sources for word in raw[source]]
        return decode(words=words, encoding_format=register.format)
    parts = [decoded[source] for source in combination.sources]
    numbers = [part for part in parts if isinstance(part, int | float)]
    return sum(numbers) if len(numbers) == len(parts) else None


def decode_values(
    *, registers: Iterable[Register], raw: Mapping[str, Sequence[int]]
) -> dict[str, Value]:
    registers = list(registers)
    decoded = {
        register.key: decode(words=raw[register.key], encoding_format=register.format)
        for register in registers
        if register.combination is None and register.key in raw
    }
    combined = {
        register.key: _combined_value(
            register=register, combination=combination, raw=raw, decoded=decoded
        )
        for register in registers
        if (combination := register.combination) is not None
        and all(source in raw for source in combination.sources)
    }
    return {**decoded, **combined}


def _outcome_keys(
    *,
    read_range: ReadRange,
    needed: Iterable[Register],
    requested: Collection[str],
) -> frozenset[str]:
    dependents = {
        register.key
        for register in needed
        if any(source in read_range.keys for source in register.sources)
    }
    return frozenset((set(read_range.keys) | dependents) & set(requested))


async def read_telemetry(
    client: RegisterReader,
    device: Device,
    enabled: Collection[str] | None = None,
    narrowing: Collection[Region] = (),
    breaks: Collection[Break] = (),
) -> Readout:
    registers = device_registers(profile=device.profile, device_type=device.device_type)
    needed = _needed(registers, enabled)
    by_key = {register.key: register for register in needed}
    requested = set(by_key) if enabled is None else set(enabled)
    raw: dict[str, Sequence[int]] = {}
    refusals: dict[str, int] = {}
    outcomes: list[RequestOutcome] = []
    for read_range in plan_ranges(
        registers=needed,
        profile=device.profile,
        narrowing=narrowing,
        breaks=breaks,
    ):
        code: int | None = None
        try:
            words = await client.read_holding_registers(
                address=read_range.address, count=read_range.count
            )
        except ModbusError as err:
            if err.exception_code is None or err.device_unavailable:
                raise
            code = err.exception_code
        else:
            for key in read_range.keys:
                register = by_key[key]
                start = (register.address or 0) - read_range.address
                raw[key] = words[start : start + register.words]
        keys = _outcome_keys(read_range=read_range, needed=needed, requested=requested)
        outcomes.append(RequestOutcome(rows=read_range.rows, keys=keys, code=code))
        if code is not None:
            for key in sorted(keys):
                refusals.setdefault(key, code)
    return Readout(
        values={
            key: value
            for key, value in decode_values(registers=needed, raw=raw).items()
            if key in requested
        },
        refusals=refusals,
        outcomes=tuple(outcomes),
    )
