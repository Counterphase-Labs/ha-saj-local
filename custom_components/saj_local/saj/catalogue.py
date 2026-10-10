from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import pairwise
from typing import TYPE_CHECKING

from .codec import Encoding, Range
from .definitions import (
    DEFINITIONS,
    FAMILY_BY_NAME,
    Combination,
    Definition,
    EntityKind,
    Family,
    Operation,
    Quantity,
    Unit,
)
from .models import ENABLING_EVIDENCE, Evidence, Placement, Profile, Replacement, Shape
from .profiles import PROFILES

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from .codec import BitRange, Format

ASSUMED_CORE_PHASES = 1
ASSUMED_CORE_STRINGS = 2
REALTIME_SPAN = "realtime"
ENERGY_BLOCK = "energy"


class CatalogueError(ValueError):
    pass


@dataclass(frozen=True)
class Row:
    address: int
    words: int

    @property
    def end(self) -> int:
        return self.address + self.words


@dataclass(frozen=True)
class Register:
    definition: Definition
    address: int | None
    evidence: Evidence
    core: bool

    @property
    def key(self) -> str:
        return self.definition.key

    @property
    def words(self) -> int:
        return self.definition.word_count

    @property
    def row(self) -> Row | None:
        if self.address is None:
            return None
        return Row(address=self.address, words=self.words)

    @property
    def encoding(self) -> Encoding:
        return self.definition.encoding

    @property
    def format(self) -> Format:
        return self.definition.format

    @property
    def scale(self) -> float:
        return self.definition.scale

    @property
    def quantity(self) -> Quantity:
        return self.definition.quantity

    @property
    def unit(self) -> Unit | None:
        return self.definition.unit

    @property
    def kind(self) -> EntityKind:
        return self.definition.kind

    @property
    def writable(self) -> bool:
        return self.definition.writable

    @property
    def range(self) -> Range | None:
        return self.definition.range

    @property
    def options(self) -> Mapping[int, str] | None:
        return self.definition.options

    @property
    def field(self) -> BitRange | None:
        return self.definition.field

    @property
    def combination(self) -> Combination | None:
        return self.definition.combination

    @property
    def sources(self) -> tuple[str, ...]:
        if self.definition.combination is None:
            return ()
        return self.definition.combination.sources


class Catalogue:
    def __init__(
        self,
        *,
        profile: Profile,
        definitions: Sequence[Definition] = DEFINITIONS,
        families: Mapping[str, Family] = FAMILY_BY_NAME,
    ) -> None:
        self.profile = profile
        by_key = _definitions_by_key(definitions=definitions)
        effective = _apply_replacements(profile=profile, definitions=by_key)
        placements = _placements(profile=profile, families=families)
        _require_unique_keys(placements=placements)
        registers = tuple(
            _register(placement=placement, definitions=effective)
            for placement in placements
        )
        _require_writable_forms(registers=registers)
        _require_combination_sources(registers=registers)
        _require_addresses(registers=registers)
        _require_no_overlap(registers=registers)
        _require_spans(profile=profile, registers=registers)
        self.registers = tuple(sorted(registers, key=_register_order))
        self._by_shape: dict[Shape, tuple[Register, ...]] = {}

    def registers_for(self, *, shape: Shape) -> tuple[Register, ...]:
        if shape not in self._by_shape:
            self._by_shape[shape] = _fitting(registers=self.registers, shape=shape)
        return self._by_shape[shape]

    def rows_for(self, *, shape: Shape) -> tuple[Row, ...]:
        rows = {
            register.row
            for register in self.registers_for(shape=shape)
            if register.row is not None
        }
        return tuple(sorted(rows, key=lambda row: (row.address, row.words)))


def _definitions_by_key(*, definitions: Sequence[Definition]) -> dict[str, Definition]:
    by_key: dict[str, Definition] = {}
    for definition in definitions:
        if definition.key in by_key:
            message = f"Duplicate definition for key {definition.key}"
            raise CatalogueError(message)
        by_key[definition.key] = definition
    return by_key


