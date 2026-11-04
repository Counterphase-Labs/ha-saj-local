from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import pairwise
from typing import TYPE_CHECKING

from .codec import WORD_BITS, Encoding, Range
from .definitions import (
    DEFINITIONS,
    FAMILY_BY_NAME,
    Access,
    Combination,
    Definition,
    EntityKind,
    Family,
    Operation,
    Quantity,
    Unit,
    fault_summary_key,
    fault_unrecognised_key,
)
from .models import (
    ENABLED_WITHOUT_EVIDENCE,
    ENABLING_EVIDENCE,
    Evidence,
    FunctionCode,
    Placement,
    Profile,
    Replacement,
    Shape,
)
from .profiles import PROFILES

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping, Sequence

    from .codec import BitRange, Format
    from .models import Equipment
    from .models.faults import FaultMap, Source

ASSUMED_CORE_PHASES = 1
ASSUMED_CORE_STRINGS = 2
REALTIME_SPAN = "realtime"
ENERGY_BLOCK = "energy"
SERIAL_ADDRESS = 0x8F03
SERIAL_WORD_COUNT = 10
TRIMMED_OPERATIONS = frozenset({Operation.SUM, Operation.ANY_BIT})


class CatalogueError(ValueError):
    pass


@dataclass(frozen=True)
class Fit:
    profile: Profile
    device_type: int
    equipment: frozenset[Equipment]
    pack_limit: int | None = None


@dataclass(frozen=True)
class Row:
    address: int
    words: int
    function: FunctionCode = FunctionCode.HOLDING

    @property
    def end(self) -> int:
        return self.address + self.words


@dataclass(frozen=True)
class Register:
    definition: Definition
    address: int | None
    evidence: Evidence
    core: bool
    function: FunctionCode = FunctionCode.HOLDING

    @property
    def key(self) -> str:
        return self.definition.key

    @property
    def control(self) -> bool:
        return self.definition.control

    @property
    def equipment(self) -> Equipment | None:
        return self.definition.equipment

    @property
    def words(self) -> int:
        return self.definition.word_count

    @property
    def row(self) -> Row | None:
        if self.address is None:
            return None
        return Row(address=self.address, words=self.words, function=self.function)

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
    def access(self) -> Access:
        return self.definition.access

    @property
    def writable(self) -> bool:
        return self.definition.writable

    @property
    def readable(self) -> bool:
        return self.definition.readable

    @property
    def command_value(self) -> int | None:
        return self.definition.command_value

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
    def packs(self) -> int:
        return self.definition.packs

    @property
    def exposed(self) -> bool:
        return self.definition.exposed

    @property
    def private(self) -> bool:
        return self.definition.private

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
        fault_placements, fault_definitions = _fault_rows(
            profile=profile, definitions=effective, placements=placements
        )
        placements = (*placements, *fault_placements)
        effective = {**effective, **fault_definitions}
        _require_unique_keys(placements=placements)
        registers = tuple(
            _register(placement=placement, definitions=effective, profile=profile)
            for placement in placements
        )
        _require_writable_forms(registers=registers)
        _require_write_only_forms(registers=registers)
        _require_combination_sources(registers=registers)
        _require_combination_equipment(registers=registers)
        _require_probes(profile=profile, registers=registers)
        _require_addresses(registers=registers)
        _require_no_overlap(registers=registers)
        _require_spans(profile=profile, registers=registers)
        self.registers = tuple(sorted(registers, key=_register_order))
        self.pack_maximum = max(
            (register.packs for register in self.registers), default=0
        )
        self._by_fit: dict[
            tuple[Shape, frozenset[Equipment], int | None], tuple[Register, ...]
        ] = {}

    def registers_for(
        self,
        *,
        shape: Shape,
        equipment: Collection[Equipment],
        pack_limit: int | None = None,
    ) -> tuple[Register, ...]:
        fitted = frozenset(equipment)
        selection = (shape, fitted, pack_limit)
        if selection not in self._by_fit:
            self._by_fit[selection] = _fitting(
                registers=self.registers,
                shape=shape,
                equipment=fitted,
                pack_limit=pack_limit,
            )
        return self._by_fit[selection]

    def read_registers_for(
        self,
        *,
        shape: Shape,
        equipment: Collection[Equipment],
        pack_limit: int | None = None,
    ) -> tuple[Register, ...]:
        return self._readable(
            shape=shape, equipment=equipment, pack_limit=pack_limit, readable=True
        )

    def unread_registers_for(
        self,
        *,
        equipment: Collection[Equipment],
        shape: Shape,
        pack_limit: int | None = None,
    ) -> tuple[Register, ...]:
        return self._readable(
            readable=False, equipment=equipment, shape=shape, pack_limit=pack_limit
        )

    def _readable(
        self,
        *,
        shape: Shape,
        equipment: Collection[Equipment],
        pack_limit: int | None,
        readable: bool,
    ) -> tuple[Register, ...]:
        return tuple(
            register
            for register in self.registers_for(
                shape=shape, equipment=equipment, pack_limit=pack_limit
            )
            if register.readable is readable
        )

    def rows_for(
        self, *, shape: Shape, equipment: Collection[Equipment]
    ) -> tuple[Row, ...]:
        return _rows_of(
            registers=self.read_registers_for(shape=shape, equipment=equipment)
        )

    def unread_rows_for(
        self, *, shape: Shape, equipment: Collection[Equipment]
    ) -> tuple[Row, ...]:
        return _rows_of(
            registers=self.unread_registers_for(shape=shape, equipment=equipment)
        )


