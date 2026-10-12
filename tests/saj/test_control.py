import logging
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, time

import pytest

import saj.control as control_module
from saj.catalogue import Catalogue
from saj.client import ModbusError, ModbusErrorMessage
from saj.codec import BitRange, Encoding, Range
from saj.control import (
    Control,
    Inspection,
    RequestPlan,
    Write,
    request_plan,
    validate_value,
)
from saj.definitions import PROTECTED_KEYS, Access, Definition, EntityKind, Quantity
from saj.device import Device
from saj.errors import (
    ControlDisabledError,
    EmsTimeoutError,
    InvalidValueError,
    LinkUnavailableError,
    ModelUnverifiedError,
    ProtectedSettingError,
    SeparateRegistersError,
    UnknownSettingError,
    ValueProblem,
    WriteAllowanceError,
    WriteMismatchError,
    WriteRejectedError,
    WriteUnconfirmedError,
)
from saj.models import (
    EnableBitMethod,
    Equipment,
    Evidence,
    OperatingModeMethod,
    Placement,
    PowerFunction,
    Profile,
    Shape,
    Span,
)
from tests.saj.fakes import WritableClient

SHAPE = Shape(phases=1, strings=1)
SPAN = Span(name="all", first=0x1000, last=0x10FF)
NOW = 100.0
PROTECTED_KEY = min(PROTECTED_KEYS)
FLAGS = 0x1050
EMS_FLAGS = 0x1080
EMS_TARGET_ADDRESS = 0x2050
EMS_TARGET = "ems_grid_power_target"
LIMIT_LOW_ADDRESS = 0x2060
LIMIT_PAIR_ADDRESS = 0x2070
LIMIT_LONE_ADDRESS = 0x2073
GAP_ADDRESS = 0x2072


EVERY_RULE = pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"enabled": False}, ControlDisabledError),
        ({"detected": False}, ModelUnverifiedError),
        ({"retry": 5}, LinkUnavailableError),
        ({"connected": False}, LinkUnavailableError),
    ],
    ids=["control-off", "unverified-model", "backing-off", "connection-closed"],
)


def _setting(key: str, kind: EntityKind, **changes: object) -> Definition:
    values: dict[str, object] = {
        "key": key,
        "quantity": Quantity.COUNT,
        "encoding": Encoding.U16,
        "kind": kind,
        "access": Access.READ_WRITE,
    }
    return Definition(**{**values, **changes})


def _limit(key: str, **changes: object) -> Definition:
    return _setting(
        key,
        EntityKind.NUMBER,
        access=Access.WRITE_ONLY,
        range=Range(minimum=0, maximum=1000),
        **changes,
    )


def _definitions() -> dict[int, list[Definition]]:
    return {
        0x1010: [
            _setting(
                "level",
                EntityKind.NUMBER,
                scale=0.1,
                range=Range(minimum=0, maximum=100),
            )
        ],
        0x1020: [
            _setting(
                "wide",
                EntityKind.NUMBER,
                encoding=Encoding.U32,
                range=Range(minimum=0, maximum=100000),
            )
        ],
        0x1030: [_setting("mode", EntityKind.SELECT, options={0: "a", 1: "b", 5: "e"})],
        0x1040: [_setting("start", EntityKind.TIME, encoding=Encoding.TIME_OF_DAY)],
        FLAGS: [
            _setting(
                "flag_a",
                EntityKind.SWITCH,
                field=BitRange(first=0, last=0),
                range=Range(minimum=0, maximum=1),
            ),
            _setting(
                "flag_b",
                EntityKind.SWITCH,
                field=BitRange(first=1, last=1),
                range=Range(minimum=0, maximum=1),
            ),
            _setting(
                "days",
                EntityKind.NUMBER,
                field=BitRange(first=8, last=14),
                range=Range(minimum=0, maximum=127),
            ),
        ],
        0x1060: [
            Definition(key="reading", quantity=Quantity.COUNT, encoding=Encoding.U16)
        ],
        0x1070: [_setting(PROTECTED_KEY, EntityKind.NUMBER)],
        0x2010: [
            _setting(
                "target",
                EntityKind.NUMBER,
                access=Access.WRITE_ONLY,
                encoding=Encoding.I16,
                scale=0.01,
                range=Range(minimum=-100, maximum=100),
            )
        ],
        0x2020: [
            _setting(
                "clear_history",
                EntityKind.BUTTON,
                access=Access.WRITE_ONLY,
                command_value=1,
            ),
            _setting(
                "clear_current",
                EntityKind.BUTTON,
                access=Access.WRITE_ONLY,
                command_value=2,
            ),
        ],
        EMS_FLAGS: [
            _setting(
                "ems_inverter_control",
                EntityKind.SWITCH,
                field=BitRange(first=0, last=0),
                range=Range(minimum=0, maximum=1),
            ),
            _setting(
                "ems_battery_control",
                EntityKind.SWITCH,
                field=BitRange(first=1, last=1),
                range=Range(minimum=0, maximum=1),
            ),
        ],
        EMS_TARGET_ADDRESS: [
            _setting(
                EMS_TARGET,
                EntityKind.NUMBER,
                access=Access.WRITE_ONLY,
                encoding=Encoding.I16,
                scale=0.01,
                range=Range(minimum=-100, maximum=100),
            )
        ],
        LIMIT_LOW_ADDRESS: [_limit("ems_battery_charge_current_limit", scale=0.1)],
        LIMIT_LOW_ADDRESS + 1: [_limit("ems_battery_discharge_current_limit")],
        LIMIT_PAIR_ADDRESS: [_limit("ems_inverter_import_power_limit")],
        LIMIT_PAIR_ADDRESS + 1: [_limit("ems_inverter_export_power_limit")],
        GAP_ADDRESS: [_setting("gap", EntityKind.NUMBER, access=Access.WRITE_ONLY)],
        LIMIT_LONE_ADDRESS: [_limit("ems_pv_power_limit", invalid=frozenset({0xFFFF}))],
        0x2030: [
            _setting(
                "sync",
                EntityKind.BUTTON,
                access=Access.WRITE_ONLY,
                encoding=Encoding.CLOCK,
            )
        ],
    }