def _apply_replacements(
    *, profile: Profile, definitions: Mapping[str, Definition]
) -> dict[str, Definition]:
    effective = dict(definitions)
    for replacement in profile.replacements:
        original = effective.get(replacement.key)
        if original is None:
            message = f"Replacement for key {replacement.key} that has no definition"
            raise CatalogueError(message)
        effective[replacement.key] = _replaced(
            original=original, replacement=replacement
        )
    return effective


def _replaced(*, original: Definition, replacement: Replacement) -> Definition:
    definition = original
    if replacement.range is not None:
        minimum, maximum = replacement.range
        definition = replace(definition, range=Range(minimum=minimum, maximum=maximum))
    if replacement.options is not None:
        definition = replace(definition, options=replacement.options)
    if replacement.encoding is not None:
        definition = replace(definition, encoding=Encoding(replacement.encoding))
    if replacement.scale is not None:
        definition = replace(definition, scale=replacement.scale)
    return definition


def _placements(
    *, profile: Profile, families: Mapping[str, Family]
) -> tuple[Placement, ...]:
    placed = list(profile.placements)
    for use in profile.families:
        family = families.get(use.family)
        if family is None:
            message = f"Unknown family {use.family}"
            raise CatalogueError(message)
        if use.count is not None:
            family = replace(family, count=use.count)
        if use.base is not None:
            family = replace(family, base=use.base)
        placed.extend(
            Placement(
                key=key,
                address=address,
                evidence=use.exceptions.get(key, use.evidence),
            )
            for key, address in family.addresses()
        )
    return tuple(placed)


def _require_unique_keys(*, placements: Iterable[Placement]) -> None:
    seen: set[str] = set()
    for placement in placements:
        if placement.key in seen:
            message = f"Duplicate key {placement.key}"
            raise CatalogueError(message)
        seen.add(placement.key)


def _register(
    *, placement: Placement, definitions: Mapping[str, Definition]
) -> Register:
    definition = definitions.get(placement.key)
    if definition is None:
        message = f"Address for key {placement.key} that has no definition"
        raise CatalogueError(message)
    return Register(
        definition=definition,
        address=placement.address,
        evidence=placement.evidence,
        core=definition.core and placement.evidence in ENABLING_EVIDENCE,
    )


def _require_writable_forms(*, registers: Iterable[Register]) -> None:
    for register in registers:
        if register.writable and not register.definition.has_writable_form:
            message = (
                f"Writable key {register.key} has no range, options"
                " or writable encoding"
            )
            raise CatalogueError(message)


def _require_combination_sources(*, registers: Sequence[Register]) -> None:
    keys = {register.key for register in registers}
    for register in registers:
        missing = [source for source in register.sources if source not in keys]
        if missing:
            message = f"Combined key {register.key} lacks sources {missing}"
            raise CatalogueError(message)


def _require_addresses(*, registers: Iterable[Register]) -> None:
    for register in registers:
        if (register.address is None) != (register.combination is not None):
            message = (
                f"Key {register.key} must have an address unless it is combined,"
                " and a combined key must not have one"
            )
            raise CatalogueError(message)


def _register_order(register: Register) -> tuple[bool, int, int, str]:
    return (
        register.address is None,
        register.address or 0,
        register.field.first if register.field is not None else 0,
        register.key,
    )


def _require_no_overlap(*, registers: Iterable[Register]) -> None:
    rows: dict[Row, list[Register]] = {}
    for register in registers:
        if register.row is not None:
            rows.setdefault(register.row, []).append(register)
    for row, sharing in rows.items():
        if len(sharing) > 1 and any(register.field is None for register in sharing):
            message = f"Keys {[register.key for register in sharing]} share {row}"
            raise CatalogueError(message)
    ordered = sorted(rows, key=lambda row: (row.address, row.words))
    for previous, following in pairwise(ordered):
        if following.address < previous.end:
            message = (
                f"Rows at {previous.address:#06x} and {following.address:#06x} overlap"
            )
            raise CatalogueError(message)


