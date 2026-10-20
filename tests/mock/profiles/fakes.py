"""Stand-ins for the field helpers, so a profile module is tested on its own."""

from saj_modbus_mock.registers import Access, Encoding, Field

HELPER_NAMES = (
    "live",
    "fixed",
    "text",
    "blob",
    "setting",
    "command",
    "counter_group",
    "phase_key",
)


def fake_live(*, address, name, source, enc=Encoding.U16, scale=1.0):
    return Field(address=address, name=name, encoding=enc, scale=scale, source=source)


def fake_fixed(*, address, name, value=0, enc=Encoding.U16, scale=1.0):
    return Field(address=address, name=name, encoding=enc, scale=scale, initial=value)


def fake_text(*, address, name, value, length):
    return Field(
        address=address,
        name=name,
        encoding=Encoding.TEXT,
        initial=value,
        length=length,
    )


def fake_blob(*, address, name, value, length):
    return Field(
        address=address,
        name=name,
        encoding=Encoding.HEX,
        initial=value,
        length=length,
    )


def fake_setting(*, address, name, value=0, shape=None):
    return Field(
        address=address,
        name=name,
        encoding=shape.enc if shape else Encoding.U16,
        scale=shape.scale if shape else 1.0,
        access=Access.READ_WRITE,
        initial=value,
        length=shape.length if shape else 0,
        minimum=shape.minimum if shape else None,
        maximum=shape.maximum if shape else None,
        options=shape.options if shape else None,
        keepalive_bit=shape.keepalive_bit if shape else 0,
        labels=shape.labels if shape else (),
    )


def fake_command(*, address, name, labels=None, enc=Encoding.U16):
    return Field(
        address=address,
        name=name,
        encoding=enc,
        access=Access.WRITE_ONLY,
        options=frozenset(labels) if labels else None,
        labels=tuple(labels.items()) if labels else (),
    )


def fake_counter_group(*, start, base, name, present=True, parallel=False):
    """One recognisable field that records how the group was requested."""
    return [
        Field(
            address=start,
            name=name,
            encoding=Encoding.U32,
            source=f"counter:{base}:{present}:{parallel}",
        ),
    ]


def fake_phase_key(*, group, phase, suffix, phases):
    return f"phase:{group}:{phase}:{suffix}:{phases}"


FAKES = {
    "live": fake_live,
    "fixed": fake_fixed,
    "text": fake_text,
    "blob": fake_blob,
    "setting": fake_setting,
    "command": fake_command,
    "counter_group": fake_counter_group,
    "phase_key": fake_phase_key,
}


def isolate(monkeypatch, module):
    """Replace the field helpers a profile module imported with the fakes above."""
    for name, fake in FAKES.items():
        if hasattr(module, name):
            monkeypatch.setattr(module, name, fake)