def _registers():
    by_address = _definitions()
    definitions = [definition for group in by_address.values() for definition in group]
    placements = tuple(
        Placement(key=definition.key, address=address, evidence=Evidence.VERIFIED)
        for address, group in by_address.items()
        for definition in group
    )
    profile = Profile(
        key="test",
        display_name="Test",
        device_types={1: SHAPE},
        hand_verified=True,
        largest_request=32,
        spans=(SPAN,),
        placements=placements,
        power_control={
            PowerFunction.INVERTER: EnableBitMethod(
                enable_key="ems_inverter_control",
                target_key="ems_inverter_power_target",
                alternate_keys=("ems_battery_control",),
                timeout_key="ems_timeout",
            ),
            PowerFunction.GRID: EnableBitMethod(
                enable_key="ems_grid_control",
                target_key=EMS_TARGET,
                limit_keys=(
                    "ems_battery_charge_current_limit",
                    "ems_battery_discharge_current_limit",
                    "ems_inverter_import_power_limit",
                    "ems_inverter_export_power_limit",
                    "ems_pv_power_limit",
                ),
            ),
            PowerFunction.BATTERY: OperatingModeMethod(
                mode_key="mode",
                passive_mode=3,
                default_mode=0,
                direction_key="level",
                standby=0,
                discharge=1,
                charge=2,
                charge_power_key="charge",
                discharge_power_key="discharge",
            ),
        },
    )
    return profile, Catalogue(profile=profile, definitions=definitions).registers


@pytest.fixture
def device(monkeypatch) -> Device:
    profile, registers = _registers()
    monkeypatch.setattr(control_module, "device_registers", lambda **_: registers)
    return Device(
        serial="S",
        device_type=1,
        rated_power=6000,
        profile=profile,
        detected=True,
    )


@dataclass
class StubAllowance:
    room: bool = True
    limit: int = 10
    window: float = 60.0
    recorded: list[float] = field(default_factory=list)

    def has_room(self, *, now: float) -> bool:
        del now
        return self.room

    def record(self, *, now: float) -> None:
        self.recorded.append(now)


@dataclass
class StubGuard:
    retry: float = 0.0
    allowance: StubAllowance = field(default_factory=StubAllowance)

    def retry_in(self, *, now: float) -> float:
        del now
        return self.retry


def _rule_scenario(device: Device, changes: dict):
    link = WritableClient(connected=changes.get("connected", True))
    guard = StubGuard(
        retry=changes.get("retry", 0),
        allowance=StubAllowance(room=changes.get("room", True)),
    )
    unverified = Device(
        serial=device.serial,
        device_type=device.device_type,
        rated_power=device.rated_power,
        profile=device.profile,
        detected=changes.get("detected", True),
    )
    control = _control(
        unverified, link, guard=guard, enabled=changes.get("enabled", True)
    )
    return control, link, guard


async def _assert_refused(device, changes, error, **write):
    control, link, guard = _rule_scenario(device, changes)

    with pytest.raises(error):
        await control.write(**write)

    assert link.requests == []
    assert guard.allowance.recorded == []


def _control(
    device: Device,
    link: WritableClient,
    *,
    guard: StubGuard | None = None,
    enabled: bool = True,
) -> Control:
    return Control(
        link=link,
        device=device,
        guard=guard or StubGuard(),
        enabled=enabled,
        clock=lambda: NOW,
    )


@pytest.mark.parametrize(
    ("changes", "key", "value", "error"),
    [
        ({"enabled": False}, "level", 5, ControlDisabledError),
        (
            {"enabled": False, "detected": False, "retry": 5, "room": False},
            PROTECTED_KEY,
            "bad",
            ControlDisabledError,
        ),
        (
            {"detected": False, "retry": 5, "room": False},
            PROTECTED_KEY,
            "bad",
            ModelUnverifiedError,
        ),
        (
            {"retry": 5, "room": False},
            PROTECTED_KEY,
            "bad",
            ProtectedSettingError,
        ),
        ({"retry": 5, "room": False}, "reading", "bad", UnknownSettingError),
        ({"retry": 5, "room": False}, "nothing", "bad", UnknownSettingError),
        ({"retry": 5, "room": False}, "level", "bad", InvalidValueError),
        ({"retry": 5, "room": False}, "level", 500, InvalidValueError),
        ({"retry": 5, "room": False}, "level", 5, LinkUnavailableError),
        ({"connected": False, "room": False}, "level", 5, LinkUnavailableError),
        ({"room": False}, "level", 5, WriteAllowanceError),
    ],
    ids=[
        "control-off",
        "control-off-beats-everything",
        "unverified-model",
        "protected-setting",
        "read-only-row",
        "unknown-key",
        "value-not-a-number",
        "value-out-of-range",
        "backing-off",
        "connection-closed",
        "allowance-full",
    ],
)
async def test_the_first_failing_rule_wins_and_nothing_is_sent(
    device: Device, changes: dict, key: str, value: object, error: type[Exception]
):
    await _assert_refused(device, changes, error, key=key, value=value)


