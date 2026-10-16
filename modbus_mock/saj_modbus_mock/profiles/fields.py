import dataclasses

from saj_modbus_mock.registers import Access, Encoding, Field, FieldValue

ZERO = "zero"
PHASE_NAMES = ("r", "s", "t")
COUNTER_WORDS = 2
PERIODS = ("today", "month", "year", "total")
U16 = Encoding.U16
I16 = Encoding.I16
U32 = Encoding.U32
I32 = Encoding.I32


def live(
    *,
    address: int,
    name: str,
    source: str,
    enc: Encoding = U16,
    scale: float = 1.0,
) -> Field:
    return Field(address=address, name=name, encoding=enc, scale=scale, source=source)


def fixed(
    *,
    address: int,
    name: str,
    value: FieldValue = 0,
    enc: Encoding = U16,
    scale: float = 1.0,
) -> Field:
    return Field(
        address=address,
        name=name,
        encoding=enc,
        scale=scale,
        initial=value,
    )


def text(*, address: int, name: str, value: str, length: int) -> Field:
    return Field(
        address=address,
        name=name,
        encoding=Encoding.TEXT,
        initial=value,
        length=length,
    )


def blob(*, address: int, name: str, value: int, length: int) -> Field:
    """Unsigned raw words, most significant word first."""
    return Field(
        address=address,
        name=name,
        encoding=Encoding.HEX,
        initial=value,
        length=length,
    )


@dataclasses.dataclass(frozen=True, slots=True)
class Shape:
    enc: Encoding = U16
    scale: float = 1.0
    labels: tuple[tuple[int, str], ...] = ()
    length: int = 0
    minimum: int | None = None
    maximum: int | None = None
    options: frozenset[int] | None = None
    keepalive_bit: int = 0


def labelled(*, labels: dict[int, str]) -> Shape:
    """A choice limited to the named raw values."""
    return Shape(options=frozenset(labels), labels=tuple(labels.items()))


def setting(
    *,
    address: int,
    name: str,
    value: FieldValue = 0,
    shape: Shape | None = None,
) -> Field:
    shape = shape or Shape()
    return Field(
        address=address,
        name=name,
        encoding=shape.enc,
        scale=shape.scale,
        access=Access.READ_WRITE,
        initial=value,
        length=shape.length,
        minimum=shape.minimum,
        maximum=shape.maximum,
        options=shape.options,
        keepalive_bit=shape.keepalive_bit,
        labels=shape.labels,
    )


def command(
    *,
    address: int,
    name: str,
    labels: dict[int, str] | None = None,
    enc: Encoding = U16,
) -> Field:
    """A write-only trigger; its labels, when given, also define its options."""
    shape = Shape() if labels is None else labelled(labels=labels)
    return Field(
        address=address,
        name=name,
        encoding=enc,
        access=Access.WRITE_ONLY,
        options=shape.options,
        labels=shape.labels,
    )


def phase_key(*, group: str, phase: int, suffix: str, phases: int) -> str:
    if phase >= phases:
        return ZERO
    return f"{group}_{PHASE_NAMES[phase]}_{suffix}"


def counter_group(
    *,
    start: int,
    base: str,
    name: str,
    present: bool = True,
    parallel: bool = False,
) -> list[Field]:
    """Today, month, year and total as four consecutive 32-bit kWh counters."""
    prefix = "parallel_" if parallel else ""
    return [
        live(
            address=start + COUNTER_WORDS * index,
            name=f"{name}_{period}",
            source=f"{prefix}{base}_{period}_kwh" if present else ZERO,
            enc=U32,
            scale=0.01,
        )
        for index, period in enumerate(PERIODS)
    ]
