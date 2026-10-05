import pytest

from saj_modbus_mock import device as device_module
from saj_modbus_mock.device import Block, Device, initial_settings
from saj_modbus_mock.exceptions import ExceptionCode, ModbusError
from saj_modbus_mock.registers import Access, Encoding, Field

TELEMETRY = {"pressure": 12.5}
BAD_MONTH = 13


def fake_encode(*, field, value):
    """Scaled integer in the last word; the encoding itself is tested elsewhere."""
    if isinstance(value, str) or field.is_clock:
        return [0] * field.words
    return [0] * (field.words - 1) + [round(float(value) / field.scale)]


def fake_decode_raw(*, field, words):
    raw = 0
    for word in words:
        raw = (raw << 16) | word
    if field.encoding is Encoding.I16 and raw >= 0x8000:
        raw -= 0x10000
    return raw


def fake_decode(*, field, words):
    if field.is_text:
        return "".join(chr(word >> 8) + chr(word & 0xFF) for word in words)
    if field.is_clock:
        if words[1] >> 8 == BAD_MONTH:
            message = "month must be in 1..12"
            raise ValueError(message)
        return float(sum(words))
    return fake_decode_raw(field=field, words=words) * field.scale


@pytest.fixture(autouse=True)
def stubbed_encoding(monkeypatch):
    monkeypatch.setattr(device_module, "encode", fake_encode)
    monkeypatch.setattr(device_module, "decode", fake_decode)
    monkeypatch.setattr(device_module, "decode_raw", fake_decode_raw)


class Recorder:
    def __init__(self):
        self.reads = []
        self.writes = []

    def field_read(self, *, field):
        self.reads.append(field.name)

    def field_written(self, *, field, value):
        self.writes.append((field.name, value))


def build(*, unavailable=None):
    fields = (
        Field(address=0x100, name="pressure", scale=0.1, source="pressure"),
        Field(
            address=0x101,
            name="big",
            encoding=Encoding.U32,
            access=Access.READ_WRITE,
            initial=7,
        ),
        Field(
            address=0x104,
            name="small",
            access=Access.READ_WRITE,
            minimum=2,
            maximum=9,
            initial=2,
        ),
        Field(
            address=0x105,
            name="mode",
            access=Access.READ_WRITE,
            options=frozenset({1, 4}),
            initial=1,
        ),
        Field(
            address=0x106,
            name="label",
            encoding=Encoding.TEXT,
            length=2,
            access=Access.READ_WRITE,
            initial="ab",
        ),
        Field(
            address=0x108,
            name="clock",
            encoding=Encoding.CLOCK,
            access=Access.READ_WRITE,
            initial=0,
        ),
        Field(
            address=0x10C,
            name="trigger",
            access=Access.WRITE_ONLY,
            options=frozenset({1}),
        ),
        Field(
            address=0x10D,
            name="signed",
            encoding=Encoding.I16,
            access=Access.READ_WRITE,
            initial=-3,
        ),
    )
    blocks = (
        Block(start=0x100, end=0x10E, fields=fields),
        Block(start=0x200, end=0x201, fields=(), unavailable=unavailable),
    )
    settings = initial_settings(blocks=blocks)
    recorder = Recorder()
    device = Device(
        blocks=blocks,
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: TELEMETRY,
        settings=settings,
        observer=recorder,
    )
    return device, settings, recorder


def refusal(*, action):
    with pytest.raises(ModbusError) as caught:
        action()
    return caught.value.code


def test_the_initial_settings_hold_every_readable_stored_field_only():
    _, settings, _ = build()

    assert set(settings) == {"big", "small", "mode", "label", "clock", "signed"}


def test_read_mixes_live_values_stored_values_and_reserved_words():
    device, _, recorder = build()

    assert device.read(start=0x100, count=6) == [125, 0, 7, 0, 2, 1]
    assert recorder.reads == ["pressure", "big", "small", "mode"]


def test_reading_asks_for_telemetry_once_per_request():
    calls = []
    fields = (
        Field(address=0, name="a", source="pressure"),
        Field(address=1, name="b", source="pressure"),
    )
    device = Device(
        blocks=(Block(start=0, end=1, fields=fields),),
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: calls.append(1) or TELEMETRY,
        settings={},
        observer=Recorder(),
    )

    device.read(start=0, count=2)

    assert calls == [1]


def test_read_starting_inside_a_multi_word_field_returns_the_tail_only():
    device, _, _ = build()

    assert device.read(start=0x102, count=1) == [7]


def test_read_stopping_inside_a_multi_word_field_returns_the_head_only():
    device, _, _ = build()

    assert device.read(start=0x101, count=1) == [0]