async def test_a_full_allowance_refuses_a_write_but_not_the_ems_switch_off(
    device: Device,
):
    link = WritableClient({FLAGS: 0b11, EMS_FLAGS: 0b11})
    guard = StubGuard(allowance=StubAllowance(room=False))
    control = _control(device, link, guard=guard)

    with pytest.raises(WriteAllowanceError):
        await control.write(key="ems_inverter_control", value=0)
    assert link.writes == []

    result = await control.switch_off(write=Write(key="ems_inverter_control", value=0))

    assert link.writes == [("single", EMS_FLAGS, (0b10,))]
    assert result.values["ems_inverter_control"] == 0
    assert (result.assumed, result.written) == (False, True)
    assert guard.allowance.recorded == [NOW]


async def test_the_ems_switch_off_clears_every_named_bit_and_keeps_the_rest(
    device: Device,
):
    link = WritableClient({EMS_FLAGS: 0xFFFF})

    await _control(device, link).switch_off(
        write=Write(
            key="ems_inverter_control", value=0, also={"ems_battery_control": 0}
        )
    )

    assert link.writes == [("single", EMS_FLAGS, (0xFFFC,))]


@pytest.mark.parametrize(
    ("key", "value", "address", "sent"),
    [("mode", 5, 0x1030, 5), ("level", 0, 0x1010, 0)],
)
async def test_the_switch_off_sends_the_rows_of_a_models_stop_with_the_allowance_full(
    device: Device, key: str, value: int, address: int, sent: int
):
    link = WritableClient()
    guard = StubGuard(allowance=StubAllowance(room=False))

    await _control(device, link, guard=guard).switch_off(
        write=Write(key=key, value=value)
    )

    assert link.writes == [("single", address, (sent,))]
    assert guard.allowance.recorded == [NOW]


@pytest.mark.parametrize(
    "write",
    [
        Write(key="flag_a", value=0),
        Write(key="ems_inverter_control", value=0, also={"flag_a": 0}),
        Write(key="flag_a", value=0, also={"ems_inverter_control": 0}),
        Write(key="wide", value=0),
        Write(key=EMS_TARGET, value=0),
        Write(key="nothing", value=0),
    ],
    ids=[
        "other-switch",
        "ems-first-then-other",
        "other-first-then-ems",
        "number",
        "ems-target",
        "unknown",
    ],
)
async def test_the_switch_off_refuses_what_is_not_part_of_a_stop_and_sends_nothing(
    device: Device, write: Write
):
    link = WritableClient({FLAGS: 0b11, EMS_FLAGS: 0b11})
    guard = StubGuard(allowance=StubAllowance(room=False))

    with pytest.raises(UnknownSettingError):
        await _control(device, link, guard=guard).switch_off(write=write)

    assert link.requests == []
    assert guard.allowance.recorded == []


async def test_the_switch_off_never_sets_an_ems_bit(device: Device):
    link = WritableClient()

    with pytest.raises(InvalidValueError):
        await _control(device, link).switch_off(
            write=Write(key="ems_inverter_control", value=1)
        )

    assert link.requests == []


@EVERY_RULE
async def test_the_switch_off_keeps_every_other_rule_and_sends_nothing(
    device: Device, changes: dict, error: type[Exception]
):
    control, link, guard = _rule_scenario(device, {**changes, "room": False})

    with pytest.raises(error):
        await control.switch_off(write=Write(key="ems_inverter_control", value=0))

    assert link.requests == []
    assert guard.allowance.recorded == []


async def test_a_setting_is_read_with_one_request_and_without_touching_the_allowance(
    device: Device,
):
    link = WritableClient({0x1030: 5})
    guard = StubGuard(allowance=StubAllowance(room=False))

    value = await _control(device, link, guard=guard).read_setting(key="mode")

    assert link.requests == [("read", 0x1030, (0,))]
    assert value == 5
    assert guard.allowance.recorded == []


@pytest.mark.parametrize("key", ["reading", EMS_TARGET, "nothing"])
async def test_only_a_readable_writable_setting_can_be_read_through_control(
    device: Device, key: str
):
    link = WritableClient()

    with pytest.raises(UnknownSettingError):
        await _control(device, link).read_setting(key=key)

    assert link.requests == []


@EVERY_RULE
async def test_reading_a_setting_keeps_the_write_rules_and_sends_nothing(
    device: Device, changes: dict, error: type[Exception]
):
    control, link, _ = _rule_scenario(device, changes)

    with pytest.raises(error):
        await control.read_setting(key="mode")

    assert link.requests == []


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"enabled": False}, ControlDisabledError),
        ({"detected": False}, ModelUnverifiedError),
    ],
)
def test_require_admitted_refuses_a_disabled_control_and_an_unverified_model(
    device: Device, changes: dict, error: type[Exception]
):
    control, _, _ = _rule_scenario(device, changes)

    with pytest.raises(error):
        control.require_admitted()


