import pytest

from saj_local_mock import device as device_module
from saj_local_mock.device import Block, Device, initial_settings
from saj_local_mock.exceptions import ControlError, ExceptionCode, ModbusError
from saj_local_mock.registers import Access, Encoding, Field

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


def test_a_field_can_be_found_by_its_name():
    device, _, _ = build()

    assert device.field_named(name="small").address == 0x104
    assert device.field_named(name="nothing") is None


def test_a_named_write_stores_and_reports_raw_values_like_a_modbus_write():
    device, settings, recorder = build()

    device.write_named(values={"small": 5, "mode": 4.0, "label": "xy", "trigger": 1})

    assert settings["small"] == 5
    assert settings["mode"] == 4
    assert settings["label"] == "xy"
    assert recorder.writes == [
        ("small", 5),
        ("mode", 4),
        ("label", "xy"),
        ("trigger", 1),
    ]
    assert "trigger" not in settings


def test_a_named_write_of_a_scaled_field_reports_the_scaled_value():
    fields = (
        Field(address=0, name="scaled", scale=0.1, access=Access.READ_WRITE, initial=0),
    )
    settings = {"scaled": 0}
    recorder = Recorder()
    device = Device(
        blocks=(Block(start=0, end=0, fields=fields),),
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: TELEMETRY,
        settings=settings,
        observer=recorder,
    )

    device.write_named(values={"scaled": 25})

    assert settings["scaled"] == pytest.approx(2.5)
    assert recorder.writes == [("scaled", pytest.approx(2.5))]


def test_a_named_write_brings_the_simulation_up_to_date_first():
    calls = []
    fields = (Field(address=0, name="a", access=Access.READ_WRITE, initial=0),)
    device = Device(
        blocks=(Block(start=0, end=0, fields=fields),),
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: calls.append(1) or TELEMETRY,
        settings={"a": 0},
        observer=Recorder(),
    )

    device.write_named(values={"a": 1})

    assert calls == [1]


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"nothing": 1}, "nothing", "is not a writable field"),
        ({"pressure": 1}, "pressure", "is not a writable field"),
        ({"clock": 1}, "clock", "is not a writable field"),
        ({"small": "5"}, "small", "must be an integer"),
        ({"small": True}, "small", "must be an integer"),
        ({"small": 5.5}, "small", "must be an integer"),
        ({"small": float("nan")}, "small", "must be an integer"),
        ({"small": float("inf")}, "small", "must be an integer"),
        ({"small": None}, "small", "must be an integer"),
        ({"small": 1}, "small", "value below minimum"),
        ({"small": 10}, "small", "value above maximum"),
        ({"mode": 2}, "mode", "value outside enumeration"),
        ({"big": 2**32}, "big", "value above maximum"),
        ({"big": -1}, "big", "value below minimum"),
        ({"signed": 2**15}, "signed", "value above maximum"),
        ({"signed": -(2**15) - 1}, "signed", "value below minimum"),
        ({"label": 5}, "label", "must be text"),
        ({"label": "abcde"}, "label", "text is too long"),
        ({"label": "\u00e9"}, "label", "text must be ASCII"),
    ],
)
def test_a_refused_named_write_names_the_field_and_the_reason(values, key, reason):
    device, _, _ = build()

    with pytest.raises(ControlError) as caught:
        device.write_named(values=values)

    assert (caught.value.key, caught.value.reason) == (key, reason)
    assert str(caught.value) == f"{key}: {reason}"


@pytest.mark.parametrize(
    ("name", "raw"),
    [("big", 2**32 - 1), ("big", 0), ("signed", 2**15 - 1), ("signed", -(2**15))],
)
def test_a_named_write_accepts_the_edges_of_what_the_register_holds(name, raw):
    device, settings, _ = build()

    device.write_named(values={name: raw})

    assert settings[name] == raw


def test_a_named_write_changes_nothing_unless_every_value_is_valid():
    device, settings, recorder = build()

    with pytest.raises(ControlError):
        device.write_named(values={"small": 5, "mode": 2})

    assert settings["small"] == 2
    assert recorder.writes == []