def _require_spans(*, profile: Profile, registers: Iterable[Register]) -> None:
    for register in registers:
        row = register.row
        if row is None:
            continue
        if not any(
            span.contains(address=row.address, words=row.words)
            for span in profile.spans
        ):
            message = f"Key {register.key} at {row.address:#06x} is outside every span"
            raise CatalogueError(message)
        if row.words > profile.largest_request:
            message = f"Key {register.key} is wider than the largest request"
            raise CatalogueError(message)


def _fitting(*, registers: Iterable[Register], shape: Shape) -> tuple[Register, ...]:
    fitting = [
        register
        for register in registers
        if register.definition.phases <= shape.phases
        and register.definition.strings <= shape.strings
    ]
    present = {register.key for register in fitting}
    return tuple(
        _for_shape(register=register, present=present, shape=shape)
        for register in fitting
        if _combination_available(register=register, present=present)
    )


def _combination_available(*, register: Register, present: set[str]) -> bool:
    if register.combination is None:
        return True
    if register.combination.operation is Operation.SUM:
        return any(source in present for source in register.sources)
    return all(source in present for source in register.sources)


def _for_shape(*, register: Register, present: set[str], shape: Shape) -> Register:
    updated = register
    if (
        register.combination is not None
        and register.combination.operation is Operation.SUM
    ):
        sources = tuple(source for source in register.sources if source in present)
        updated = replace(
            updated,
            definition=replace(
                register.definition,
                combination=Combination(operation=Operation.SUM, sources=sources),
            ),
        )
    if shape.assumed and (
        register.definition.phases > ASSUMED_CORE_PHASES
        or register.definition.strings > ASSUMED_CORE_STRINGS
    ):
        updated = replace(updated, core=False)
    return updated


CATALOGUES: Mapping[str, Catalogue] = {
    profile.key: Catalogue(profile=profile) for profile in PROFILES
}


def catalogue_of(*, profile: Profile) -> Catalogue:
    shipped = CATALOGUES.get(profile.key)
    if shipped is not None and shipped.profile is profile:
        return shipped
    return Catalogue(profile=profile)


def device_registers(*, profile: Profile, device_type: int) -> tuple[Register, ...]:
    return catalogue_of(profile=profile).registers_for(
        shape=profile.shape_of(device_type=device_type)
    )


def device_keys(*, profile: Profile, device_type: int) -> frozenset[str]:
    return frozenset(
        register.key
        for register in device_registers(profile=profile, device_type=device_type)
    )


def known_keys(*, profiles: Iterable[Profile]) -> frozenset[str]:
    return frozenset(
        register.key
        for profile in profiles
        for register in catalogue_of(profile=profile).registers
    )


def blocks_by_key(*, profile: Profile, device_type: int) -> dict[str, str]:
    registers = device_registers(profile=profile, device_type=device_type)
    by_key = {register.key: register for register in registers}
    placed = [
        (_placed(register=register, by_key=by_key), register) for register in registers
    ]
    placed.sort(key=lambda item: item[0].address)
    return {
        register.key: _block(profile=profile, register=register, row=row)
        for row, register in placed
    }


def _placed(*, register: Register, by_key: Mapping[str, Register]) -> Row:
    row = register.row
    if row is not None:
        return row
    rows = (by_key[source].row for source in register.sources)
    return min((row for row in rows if row is not None), key=lambda row: row.address)


def _block(*, profile: Profile, register: Register, row: Row) -> str:
    span = next(
        span
        for span in profile.spans
        if span.contains(address=row.address, words=row.words)
    )
    if span.name == REALTIME_SPAN and register.quantity is Quantity.ENERGY:
        return ENERGY_BLOCK
    return span.name
