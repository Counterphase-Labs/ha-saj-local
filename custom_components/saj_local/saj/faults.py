from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models.faults import FAULT_WORD_BITS, FaultMap, Source

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass(frozen=True)
class Decoded:
    active: frozenset[str]
    unrecognised: frozenset[Source]


def _set_bits(*, words: Mapping[int, int]) -> frozenset[Source]:
    return frozenset(
        Source(register=register, bit=bit)
        for register, value in words.items()
        for bit in range(FAULT_WORD_BITS)
        if value >> bit & 1
    )


def _decoded(*, fault_map: FaultMap, bits: frozenset[Source]) -> Decoded:
    named = {key: frozenset(fault_map.sources_of(key=key)) for key in fault_map.named}
    return Decoded(
        active=frozenset(key for key, sources in named.items() if sources & bits),
        unrecognised=bits.difference(*named.values()),
    )


def decode(*, fault_map: FaultMap, words: Mapping[int, int]) -> Decoded:
    return _decoded(fault_map=fault_map, bits=_set_bits(words=words))


@dataclass(frozen=True)
class Transition:
    raised: frozenset[str]
    cleared: frozenset[str]
    unrecognised_raised: tuple[Source, ...]
    unrecognised_cleared: tuple[Source, ...]

    @property
    def changed(self) -> bool:
        return bool(
            self.raised
            or self.cleared
            or self.unrecognised_raised
            or self.unrecognised_cleared
        )


class FaultWatch:
    def __init__(self, *, fault_map: FaultMap) -> None:
        self._fault_map = fault_map
        self._bits: frozenset[Source] = frozenset()

    def observe(self, *, words: Mapping[int, int]) -> Transition:
        before = _decoded(fault_map=self._fault_map, bits=self._bits)
        kept = frozenset(
            source for source in self._bits if source.register not in words
        )
        self._bits = kept | _set_bits(words=words)
        after = _decoded(fault_map=self._fault_map, bits=self._bits)
        return Transition(
            raised=after.active - before.active,
            cleared=before.active - after.active,
            unrecognised_raised=tuple(sorted(after.unrecognised - before.unrecognised)),
            unrecognised_cleared=tuple(
                sorted(before.unrecognised - after.unrecognised)
            ),
        )
