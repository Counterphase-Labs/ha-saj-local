from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .catalogue import device_read_registers
from .client import ModbusError, ModbusErrorMessage
from .codec import Value, decode
from .definitions import Combination, Operation
from .models import FunctionCode

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping, Sequence

    from .catalogue import Fit, Register, Row
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
PERCENT = 100
SHARE_DECIMALS = 1
SETUP_KEYS = frozenset(
    {OPERATING_MODE, BATTERY_SOC, LOAD_POWER, PV_POWER, BATTERY_POWER, GRID_POWER}
)


def setup_keys(device: Device) -> frozenset[str]:
    registers = device_read_registers(fit=device.fit)
    return SETUP_KEYS & {register.key for register in registers}


@dataclass(frozen=True)
class ReadRange:
    address: int
    count: int
    keys: tuple[str, ...]
    rows: tuple[Row, ...] = ()
    function: FunctionCode = FunctionCode.HOLDING


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
        function=members[0].function,
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
    pending = list(wanted)
    while pending:
        for source in by_key[pending.pop()].sources:
            if source not in wanted:
                wanted.add(source)
                pending.append(source)
    return [register for register in registers if register.key in wanted]


def _leaves_of(*, key: str, by_key: Mapping[str, Register]) -> frozenset[str]:
    sources = by_key[key].sources
    if not sources:
        return frozenset({key})
    return frozenset().union(*(_leaves_of(key=s, by_key=by_key) for s in sources))


def plan_requests(
    *,
    fit: Fit,
    enabled: Collection[str] | None = None,
    narrowing: Collection[Region] = (),
    breaks: Collection[Break] = (),
) -> list[ReadRange]:
    registers = device_read_registers(fit=fit)
    return plan_ranges(
        registers=_needed(registers, enabled),
        profile=fit.profile,
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
        fit=device.fit,
        enabled=enabled,
        narrowing=narrowing,
        breaks=breaks,
    )


def _share(*, part: float, whole: float) -> float | None:
    if whole == 0:
        return None
    return round(min(PERCENT, max(0, part / whole * PERCENT)), SHARE_DECIMALS)


def _arithmetic(*, operation: Operation, numbers: Sequence[float]) -> Value:
    if operation is Operation.DIFFERENCE:
        return numbers[0] - numbers[1]
    if operation is Operation.SHARE_PERCENT:
        return _share(part=numbers[0], whole=numbers[1])
    if operation is Operation.REMAINDER_PERCENT:
        return _share(part=numbers[0] - numbers[1], whole=numbers[0])
    return sum(numbers)


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
    if combination.operation is Operation.ESTIMATE:
        return None
    parts = [decoded[source] for source in combination.sources]
    numbers = [part for part in parts if isinstance(part, int | float)]
    if len(numbers) != len(parts):
        return None
    if combination.operation is Operation.ANY_BIT:
        return int(
            any(
                int(number) & combination.mask_of(source=source)
                for source, number in zip(combination.sources, numbers, strict=True)
            )
        )
    return _arithmetic(operation=combination.operation, numbers=numbers)


def decode_values(
    *, registers: Iterable[Register], raw: Mapping[str, Sequence[int]]
) -> dict[str, Value]:
    registers = list(registers)
    values: dict[str, Value] = {
        register.key: decode(words=raw[register.key], encoding_format=register.format)
        for register in registers
        if register.combination is None and register.key in raw
    }
    pending = [register for register in registers if register.combination is not None]
    while ready := [
        register
        for register in pending
        if register.combination is not None
        and all(
            source in values or source in raw for source in register.combination.sources
        )
    ]:
        combined = {
            register.key: _combined_value(
                register=register,
                combination=combination,
                raw=raw,
                decoded=values,
            )
            for register in ready
            if (combination := register.combination) is not None
        }
        values.update(combined)
        pending = [register for register in pending if register.key not in combined]
    return values


def _outcome_keys(
    *,
    read_range: ReadRange,
    needed: Collection[Register],
    requested: Collection[str],
) -> frozenset[str]:
    by_key = {register.key: register for register in needed}
    dependents = {
        register.key
        for register in needed
        if register.sources
        and not _leaves_of(key=register.key, by_key=by_key).isdisjoint(read_range.keys)
    }
    return frozenset((set(read_range.keys) | dependents) & set(requested))


async def _read_range(
    *, client: RegisterReader, read_range: ReadRange
) -> tuple[int, ...]:
    read = (
        client.read_input_registers
        if read_range.function is FunctionCode.INPUT
        else client.read_holding_registers
    )
    return await read(address=read_range.address, count=read_range.count)


async def read_telemetry(
    client: RegisterReader,
    device: Device,
    enabled: Collection[str] | None = None,
    narrowing: Collection[Region] = (),
    breaks: Collection[Break] = (),
) -> Readout:
    registers = device_read_registers(fit=device.fit)
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
            words = await _read_range(client=client, read_range=read_range)
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