def test_require_admitted_passes_an_enabled_control_on_a_verified_model(
    device: Device,
):
    control, _, _ = _rule_scenario(device, {})

    control.require_admitted()


async def test_the_keep_alive_reads_the_one_word_target_and_returns_its_value(
    device: Device,
):
    link = WritableClient({EMS_TARGET_ADDRESS: 0xFFEC})
    guard = StubGuard(allowance=StubAllowance(room=False))

    value = await _control(device, link, guard=guard).keep_alive_read_ems(
        key=EMS_TARGET
    )

    assert link.requests == [("read", EMS_TARGET_ADDRESS, (0,))]
    assert value == -0.2
    assert guard.allowance.recorded == []


@pytest.mark.parametrize(
    "key",
    ["level", "reading", "ems_inverter_control", "clear_history", PROTECTED_KEY],
)
async def test_the_keep_alive_refuses_every_register_but_the_ems_targets(
    device: Device, key: str
):
    link = WritableClient()

    with pytest.raises(UnknownSettingError):
        await _control(device, link).keep_alive_read_ems(key=key)

    assert link.requests == []


@EVERY_RULE
async def test_the_keep_alive_keeps_the_write_rules_and_sends_nothing(
    device: Device, changes: dict, error: type[Exception]
):
    control, link, _ = _rule_scenario(device, changes)

    with pytest.raises(error) as caught:
        await control.keep_alive_read_ems(key=EMS_TARGET)

    assert not getattr(caught.value, "link_failed", False)
    assert link.requests == []


async def test_a_keep_alive_the_device_answers_with_an_exception_is_a_rejection(
    device: Device,
):
    link = WritableClient(
        failures={
            1: ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2)
        }
    )

    with pytest.raises(WriteRejectedError) as caught:
        await _control(device, link).keep_alive_read_ems(key=EMS_TARGET)

    assert caught.value.exception_code == 2
    assert not caught.value.link_failed


async def test_a_keep_alive_nobody_answers_fails_the_link(device: Device):
    link = WritableClient(failures={1: ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT)})

    with pytest.raises(LinkUnavailableError) as caught:
        await _control(device, link).keep_alive_read_ems(key=EMS_TARGET)

    assert caught.value.link_failed


@pytest.mark.parametrize(
    "write",
    [
        Write(key="level", value=1),
        Write(key="level", value=2),
        Write(key="level", value=0.5),
        Write(key="mode", value=3),
        Write(key="ems_inverter_control", value=1),
        Write(key="ems_battery_control", value=2),
        Write(key="ems_inverter_control", value=0, also={"ems_battery_control": 1}),
        Write(key="mode", value=5, also={"level": 2}),
    ],
    ids=[
        "direction-discharge",
        "direction-charge",
        "direction-other",
        "mode-the-methods-own",
        "enable-on",
        "alternate-on",
        "alternate-on-with-the-enable-off",
        "mode-with-a-direction-that-is-not-standby",
    ],
)
async def test_the_switch_off_refuses_a_stop_row_given_a_value_a_stop_does_not_have(
    device: Device, write: Write
):
    link = WritableClient({EMS_FLAGS: 0b11})
    guard = StubGuard(allowance=StubAllowance(room=False))

    with pytest.raises(InvalidValueError):
        await _control(device, link, guard=guard).switch_off(write=write)

    assert link.requests == []
    assert guard.allowance.recorded == []


@pytest.mark.parametrize(
    "write",
    [
        Write(key="mode", value=0),
        Write(key="mode", value=1),
        Write(key="level", value=0),
        Write(key="ems_battery_control", value=0),
    ],
)
async def test_the_switch_off_accepts_only_the_values_a_stop_has(
    device: Device, write: Write
):
    link = WritableClient({EMS_FLAGS: 0b11, 0x1030: 4, 0x1010: 40})
    guard = StubGuard(allowance=StubAllowance(room=False))

    await _control(device, link, guard=guard).switch_off(write=write)

    assert guard.allowance.recorded == [NOW]


async def test_the_states_of_rows_in_one_register_are_read_in_one_request(
    device: Device,
):
    link = WritableClient({EMS_FLAGS: 0b10, 0x1030: 5})
    guard = StubGuard(allowance=StubAllowance(room=False))

    values = await _control(device, link, guard=guard).read_states(
        keys=["ems_inverter_control", "ems_battery_control", "mode"]
    )

    assert values == {"ems_inverter_control": 0, "ems_battery_control": 1, "mode": 5}
    assert link.requests == [("read", EMS_FLAGS, (0,)), ("read", 0x1030, (0,))]
    assert guard.allowance.recorded == []


@pytest.mark.parametrize("key", ["nothing", EMS_TARGET, "clear_history"])
async def test_only_readable_rows_have_their_state_read(device: Device, key: str):
    link = WritableClient()

    with pytest.raises(UnknownSettingError):
        await _control(device, link).read_states(keys=[key])

    assert link.requests == []


@EVERY_RULE
async def test_reading_states_keeps_the_write_rules_and_sends_nothing(
    device: Device, changes: dict, error: type[Exception]
):
    control, link, _ = _rule_scenario(device, changes)

    with pytest.raises(error):
        await control.read_states(keys=["mode"])

    assert link.requests == []