@pytest.mark.parametrize(
    ("start", "count", "code"),
    [
        (0x0FF, 1, ExceptionCode.ILLEGAL_DATA_ADDRESS),
        (0x300, 1, ExceptionCode.ILLEGAL_DATA_ADDRESS),
        (0x10D, 3, ExceptionCode.BLOCK_OVERRUN),
        (0x10C, 1, ExceptionCode.ILLEGAL_DATA_ADDRESS),
        (0x200, 1, ExceptionCode.CHARGER_UNAVAILABLE),
    ],
)
def test_reads_that_the_device_cannot_serve_produce_the_documented_exception(
    start, count, code
):
    device, _, _ = build(unavailable=ExceptionCode.CHARGER_UNAVAILABLE)

    assert refusal(action=lambda: device.read(start=start, count=count)) is code


def test_a_refused_read_notifies_nobody():
    device, _, recorder = build()

    refusal(action=lambda: device.read(start=0x10B, count=2))

    assert recorder.reads == []


@pytest.mark.parametrize(
    ("start", "words", "stored"),
    [
        (0x104, [5], ("small", 5)),
        (0x105, [4], ("mode", 4)),
        (0x101, [0, 9], ("big", 9)),
        (0x106, [0x4142, 0x4344], ("label", "ABCD")),
        (0x10D, [0xFFFE], ("signed", -2)),
    ],
)
def test_accepted_writes_are_stored_and_reported(start, words, stored):
    device, settings, recorder = build()

    device.write(start=start, words=words)

    assert settings[stored[0]] == stored[1]
    assert recorder.writes == [stored]


def test_a_write_asks_for_telemetry_first_so_time_catches_up_before_the_change():
    order = []
    recorder = Recorder()
    recorder.field_written = lambda **_: order.append("write")
    fields = (Field(address=0, name="a", access=Access.READ_WRITE),)
    device = Device(
        blocks=(Block(start=0, end=0, fields=fields),),
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: order.append("telemetry") or {},
        settings={"a": 0},
        observer=recorder,
    )

    device.write(start=0, words=[1])

    assert order == ["telemetry", "write"]


def test_write_only_fields_notify_without_being_stored():
    device, settings, recorder = build()

    device.write(start=0x10C, words=[1])

    assert recorder.writes == [("trigger", 1)]
    assert "trigger" not in settings


def test_clock_field_accepts_a_valid_date():
    device, settings, _ = build()

    device.write(start=0x108, words=[2026, (6 << 8) | 21, (8 << 8) | 30, 0])

    assert settings["clock"] > 0


@pytest.mark.parametrize(
    ("start", "words", "code"),
    [
        (0x100, [1], ExceptionCode.ILLEGAL_DATA_ADDRESS),
        (0x10E, [1], ExceptionCode.ILLEGAL_DATA_ADDRESS),
        (0x0FF, [1], ExceptionCode.ILLEGAL_DATA_ADDRESS),
        (0x101, [5], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x102, [5], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x104, [1], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x104, [10], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x105, [2], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x106, [0x4142, 0xC344], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x108, [2026, (13 << 8) | 1, 0, 0], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x10C, [2], ExceptionCode.ILLEGAL_DATA_VALUE),
        (0x10D, [1, 2], ExceptionCode.ILLEGAL_DATA_ADDRESS),
    ],
)
def test_refused_writes_name_the_documented_exception(start, words, code):
    device, _, _ = build()

    assert refusal(action=lambda: device.write(start=start, words=words)) is code


def test_a_refused_write_changes_nothing():
    device, settings, recorder = build()

    code = refusal(action=lambda: device.write(start=0x104, words=[5, 99]))

    assert code is ExceptionCode.ILLEGAL_DATA_VALUE
    assert settings["small"] == 2
    assert recorder.writes == []


def test_writes_to_an_unavailable_block_are_refused_with_its_exception():
    device, _, _ = build(unavailable=ExceptionCode.CHARGER_UNAVAILABLE)

    assert (
        refusal(action=lambda: device.write(start=0x200, words=[1]))
        is ExceptionCode.CHARGER_UNAVAILABLE
    )


def test_reset_restores_the_given_initial_values():
    device, settings, _ = build()
    device.write(start=0x104, words=[5])

    device.reset_settings(initial={"small": 2})

    assert settings["small"] == 2


@pytest.mark.parametrize(
    "fields",
    [
        (Field(address=0x50, name="outside"),),
        (
            Field(address=0x10, name="a", encoding=Encoding.U32),
            Field(address=0x11, name="b"),
        ),
    ],
)
def test_blocks_refuse_misplaced_or_overlapping_fields(fields):
    with pytest.raises(ValueError, match=r"outside|overlaps"):
        Block(start=0x10, end=0x20, fields=fields)


def test_a_block_finds_the_field_covering_an_address():
    field = Field(address=0x10, name="a", encoding=Encoding.U32)
    block = Block(start=0x10, end=0x20, fields=(field,))

    assert block.field_at(address=0x11) is field
    assert block.field_at(address=0x12) is None
    assert block.contains(address=0x20)
    assert not block.contains(address=0x21)