def _rows_of(*, registers: Iterable[Register]) -> tuple[Row, ...]:
    rows = {register.row for register in registers if register.row is not None}
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
    if replacement.uncombined:
        definition = replace(definition, combination=None)
    if replacement.sum_of:
        definition = replace(
            definition,
            combination=Combination(
                operation=Operation.SUM, sources=replacement.sum_of
            ),
        )
    if replacement.equipment is not None:
        definition = replace(definition, equipment=replacement.equipment)
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
    combined = {
        replacement.key for replacement in profile.replacements if replacement.sum_of
    }
    return tuple(
        replace(placement, address=None) if placement.key in combined else placement
        for placement in placed
    )


def _require_unique_keys(*, placements: Iterable[Placement]) -> None:
    seen: set[str] = set()
    for placement in placements:
        if placement.key in seen:
            message = f"Duplicate key {placement.key}"
            raise CatalogueError(message)
        seen.add(placement.key)


def _register(
    *, placement: Placement, definitions: Mapping[str, Definition], profile: Profile
) -> Register:
    definition = definitions.get(placement.key)
    if definition is None:
        message = f"Address for key {placement.key} that has no definition"
        raise CatalogueError(message)
    return Register(
        definition=definition,
        address=placement.address,
        evidence=placement.evidence,
        core=definition.core
        and _enabled_by_default(definition=definition, evidence=placement.evidence),
        function=_function_at(profile=profile, address=placement.address),
    )


def _function_at(*, profile: Profile, address: int | None) -> FunctionCode:
    span = next(
        (
            span
            for span in profile.spans
            if address is not None and span.first <= address <= span.last
        ),
        None,
    )
    return FunctionCode.HOLDING if span is None else span.function


def _enabled_by_default(*, definition: Definition, evidence: Evidence) -> bool:
    return (
        definition.writable
        or evidence in ENABLING_EVIDENCE
        or definition.quantity is Quantity.PROBLEM
        or (
            definition.equipment is not None
            and definition.equipment in ENABLED_WITHOUT_EVIDENCE
        )
    )


@dataclass(frozen=True)
class _Derived:
    key: str
    combination: Combination
    evidence: Evidence


def _defined(*, key: str, definitions: Mapping[str, Definition]) -> Definition:
    definition = definitions.get(key)
    if definition is None:
        message = f"Fault key {key} has no definition"
        raise CatalogueError(message)
    return definition