def test_a_named_write_with_a_value_beyond_the_register_changes_nothing():
    device, settings, recorder = build()

    with pytest.raises(ControlError):
        device.write_named(values={"small": 5, "big": 2**32})

    assert settings["small"] == 2
    assert recorder.writes == []


@pytest.mark.parametrize(
    ("name", "stored", "reason"),
    [
        ("mode", 2, "value outside enumeration"),
        ("small", 1, "value below minimum"),
        ("small", 10, "value above maximum"),
        ("big", 2**32, "value above maximum"),
        ("big", -1, "value below minimum"),
        ("signed", 2**15, "value above maximum"),
        ("signed", -(2**15) - 1, "value below minimum"),
        ("label", "abcde", "text is too long"),
        ("label", "\u00e9", "text must be ASCII"),
        ("small", 2.5, "is not a whole raw value"),
        ("small", float("inf"), "is not a whole raw value"),
        ("small", float("nan"), "is not a whole raw value"),
    ],
)
def test_a_stored_setting_a_write_would_refuse_is_refused(name, stored, reason):
    device, _, _ = build()

    with pytest.raises(ControlError) as caught:
        device.check_stored(name=name, value=stored)

    assert (caught.value.key, caught.value.reason) == (name, reason)


@pytest.mark.parametrize(
    ("name", "stored"),
    [("small", 2), ("small", 9), ("mode", 4), ("big", 2**32 - 1), ("label", "xy")],
)
def test_a_stored_setting_a_write_would_accept_is_accepted(name, stored):
    device, _, _ = build()

    device.check_stored(name=name, value=stored)


def test_a_stored_scaled_setting_is_checked_by_its_raw_value():
    fields = (
        Field(
            address=0,
            name="scaled",
            access=Access.READ_WRITE,
            scale=0.1,
            maximum=100,
            initial=1.0,
        ),
    )
    device = Device(
        blocks=(Block(start=0, end=0, fields=fields),),
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: TELEMETRY,
        settings={"scaled": 1.0},
        observer=Recorder(),
    )

    device.check_stored(name="scaled", value=10.0)
    for refused in (10.1, 2.55):
        with pytest.raises(ControlError):
            device.check_stored(name="scaled", value=refused)


def test_peeking_gives_the_words_a_client_read_returns_without_telling_the_observer():
    device, _, recorder = build(unavailable=ExceptionCode.CHARGER_UNAVAILABLE)

    peeked = device.peek_fields()

    assert peeked["pressure"] == device.read(start=0x100, count=1)
    assert peeked["big"] == device.read(start=0x101, count=2)
    assert recorder.reads == ["pressure", "big"]


def test_peeking_covers_readable_fields_of_answering_blocks_only():
    device, _, _ = build()
    refusing, _, _ = build(unavailable=ExceptionCode.CHARGER_UNAVAILABLE)
    hidden = Device(
        blocks=(
            Block(
                start=0x300,
                end=0x301,
                fields=(Field(address=0x300, name="hidden", access=Access.READ_WRITE),),
                unavailable=ExceptionCode.CHARGER_UNAVAILABLE,
            ),
        ),
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: TELEMETRY,
        settings={"hidden": 0},
        observer=Recorder(),
    )

    assert set(device.peek_fields()) == {
        "pressure",
        "big",
        "small",
        "mode",
        "label",
        "clock",
        "signed",
    }
    assert "trigger" not in device.peek_fields()
    assert hidden.peek_fields() == {}
    assert set(refusing.peek_fields()) == set(device.peek_fields())


def test_peeking_asks_for_telemetry_once():
    calls = []
    device = Device(
        blocks=(
            Block(
                start=0,
                end=1,
                fields=(
                    Field(address=0, name="a", source="pressure"),
                    Field(address=1, name="b", source="pressure"),
                ),
            ),
        ),
        overrun_code=ExceptionCode.BLOCK_OVERRUN,
        telemetry=lambda: calls.append(1) or TELEMETRY,
        settings={},
        observer=Recorder(),
    )

    device.peek_fields()

    assert calls == [1]
