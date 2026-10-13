from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

FAULT_WORD_BITS = 32
ALL_BITS = -1


@dataclass(frozen=True, order=True)
class Source:
    register: int
    bit: int

    def __str__(self) -> str:
        return f"{self.register:#06x}:{self.bit}"


@dataclass(frozen=True)
class FaultMap:
    words: Mapping[str, int] = field(default_factory=dict)
    named: Mapping[str, Mapping[int, tuple[int, ...]]] = field(default_factory=dict)

    def sources_of(self, *, key: str) -> tuple[Source, ...]:
        return tuple(
            Source(register=register, bit=bit)
            for register, bits in self.named[key].items()
            for bit in bits
        )

    def mask_of(self, *, key: str, register: int) -> int:
        return sum(1 << bit for bit in self.named[key].get(register, ()))

    def mapped_mask(self, *, register: int) -> int:
        mask = 0
        for key in self.named:
            mask |= self.mask_of(key=key, register=register)
        return mask

    def unmapped_mask(self, *, register: int) -> int:
        return ((1 << FAULT_WORD_BITS) - 1) & ~self.mapped_mask(register=register)

    def registers_of(self, *, values: Mapping[str, object]) -> dict[int, int]:
        return {
            register: value
            for key, register in self.words.items()
            if isinstance(value := values.get(key), int)
        }