def _require_fault_words(
    *,
    fault_map: FaultMap,
    definitions: Mapping[str, Definition],
    placed: Mapping[str, Placement],
) -> None:
    for key, register in fault_map.words.items():
        _defined(key=key, definitions=definitions)
        placement = placed.get(key)
        if placement is None or placement.address != register:
            message = f"Fault word {key} is not a row at {register:#06x}"
            raise CatalogueError(message)


def _require_fault_sources(
    *, fault_map: FaultMap, definitions: Mapping[str, Definition]
) -> None:
    word_of = {register: key for key, register in fault_map.words.items()}
    claimed: dict[Source, str] = {}
    for key in fault_map.named:
        definition = _defined(key=key, definitions=definitions)
        for source in fault_map.sources_of(key=key):
            word_key = word_of.get(source.register)
            if word_key is None:
                message = f"Fault {key} reports {source}, which lies in no fault word"
                raise CatalogueError(message)
            word = definitions[word_key]
            if not 0 <= source.bit < WORD_BITS * word.word_count:
                message = f"Fault {key} reports {source}, which lies outside its word"
                raise CatalogueError(message)
            if word.equipment != definition.equipment:
                message = f"Fault {key} reports {source} of another equipment"
                raise CatalogueError(message)
            if source in claimed:
                message = f"{source} is reported by both {claimed[source]} and {key}"
                raise CatalogueError(message)
            claimed[source] = key


def _fault_rows(
    *,
    profile: Profile,
    definitions: Mapping[str, Definition],
    placements: Sequence[Placement],
) -> tuple[tuple[Placement, ...], dict[str, Definition]]:
    fault_map = profile.faults
    placed = {placement.key: placement for placement in placements}
    _require_fault_words(fault_map=fault_map, definitions=definitions, placed=placed)
    _require_fault_sources(fault_map=fault_map, definitions=definitions)
    derived: list[_Derived] = []
    for equipment in dict.fromkeys(
        definitions[key].equipment for key in fault_map.words
    ):
        derived.extend(
            _derived_for(
                equipment=equipment,
                fault_map=fault_map,
                definitions=definitions,
                placements=placements,
            )
        )
    return (
        tuple(
            Placement(key=item.key, address=None, evidence=item.evidence)
            for item in derived
        ),
        {
            item.key: replace(
                _defined(key=item.key, definitions=definitions),
                combination=item.combination,
            )
            for item in derived
        },
    )


def _derived_for(
    *,
    equipment: Equipment | None,
    fault_map: FaultMap,
    definitions: Mapping[str, Definition],
    placements: Sequence[Placement],
) -> list[_Derived]:
    word_keys = tuple(
        key for key in fault_map.words if definitions[key].equipment == equipment
    )
    evidence = next(
        placement.evidence for placement in placements if placement.key == word_keys[0]
    )
    problems = tuple(
        placement.key
        for placement in placements
        if (definition := definitions.get(placement.key)) is not None
        and definition.quantity is Quantity.PROBLEM
        and definition.equipment == equipment
        and definition.combination is None
    )
    derived = [
        _Derived(
            key=fault_summary_key(equipment=equipment),
            combination=Combination(
                operation=Operation.ANY_BIT, sources=(*word_keys, *problems)
            ),
            evidence=evidence,
        ),
        _Derived(
            key=fault_unrecognised_key(equipment=equipment),
            combination=Combination(
                operation=Operation.ANY_BIT,
                sources=word_keys,
                masks={
                    key: fault_map.unmapped_mask(register=fault_map.words[key])
                    for key in word_keys
                },
            ),
            evidence=evidence,
        ),
    ]
    for key in fault_map.named:
        if definitions[key].equipment != equipment:
            continue
        involved = tuple(
            word
            for word in word_keys
            if fault_map.mask_of(key=key, register=fault_map.words[word])
        )
        derived.append(
            _Derived(
                key=key,
                combination=Combination(
                    operation=Operation.ANY_BIT,
                    sources=involved,
                    masks={
                        word: fault_map.mask_of(key=key, register=fault_map.words[word])
                        for word in involved
                    },
                ),
                evidence=evidence,
            )
        )
    return derived