@pytest.mark.parametrize(
    ("failure", "error", "link_failed"),
    [
        (
            ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2),
            WriteRejectedError,
            False,
        ),
        (ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT), LinkUnavailableError, True),
    ],
)
async def test_a_failed_state_read_fails_like_a_failed_read_before_a_write(
    device: Device, failure, error, *, link_failed: bool
):
    link = WritableClient(failures={1: failure})

    with pytest.raises(error) as caught:
        await _control(device, link).read_states(keys=["mode"])

    assert caught.value.link_failed is link_failed


async def test_a_write_never_opens_a_connection_of_its_own(device: Device):
    link = WritableClient(connected=False)

    with pytest.raises(LinkUnavailableError) as caught:
        await _control(device, link).write(key="level", value=5)

    assert not caught.value.link_failed
    assert link.requests == []


async def test_a_one_word_row_is_written_once_with_function_six_and_read_back(
    device: Device,
):
    link = WritableClient()
    guard = StubGuard()

    result = await _control(device, link, guard=guard).write(key="level", value=4.2)

    assert link.requests == [("single", 0x1010, (42,)), ("read", 0x1010, (0,))]
    assert result.values == {"level": 4.2}
    assert (result.assumed, result.written) == (False, True)
    assert guard.allowance.recorded == [NOW]


async def test_a_row_of_several_words_is_written_with_one_multiple_request(
    device: Device,
):
    link = WritableClient()

    result = await _control(device, link).write(key="wide", value=70000)

    assert link.requests == [
        ("multiple", 0x1020, (1, 4464)),
        ("read", 0x1020, (0, 0)),
    ]
    assert result.values == {"wide": 70000}


@pytest.mark.parametrize(
    ("key", "value", "words"),
    [
        ("mode", 5, (5,)),
        ("mode", 1.0, (1,)),
        ("start", time(6, 30, 59), (0x061E,)),
        ("start", time(0, 0), (0,)),
    ],
)
async def test_each_value_is_sent_as_its_register_word(
    device: Device, key: str, value: object, words: tuple[int, ...]
):
    link = WritableClient()

    result = await _control(device, link).write(key=key, value=value)

    assert link.writes == [("single", _address_of(key), words)]
    assert result.written


def _address_of(key: str) -> int:
    return {"mode": 0x1030, "start": 0x1040}[key]


async def test_a_packed_field_is_read_replaced_written_and_read_back(device: Device):
    link = WritableClient({FLAGS: 0b1010_0000_0000_0101})

    result = await _control(device, link).write(key="days", value=3)

    assert link.requests == [
        ("read", FLAGS, (0,)),
        ("single", FLAGS, (0b1000_0011_0000_0101,)),
        ("read", FLAGS, (0,)),
    ]
    assert result.values == {"flag_a": 1, "flag_b": 0, "days": 3}


async def test_a_packed_field_keeps_every_other_bit_whether_named_or_not(
    device: Device,
):
    link = WritableClient({FLAGS: 0xFFFF})

    await _control(device, link).write(key="flag_b", value=0)

    assert link.writes == [("single", FLAGS, (0xFFFD,))]


async def test_a_packed_field_already_holding_the_value_writes_nothing(
    device: Device,
):
    link = WritableClient({FLAGS: 0b11})
    guard = StubGuard()

    result = await _control(device, link, guard=guard).write(key="flag_a", value=1)

    assert link.requests == [("read", FLAGS, (0,))]
    assert result.values == {"flag_a": 1, "flag_b": 1, "days": 0}
    assert (result.assumed, result.written) == (False, False)
    assert guard.allowance.recorded == []


async def test_fields_of_one_register_can_be_changed_in_a_single_write(device: Device):
    link = WritableClient({FLAGS: 0b01})

    result = await _control(device, link).write(
        key="flag_b", value=1, also={"flag_a": 0}
    )

    assert link.writes == [("single", FLAGS, (0b10,))]
    assert result.values["flag_b"] == 1
    assert result.values["flag_a"] == 0


@pytest.mark.parametrize(
    "also", [{"level": 1}, {"flag_a": 1, "level": 1}, {"nothing": 1}]
)
async def test_changes_made_together_must_all_be_fields_of_one_register(
    device: Device, also: dict[str, int]
):
    link = WritableClient()

    with pytest.raises((SeparateRegistersError, UnknownSettingError)):
        await _control(device, link).write(key="flag_b", value=1, also=also)

    assert link.requests == []


async def test_a_non_packed_row_cannot_be_changed_together_with_another(
    device: Device,
):
    with pytest.raises(SeparateRegistersError):
        await _control(device, WritableClient()).write(
            key="level", value=1, also={"mode": 1}
        )


async def test_a_write_only_row_is_only_ever_written_and_shows_what_was_sent(
    device: Device,
):
    link = WritableClient()
    guard = StubGuard()

    result = await _control(device, link, guard=guard).write(key="target", value=-12.5)

    assert link.requests == [("single", 0x2010, (0xFB1E,))]
    assert result.values == {"target": -12.5}
    assert (result.assumed, result.written) == (True, True)
    assert guard.allowance.recorded == [NOW]


@pytest.mark.parametrize(("key", "word"), [("clear_history", 1), ("clear_current", 2)])
async def test_a_command_sends_its_fixed_value_whatever_value_it_is_given(
    device: Device, key: str, word: int
):
    link = WritableClient()

    result = await _control(device, link).write(key=key, value=None)

    assert link.requests == [("single", 0x2020, (word,))]
    assert result.values == {}
    assert result.assumed


async def test_the_clock_is_one_multiple_write_with_no_read(device: Device):
    link = WritableClient()
    moment = datetime(2024, 3, 9, 14, 5, 59, tzinfo=UTC)

    result = await _control(device, link).write(key="sync", value=moment)

    assert link.requests == [("multiple", 0x2030, (2024, 0x0309, 0x0E05, 0x3B00))]
    assert result.values == {}


async def test_the_clock_refuses_a_value_that_is_not_a_moment(device: Device):
    link = WritableClient()

    with pytest.raises(InvalidValueError) as caught:
        await _control(device, link).write(key="sync", value=5)

    assert caught.value.problem is ValueProblem.NOT_A_CLOCK
    assert link.requests == []


async def test_a_read_back_that_differs_reports_what_the_inverter_holds(
    device: Device,
):
    link = WritableClient({0x1010: 7}, applies_writes=False)
    guard = StubGuard()

    with pytest.raises(WriteMismatchError) as caught:
        await _control(device, link, guard=guard).write(key="level", value=4.2)

    assert caught.value.read_back == {"level": 0.7}
    assert not caught.value.link_failed
    assert guard.allowance.recorded == [NOW]
    assert len(link.writes) == 1


async def test_a_packed_read_back_is_judged_by_its_field_alone(device: Device):
    link = WritableClient({FLAGS: 0b1})
    link.on_write = lambda: link.memory.update({FLAGS: link.memory[FLAGS] | 0x8000})

    result = await _control(device, link).write(key="flag_b", value=1)

    assert result.values["flag_b"] == 1
    assert result.values["flag_a"] == 1


async def test_a_packed_read_back_with_the_wrong_field_is_a_mismatch(device: Device):
    link = WritableClient({FLAGS: 0b1}, applies_writes=False)

    with pytest.raises(WriteMismatchError) as caught:
        await _control(device, link).write(key="flag_b", value=1)

    assert caught.value.read_back["flag_b"] == 0


@pytest.mark.parametrize("code", [2, 3, 0x12, 0x13])
async def test_an_exception_response_to_the_write_is_a_rejection_not_a_failure(
    device: Device, code: int
):
    exception = ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=code)
    link = WritableClient(failures={1: exception})

    with pytest.raises(WriteRejectedError) as caught:
        await _control(device, link).write(key="level", value=5)

    assert caught.value.exception_code == code
    assert not caught.value.link_failed
    assert len(link.requests) == 1


async def test_an_exception_response_before_a_packed_write_changes_nothing(
    device: Device,
):
    exception = ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2)
    link = WritableClient(failures={1: exception})

    with pytest.raises(WriteRejectedError):
        await _control(device, link).write(key="flag_a", value=1)

    assert link.writes == []


@pytest.mark.parametrize(
    "key_and_value",
    [
        ("level", 5),
        ("wide", 5),
        ("target", 5),
        ("sync", datetime(2024, 1, 1, tzinfo=UTC)),
    ],
)
async def test_a_write_without_an_answer_is_sent_once_and_the_state_is_unknown(
    device: Device, key_and_value: tuple[str, object]
):
    key, value = key_and_value
    silent = ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT)
    link = WritableClient(failures={1: silent})
    guard = StubGuard()

    with pytest.raises(WriteUnconfirmedError) as caught:
        await _control(device, link, guard=guard).write(key=key, value=value)

    assert caught.value.cause is silent
    assert not caught.value.acknowledged
    assert caught.value.link_failed
    assert len(link.requests) == 1
    assert guard.allowance.recorded == [NOW]


async def test_a_packed_write_without_an_answer_is_not_repeated(device: Device):
    silent = ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT)
    link = WritableClient(failures={2: silent})

    with pytest.raises(WriteUnconfirmedError):
        await _control(device, link).write(key="flag_a", value=1)

    assert [kind for kind, *_ in link.requests] == ["read", "single"]


async def test_a_packed_read_without_an_answer_fails_the_link_but_changes_nothing(
    device: Device,
):
    silent = ModbusError(ModbusErrorMessage.INCOMPLETE_RESPONSE)
    link = WritableClient(failures={1: silent})
    guard = StubGuard()

    with pytest.raises(LinkUnavailableError) as caught:
        await _control(device, link, guard=guard).write(key="flag_a", value=1)

    assert caught.value.cause is silent
    assert caught.value.link_failed
    assert link.writes == []
    assert guard.allowance.recorded == []


@pytest.mark.parametrize(
    "failure",
    [
        ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT),
        ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2),
    ],
)
async def test_a_write_acknowledged_but_not_read_back_is_unknown_and_not_repeated(
    device: Device, failure: ModbusError
):
    link = WritableClient(failures={2: failure})

    with pytest.raises(WriteUnconfirmedError) as caught:
        await _control(device, link).write(key="level", value=5)

    assert caught.value.acknowledged
    assert caught.value.link_failed
    assert len(link.writes) == 1


async def test_extra_words_are_read_with_the_register_and_checked_before_writing(
    device: Device,
):
    link = WritableClient({FLAGS: 0b01, FLAGS + 1: 77})
    seen: list[tuple[int, ...]] = []
    inspection = Inspection(
        extra_words=1, check=lambda words: seen.append(tuple(words))
    )

    await _control(device, link).write(key="flag_b", value=1, inspection=inspection)

    assert link.requests[0] == ("read", FLAGS, (0, 0))
    assert seen == [(77,)]
    assert link.writes == [("single", FLAGS, (0b11,))]