def _require_writable_forms(*, registers: Iterable[Register]) -> None:
    for register in registers:
        if register.writable and not register.definition.has_writable_form:
            message = (
                f"Writable key {register.key} has no range, options"
                " or writable encoding"
            )
            raise CatalogueError(message)


def _require_write_only_forms(*, registers: Iterable[Register]) -> None:
    for register in registers:
        if register.access is not Access.WRITE_ONLY and (
            register.command_value is not None
        ):
            message = f"Command key {register.key} must be write-only"
            raise CatalogueError(message)
        if register.access is Access.WRITE_ONLY and register.field is not None:
            message = f"Write-only key {register.key} cannot be a packed field"
            raise CatalogueError(message)


def _require_combination_sources(*, registers: Sequence[Register]) -> None:
    keys = {register.key for register in registers}
    for register in registers:
        missing = [source for source in register.sources if source not in keys]
        if missing:
            message = f"Combined key {register.key} lacks sources {missing}"
            raise CatalogueError(message)


def _require_combination_equipment(*, registers: Sequence[Register]) -> None:
    by_key = {register.key: register for register in registers}
    for register in registers:
        mixed = [
            source
            for source in register.sources
            if by_key[source].equipment != register.equipment
        ]
        if mixed:
            message = (
                f"Combined key {register.key} has sources {mixed} of another equipment"
            )
            raise CatalogueError(message)


def _require_probes(*, profile: Profile, registers: Sequence[Register]) -> None:
    by_key = {register.key: register for register in registers}
    for probe in profile.probes:
        for key in probe.keys:
            register = by_key.get(key)
            if register is None:
                message = f"Probe for {probe.equipment} reads {key} that has no row"
            elif not register.readable:
                message = f"Probe for {probe.equipment} reads {key} that is unreadable"
            elif register.equipment is not None:
                message = (
                    f"Probe for {probe.equipment} reads {key} that belongs to equipment"
                )
            else:
                continue
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
        if len(sharing) > 1 and not _may_share(sharing=sharing):
            message = f"Keys {[register.key for register in sharing]} share {row}"
            raise CatalogueError(message)
    ordered = sorted(rows, key=lambda row: (row.address, row.words))
    for previous, following in pairwise(ordered):
        if following.address < previous.end:
            message = (
                f"Rows at {previous.address:#06x} and {following.address:#06x} overlap"
            )
            raise CatalogueError(message)


def _may_share(*, sharing: Sequence[Register]) -> bool:
    if all(register.field is not None for register in sharing):
        return True
    if any(register.access is not Access.WRITE_ONLY for register in sharing):
        return False
    commands = [
        register.command_value
        for register in sharing
        if register.command_value is not None
    ]
    uncommanded = len(sharing) - len(commands)
    return uncommanded <= 1 and len(set(commands)) == len(commands)


def _require_spans(*, profile: Profile, registers: Iterable[Register]) -> None:
    for register in registers:
        row = register.row
        if row is None:
            continue
        if register.readable:
            _require_readable_row(profile=profile, register=register, row=row)
        elif any(
            span.overlaps(address=row.address, words=row.words)
            for span in profile.spans
        ):
            message = (
                f"Write-only key {register.key} at {row.address:#06x}"
                " lies inside a span"
            )
            raise CatalogueError(message)


def _require_readable_row(*, profile: Profile, register: Register, row: Row) -> None:
    if not any(
        span.contains(address=row.address, words=row.words) for span in profile.spans
    ):
        message = f"Key {register.key} at {row.address:#06x} is outside every span"
        raise CatalogueError(message)
    if row.words > profile.largest_request:
        message = f"Key {register.key} is wider than the largest request"
        raise CatalogueError(message)