async def test_a_failed_inspection_stops_the_write(device: Device):
    def refuse(_words) -> None:
        raise WriteAllowanceError(limit=1, window=1)

    link = WritableClient()
    inspection = Inspection(extra_words=1, check=refuse)

    with pytest.raises(WriteAllowanceError):
        await _control(device, link).write(key="flag_b", value=1, inspection=inspection)

    assert link.writes == []


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("level", RequestPlan(reads_before=False, reads_back=True)),
        ("wide", RequestPlan(reads_before=False, reads_back=True)),
        ("flag_a", RequestPlan(reads_before=True, reads_back=True)),
        ("target", RequestPlan(reads_before=False, reads_back=False)),
        ("clear_history", RequestPlan(reads_before=False, reads_back=False)),
        ("sync", RequestPlan(reads_before=False, reads_back=False)),
    ],
)
def test_the_request_plan_follows_the_type_of_row(device: Device, key: str, expected):
    registers = {
        register.key: register for register in control_module.device_registers()
    }

    assert request_plan(register=registers[key]) == expected


@pytest.mark.parametrize(
    ("definition_changes", "value", "problem"),
    [
        ({"range": Range(minimum=0, maximum=10)}, 11, ValueProblem.OUT_OF_RANGE),
        ({"range": Range(minimum=0, maximum=10)}, -1, ValueProblem.OUT_OF_RANGE),
        ({"range": Range(minimum=0, maximum=10)}, "5", ValueProblem.NOT_A_NUMBER),
        ({"range": Range(minimum=0, maximum=10)}, None, ValueProblem.NOT_A_NUMBER),
        (
            {"range": Range(minimum=0, maximum=10)},
            float("nan"),
            ValueProblem.NOT_A_NUMBER,
        ),
        ({}, 70000, ValueProblem.OUT_OF_RANGE),
        ({"options": {0: "a", 3: "b"}}, 1, ValueProblem.NOT_AN_OPTION),
        ({"options": {0: "a", 3: "b"}}, 3.5, ValueProblem.NOT_AN_OPTION),
        ({"options": {0: "a", 3: "b"}}, "a", ValueProblem.NOT_A_NUMBER),
    ],
)
def test_a_value_outside_what_the_row_allows_says_why(
    definition_changes: dict, value: object, problem: ValueProblem
):
    definition = Definition(
        key="x",
        quantity=Quantity.COUNT,
        encoding=Encoding.U16,
        **definition_changes,
    )

    with pytest.raises(InvalidValueError) as caught:
        validate_value(definition=definition, value=value)

    assert caught.value.problem is problem


@pytest.mark.parametrize(
    ("definition_changes", "value"),
    [
        ({"range": Range(minimum=0, maximum=10)}, 0),
        ({"range": Range(minimum=0, maximum=10)}, 10),
        ({"range": Range(minimum=0, maximum=10)}, 2.5),
        ({"options": {0: "a", 3: "b"}}, 3),
        ({"options": {0: "a", 3: "b"}}, 3.0),
        ({"encoding": Encoding.TIME_OF_DAY}, time(1, 1)),
    ],
)
def test_a_value_the_row_allows_passes(definition_changes: dict, value: object):
    values = {"key": "x", "quantity": Quantity.COUNT, "encoding": Encoding.U16}
    definition = Definition(**{**values, **definition_changes})

    validate_value(definition=definition, value=value)


@pytest.mark.parametrize(
    ("key", "value", "logged"),
    [
        ("level", 4.2, ("function 0x06 at 0x1010 with (42,)", "read back (42,)")),
        (
            "wide",
            70000,
            ("function 0x10 at 0x1020 with (1, 4464)", "read back (1, 4464)"),
        ),
    ],
)
async def test_a_write_is_logged_at_debug_with_its_request_and_its_read_back(
    device: Device, caplog, key: str, value: object, logged: tuple[str, str]
):
    with caplog.at_level(logging.DEBUG, logger=control_module.__name__):
        await _control(device, WritableClient()).write(key=key, value=value)

    messages = [record.getMessage() for record in caplog.records]
    for expected in logged:
        assert any(key in message and expected in message for message in messages)


async def test_a_refused_write_is_not_logged(device: Device, caplog):
    with (
        caplog.at_level(logging.DEBUG, logger=control_module.__name__),
        pytest.raises(ProtectedSettingError),
    ):
        await _control(device, WritableClient()).write(key=PROTECTED_KEY, value=1)

    assert caplog.records == []


def _refusing_check(value: object) -> None:
    raise EmsTimeoutError(timeout=int(value), interval=60)


@pytest.mark.parametrize(
    ("changes", "key", "value", "error"),
    [
        ({"enabled": False}, "level", 5, ControlDisabledError),
        ({"detected": False}, "level", 5, ModelUnverifiedError),
        ({}, PROTECTED_KEY, 5, ProtectedSettingError),
        ({}, "nothing", 5, UnknownSettingError),
        ({}, "level", 500, InvalidValueError),
        ({"retry": 5}, "level", 5, EmsTimeoutError),
        ({"connected": False}, "level", 5, EmsTimeoutError),
        ({"room": False}, "level", 5, EmsTimeoutError),
    ],
    ids=[
        "control-off",
        "unverified-model",
        "protected-setting",
        "unknown-key",
        "value-out-of-range",
        "check-beats-backing-off",
        "check-beats-closed-connection",
        "check-beats-full-allowance",
    ],
)
async def test_a_value_check_ranks_after_the_value_rules_and_before_reach_and_allowance(
    device: Device, changes: dict, key: str, value: object, error: type[Exception]
):
    await _assert_refused(
        device, changes, error, key=key, value=value, check=_refusing_check
    )


async def test_a_value_check_that_passes_lets_the_write_go_ahead(device: Device):
    link = WritableClient()
    seen = []

    result = await _control(device, link).write(
        key="level", value=4.2, check=seen.append
    )

    assert seen == [4.2]
    assert result.written


LIMIT_MEMORY = {
    LIMIT_LOW_ADDRESS: 255,
    LIMIT_LOW_ADDRESS + 1: 20,
    LIMIT_PAIR_ADDRESS: 30,
    LIMIT_PAIR_ADDRESS + 1: 40,
    GAP_ADDRESS: 99,
    LIMIT_LONE_ADDRESS: 50,
}
LIMIT_REQUESTS = [
    ("read", LIMIT_LOW_ADDRESS, (0, 0)),
    ("read", LIMIT_PAIR_ADDRESS, (0, 0)),
    ("read", LIMIT_LONE_ADDRESS, (0,)),
]


async def test_the_limits_read_groups_adjacent_limits_and_never_covers_another_register(
    device: Device,
):
    link = WritableClient(LIMIT_MEMORY)

    values = await _control(device, link).read_ems_limits()

    assert link.requests == LIMIT_REQUESTS
    assert values == {
        "ems_battery_charge_current_limit": 25.5,
        "ems_battery_discharge_current_limit": 20,
        "ems_inverter_import_power_limit": 30,
        "ems_inverter_export_power_limit": 40,
        "ems_pv_power_limit": 50,
    }


async def test_a_limit_the_inverter_holds_as_no_limit_has_no_value(device: Device):
    link = WritableClient({**LIMIT_MEMORY, LIMIT_LONE_ADDRESS: 0xFFFF})

    values = await _control(device, link).read_ems_limits()

    assert values["ems_pv_power_limit"] is None
    assert values["ems_inverter_import_power_limit"] == 30


@EVERY_RULE
async def test_the_limits_read_keeps_the_write_rules_and_sends_nothing(
    device: Device, changes: dict, error: type[Exception]
):
    control, link, guard = _rule_scenario(device, {**changes, "room": False})

    with pytest.raises(error) as caught:
        await control.read_ems_limits()

    assert not getattr(caught.value, "link_failed", False)
    assert link.requests == []
    assert guard.allowance.recorded == []


async def test_a_limits_request_answered_with_an_exception_is_skipped(
    device: Device, caplog
):
    link = WritableClient(
        LIMIT_MEMORY,
        failures={
            1: ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2)
        },
    )

    with caplog.at_level(logging.DEBUG, logger=control_module.__name__):
        values = await _control(device, link).read_ems_limits()

    assert [request[1] for request in link.requests] == [
        LIMIT_LOW_ADDRESS,
        LIMIT_PAIR_ADDRESS,
        LIMIT_LONE_ADDRESS,
    ]
    assert values == {
        "ems_inverter_import_power_limit": 30,
        "ems_inverter_export_power_limit": 40,
        "ems_pv_power_limit": 50,
    }
    assert "refused with exception 2" in caplog.text
    assert [r for r in caplog.records if r.levelno > logging.DEBUG] == []


async def test_a_limits_request_nobody_answers_fails_the_link_and_stops(
    device: Device,
):
    link = WritableClient(
        LIMIT_MEMORY, failures={2: ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT)}
    )

    with pytest.raises(LinkUnavailableError) as caught:
        await _control(device, link).read_ems_limits()

    assert caught.value.link_failed
    assert len(link.requests) == 2


@pytest.mark.parametrize(
    ("fitted", "writable"),
    [
        (frozenset(), False),
        (frozenset({Equipment.METER_B}), False),
        (frozenset({Equipment.BATTERY}), True),
    ],
)
async def test_a_setting_of_equipment_that_is_not_fitted_cannot_be_written(
    monkeypatch, *, fitted: frozenset[Equipment], writable: bool
):
    profile, _ = _registers()
    setting = _setting(
        "reserve",
        EntityKind.NUMBER,
        equipment=Equipment.BATTERY,
        range=Range(minimum=0, maximum=100),
    )
    placement = Placement(key="reserve", address=0x1010, evidence=Evidence.VERIFIED)
    registers = Catalogue(
        profile=replace(profile, placements=(placement,)), definitions=[setting]
    ).registers
    seen: list[frozenset[Equipment]] = []

    def fitted_registers(*, fit):
        seen.append(fit.equipment)
        return [r for r in registers if r.equipment in (None, *fit.equipment)]

    monkeypatch.setattr(control_module, "device_registers", fitted_registers)
    device = Device(
        serial="S",
        device_type=1,
        rated_power=6000,
        profile=profile,
        detected=True,
        equipment=fitted,
    )
    link = WritableClient()
    control = _control(device, link)

    if writable:
        result = await control.write(key="reserve", value=50)
        assert result.written is True
    else:
        with pytest.raises(UnknownSettingError):
            await control.write(key="reserve", value=50)
        assert link.writes == []
    assert seen == [fitted]