def _fitting(
    *,
    registers: Iterable[Register],
    shape: Shape,
    equipment: frozenset[Equipment],
    pack_limit: int | None,
) -> tuple[Register, ...]:
    fitting = [
        register
        for register in registers
        if register.definition.phases <= shape.phases
        and register.definition.strings <= shape.strings
        and (register.equipment is None or register.equipment in equipment)
        and _within_pack_limit(register=register, pack_limit=pack_limit)
    ]
    present = {register.key for register in fitting}
    return tuple(
        _for_shape(register=register, present=present, shape=shape)
        for register in fitting
        if _combination_available(register=register, present=present)
    )


def _within_pack_limit(*, register: Register, pack_limit: int | None) -> bool:
    return pack_limit is None or register.packs <= pack_limit


def _combination_available(*, register: Register, present: set[str]) -> bool:
    if register.combination is None:
        return True
    if register.combination.operation in TRIMMED_OPERATIONS:
        return any(source in present for source in register.sources)
    return all(source in present for source in register.sources)


def _for_shape(*, register: Register, present: set[str], shape: Shape) -> Register:
    updated = register
    combination = register.combination
    if combination is not None and combination.operation in TRIMMED_OPERATIONS:
        sources = tuple(source for source in register.sources if source in present)
        updated = replace(
            updated,
            definition=replace(
                register.definition,
                combination=Combination(
                    operation=combination.operation,
                    sources=sources,
                    masks={
                        source: mask
                        for source, mask in combination.masks.items()
                        if source in sources
                    },
                ),
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


def device_registers(*, fit: Fit) -> tuple[Register, ...]:
    return catalogue_of(profile=fit.profile).registers_for(
        shape=fit.profile.shape_of(device_type=fit.device_type),
        equipment=fit.equipment,
        pack_limit=fit.pack_limit,
    )


def device_read_registers(*, fit: Fit) -> tuple[Register, ...]:
    return catalogue_of(profile=fit.profile).read_registers_for(
        shape=fit.profile.shape_of(device_type=fit.device_type),
        equipment=fit.equipment,
        pack_limit=fit.pack_limit,
    )


def private_rows(*, registers: Iterable[Register]) -> frozenset[Row]:
    return frozenset(
        register.row
        for register in registers
        if register.private and register.row is not None
    ) | {Row(address=SERIAL_ADDRESS, words=SERIAL_WORD_COUNT)}


def device_unread_registers(*, fit: Fit) -> tuple[Register, ...]:
    return catalogue_of(profile=fit.profile).unread_registers_for(
        shape=fit.profile.shape_of(device_type=fit.device_type),
        equipment=fit.equipment,
        pack_limit=fit.pack_limit,
    )


def hidden_sources(*, fit: Fit, keys: Collection[str]) -> frozenset[str]:
    registers = device_read_registers(fit=fit)
    hidden = {register.key for register in registers if not register.exposed}
    return frozenset(
        source
        for register in registers
        if register.key in keys
        for source in register.sources
        if source in hidden
    )


def device_keys(*, fit: Fit) -> frozenset[str]:
    return frozenset(register.key for register in device_read_registers(fit=fit))


def absent_keys(*, fit: Fit) -> frozenset[str]:
    return frozenset(
        register.key
        for register in catalogue_of(profile=fit.profile).registers
        if (register.equipment is not None and register.equipment not in fit.equipment)
        or not _within_pack_limit(register=register, pack_limit=fit.pack_limit)
    )


def pack_maximum(*, profile: Profile) -> int:
    return catalogue_of(profile=profile).pack_maximum


def known_keys(*, profiles: Iterable[Profile]) -> frozenset[str]:
    return frozenset(
        register.key
        for profile in profiles
        for register in catalogue_of(profile=profile).registers
    )


def blocks_by_key(*, fit: Fit) -> dict[str, str]:
    registers = device_read_registers(fit=fit)
    by_key = {register.key: register for register in registers}
    placed = [
        (_placed(register=register, by_key=by_key), register) for register in registers
    ]
    placed.sort(key=lambda item: item[0].address)
    return {
        register.key: _block(profile=fit.profile, register=register, row=row)
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
