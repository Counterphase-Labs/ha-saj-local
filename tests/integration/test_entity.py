import logging
from types import SimpleNamespace

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.saj_local import (
    binary_sensor,
    button,
    entity,
    number,
    select,
    sensor,
    switch,
    text,
)
from custom_components.saj_local import time as time_platform
from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.catalogue import Fit, device_registers
from custom_components.saj_local.saj.definitions import Access, EntityKind, Quantity
from custom_components.saj_local.saj.errors import (
    ControlDisabledError,
    InvalidValueError,
    ProtectedSettingError,
    ValueProblem,
    WriteMismatchError,
    WriteRejectedError,
)
from custom_components.saj_local.saj.models import ALL_EQUIPMENT
from custom_components.saj_local.saj.models.h2 import PROFILE as H2
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from tests.entities import ENTRY_ID, FakeCoordinator, device, register_of

PLATFORM_MODULES = {
    EntityKind.SENSOR: sensor,
    EntityKind.BINARY_SENSOR: binary_sensor,
    EntityKind.NUMBER: number,
    EntityKind.SELECT: select,
    EntityKind.SWITCH: switch,
    EntityKind.TIME: time_platform,
    EntityKind.TEXT: text,
    EntityKind.BUTTON: button,
}
ENTITY_CLASSES = {
    EntityKind.SENSOR: sensor.SajSensor,
    EntityKind.BINARY_SENSOR: binary_sensor.SajBinarySensor,
    EntityKind.NUMBER: number.SajNumber,
    EntityKind.SELECT: select.SajSelect,
    EntityKind.SWITCH: switch.SajSwitch,
    EntityKind.TIME: time_platform.SajTime,
    EntityKind.TEXT: text.SajText,
    EntityKind.BUTTON: button.SajButton,
}
ALL_KINDS = list(PLATFORM_MODULES)


def _build(*, kind: EntityKind, prefix: str = "", coordinator=None, **changes):
    return ENTITY_CLASSES[kind](
        coordinator=coordinator or FakeCoordinator(),
        register=register_of(kind=kind, **changes),
        prefix=prefix,
    )


@pytest.mark.parametrize("kind", ALL_KINDS)
@pytest.mark.parametrize(
    ("prefix", "expected_object_id"),
    [("", "saj_test_row"), ("house", "saj_house_test_row")],
)
def test_entity_id_comes_from_the_domain_prefix_and_key_never_from_display_text(
    kind, prefix, expected_object_id
):
    built = _build(kind=kind, prefix=prefix)

    assert built.entity_id == f"{kind.value}.{expected_object_id}"


@pytest.mark.parametrize("kind", ALL_KINDS)
def test_unique_id_is_the_config_entry_id_and_key_whatever_the_domain(kind):
    built = _build(kind=kind)

    assert built.unique_id == f"{ENTRY_ID}_test_row"
    assert built.translation_key == "test_row"


def test_device_identity_names_the_installation_and_the_effective_profile():
    built = _build(kind=EntityKind.SENSOR)

    assert built.device_info["identifiers"] == {(DOMAIN, ENTRY_ID)}
    assert built.device_info["name"] == "SAJ"
    assert built.device_info["manufacturer"] == "SAJ"
    assert built.device_info["serial_number"] == "TEST-001"


@pytest.mark.parametrize(
    ("display_name", "detected", "expected"),
    [
        ("Alpha", True, "Alpha (12000 W)"),
        ("Beta", True, "Beta (12000 W)"),
        ("Beta", False, "Beta (12000 W, unverified)"),
    ],
)
def test_device_model_says_whether_the_profile_was_detected(
    display_name, detected, expected
):
    coordinator = FakeCoordinator(
        device_under_test=device(display_name=display_name, detected=detected)
    )

    built = _build(kind=EntityKind.SENSOR, coordinator=coordinator)

    assert built.device_info["model"] == expected


def test_unique_id_and_device_identity_do_not_depend_on_the_profile():
    entities = [
        _build(
            kind=EntityKind.SENSOR,
            coordinator=FakeCoordinator(device_under_test=device(display_name=name)),
        )
        for name in ("Alpha", "Beta")
    ]

    assert len({built.unique_id for built in entities}) == 1
    assert len({frozenset(built.device_info["identifiers"]) for built in entities}) == 1


@pytest.mark.parametrize("kind", ALL_KINDS)
@pytest.mark.parametrize("core", [True, False])
def test_only_a_core_row_is_enabled_by_default(kind, *, core):
    built = ENTITY_CLASSES[kind](
        coordinator=FakeCoordinator(),
        register=register_of(kind=kind, core=core),
        prefix="",
    )

    assert built.entity_registry_enabled_default is core


@pytest.mark.parametrize(
    ("kind", "changes", "category"),
    [
        (EntityKind.SENSOR, {}, None),
        (EntityKind.SENSOR, {"quantity": Quantity.VERSION}, "diagnostic"),
        (EntityKind.SENSOR, {"quantity": Quantity.ADDRESS}, "diagnostic"),
        (EntityKind.SENSOR, {"key": "settings_sequence"}, "diagnostic"),
        (EntityKind.NUMBER, {}, "config"),
        (EntityKind.NUMBER, {"key": "rs485_address"}, "diagnostic"),
        (EntityKind.SELECT, {}, "config"),
        (EntityKind.SELECT, {"key": "battery_protocol"}, "diagnostic"),
        (EntityKind.SWITCH, {}, "config"),
        (EntityKind.TIME, {}, "config"),
        (EntityKind.TEXT, {"quantity": Quantity.ADDRESS}, "diagnostic"),
        (EntityKind.BUTTON, {}, "config"),
    ],
)
def test_settings_are_configuration_and_versions_and_commissioning_diagnostic(
    kind, changes, category
):
    built = _build(kind=kind, **changes)

    assert built.entity_category == category


@pytest.mark.parametrize(
    ("installation_up", "unavailable", "expected"),
    [
        (True, frozenset(), True),
        (True, frozenset({"other_row"}), True),
        (True, frozenset({"test_row"}), False),
        (False, frozenset(), False),
        (False, frozenset({"test_row"}), False),
    ],
)
def test_availability_combines_the_installation_and_the_row_itself(
    *, installation_up, unavailable, expected
):
    coordinator = FakeCoordinator()
    coordinator.last_update_success = installation_up
    coordinator.unavailable_keys = unavailable

    assert _build(kind=EntityKind.SENSOR, coordinator=coordinator).available is expected


@pytest.fixture
def writes(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        entity.SajEntity,
        "async_write_ha_state",
        lambda self: recorded.append(self.key),
    )
    return recorded


@pytest.mark.parametrize("kind", ALL_KINDS)
def test_state_is_written_in_a_cycle_that_read_the_row(kind, writes):
    coordinator = FakeCoordinator()
    coordinator.last_read = frozenset({"test_row"})

    _build(kind=kind, coordinator=coordinator)._handle_coordinator_update()

    assert writes == ["test_row"]


async def test_state_is_not_written_while_availability_is_unchanged_and_row_unread(
    writes,
):
    coordinator = FakeCoordinator()
    built = _build(kind=EntityKind.SENSOR, coordinator=coordinator)
    await built.async_added_to_hass()
    coordinator.last_read = frozenset({"other_row"})

    built._handle_coordinator_update()
    built._handle_coordinator_update()

    assert writes == []


async def test_state_is_written_once_per_availability_change(writes):
    coordinator = FakeCoordinator()
    built = _build(kind=EntityKind.SENSOR, coordinator=coordinator)
    await built.async_added_to_hass()

    coordinator.last_update_success = False
    built._handle_coordinator_update()
    built._handle_coordinator_update()
    coordinator.last_update_success = True
    built._handle_coordinator_update()
    coordinator.unavailable_keys = frozenset({"test_row"})
    built._handle_coordinator_update()
    coordinator.unavailable_keys = frozenset()
    built._handle_coordinator_update()
    built._handle_coordinator_update()

    assert writes == ["test_row"] * 4


def test_state_is_written_for_a_key_the_coordinator_just_changed(writes):
    coordinator = FakeCoordinator()
    coordinator.changed_keys = frozenset({"test_row"})

    _build(kind=EntityKind.NUMBER, coordinator=coordinator)._handle_coordinator_update()

    assert writes == ["test_row"]


def test_state_is_not_written_for_a_key_changed_elsewhere(writes):
    coordinator = FakeCoordinator()
    coordinator.changed_keys = frozenset({"other_row"})
    built = _build(kind=EntityKind.NUMBER, coordinator=coordinator)
    built._written_available = built.available

    built._handle_coordinator_update()

    assert writes == []


@pytest.mark.parametrize("kind", ALL_KINDS)
async def test_an_action_is_one_write_by_key_to_the_coordinator(kind):
    coordinator = FakeCoordinator()

    await _build(kind=kind, coordinator=coordinator).async_change(value=7)

    coordinator.write.assert_awaited_once_with(key="test_row", value=7)


@pytest.mark.parametrize(
    ("error", "key", "refusal"),
    [
        (ControlDisabledError(), "control_not_enabled", True),
        (ProtectedSettingError("rs485_address"), "protected_setting", True),
        (
            InvalidValueError(ValueProblem.OUT_OF_RANGE),
            "invalid_value_out_of_range",
            True,
        ),
        (WriteRejectedError(exception_code=3), "write_rejected", False),
        (WriteMismatchError(read_back={}), "write_mismatch", False),
    ],
)
async def test_a_refused_or_failed_action_surfaces_its_own_translated_message(
    error, key, *, refusal
):
    coordinator = FakeCoordinator()
    coordinator.write.side_effect = error

    with pytest.raises(HomeAssistantError) as raised:
        await _build(kind=EntityKind.NUMBER, coordinator=coordinator).async_change(
            value=1
        )

    assert raised.value.translation_domain == DOMAIN
    assert raised.value.translation_key == key
    assert isinstance(raised.value, ServiceValidationError) is refusal
    assert raised.value.__cause__ is error


def test_a_write_only_row_shows_what_was_sent_and_a_read_row_shows_the_reading():
    coordinator = FakeCoordinator(values={"test_row": 1})
    coordinator.assumed["test_row"] = 9
    written = _build(
        kind=EntityKind.NUMBER, coordinator=coordinator, access=Access.WRITE_ONLY
    )
    read = _build(kind=EntityKind.NUMBER, coordinator=coordinator)

    assert (written.read_value, read.read_value) == (9, 1)


class FakeRegistry:
    def __init__(self) -> None:
        self.registered: dict[str, str] = {}
        self.taken: set[str] = set()

    def async_get_entity_id(self, domain, platform, unique_id):
        del domain, platform
        return self.registered.get(unique_id)

    def async_get_available_entity_id(self, domain, preferred):
        return f"{domain}.{preferred}_2"


@pytest.fixture
def registry(monkeypatch) -> FakeRegistry:
    fake = FakeRegistry()
    monkeypatch.setattr(entity.er, "async_get", lambda _hass: fake)
    monkeypatch.setattr(
        entity,
        "entity_id_in_use",
        lambda *, hass, entity_id: (hass, entity_id)[1] in fake.taken,
    )
    return fake


@pytest.fixture
def rows(monkeypatch):
    registers = [
        register_of(kind=kind, key=f"{kind.value}_row") for kind in ALL_KINDS
    ] + [
        register_of(kind=EntityKind.SENSOR, key="second_sensor_row"),
        register_of(kind=EntityKind.SENSOR, key="hidden_word", exposed=False),
    ]
    monkeypatch.setattr(entity, "device_registers", lambda **_: registers)
    return registers


def _entry(coordinator, **options):
    return SimpleNamespace(
        runtime_data=SimpleNamespace(coordinator=coordinator), options=options
    )


@pytest.mark.parametrize("kind", ALL_KINDS)
async def test_each_platform_creates_an_entity_for_each_row_of_its_own_type(
    kind, registry, rows
):
    del registry, rows
    created = []

    await PLATFORM_MODULES[kind].async_setup_entry(
        None, _entry(FakeCoordinator()), created.extend
    )

    expected = (
        {"second_sensor_row", "sensor_row"}
        if kind is EntityKind.SENSOR
        else {f"{kind.value}_row"}
    )
    assert {built.key for built in created} == expected
    assert {built.coordinator_context for built in created} == expected
    assert all(isinstance(built, ENTITY_CLASSES[kind]) for built in created)


@pytest.mark.parametrize("kind", ALL_KINDS)
@pytest.mark.parametrize(
    ("options", "expected_prefix"),
    [({"prefix": "house"}, "house_"), ({"prefix": ""}, ""), ({}, "")],
)
async def test_each_platform_applies_the_prefix_saved_in_the_entry_options(
    kind, options, expected_prefix, registry, rows
):
    del registry, rows
    created = []

    await PLATFORM_MODULES[kind].async_setup_entry(
        None, _entry(FakeCoordinator(), **options), created.extend
    )

    assert {built.entity_id for built in created} == {
        f"{kind.value}.saj_{expected_prefix}{built.key}" for built in created
    }


async def test_entities_are_added_without_attaching_them_to_a_subentry(registry, rows):
    del registry, rows
    calls = []

    def add_entities(entities, *args, **kwargs):
        calls.append((list(entities), args, kwargs))

    await number.async_setup_entry(None, _entry(FakeCoordinator()), add_entities)

    assert len(calls) == 1
    assert calls[0][1:] == ((), {})


@pytest.mark.parametrize("kind", ALL_KINDS)
async def test_a_new_entity_whose_id_is_taken_logs_one_warning_naming_both_ids(
    kind, registry, rows, caplog
):
    del rows
    registry.taken.add(f"{kind.value}.saj_house_{kind.value}_row")
    entry = _entry(FakeCoordinator(), prefix="house")

    with caplog.at_level(logging.WARNING, logger=entity.__name__):
        await PLATFORM_MODULES[kind].async_setup_entry(None, entry, [].extend)

    assert [record.getMessage() for record in caplog.records] == [
        (
            f"Entity ID {kind.value}.saj_house_{kind.value}_row is taken, so "
            f"{kind.value} {kind.value}_row is registered as "
            f"{kind.value}.saj_house_{kind.value}_row_2"
        )
    ]


@pytest.mark.parametrize("already_registered", [True, False])
async def test_only_an_entity_new_to_the_registry_is_warned_about(
    registry, rows, caplog, *, already_registered
):
    del rows
    registry.taken.add("number.saj_number_row")
    if already_registered:
        registry.registered[f"{ENTRY_ID}_number_row"] = "number.saj_number_row"

    with caplog.at_level(logging.WARNING, logger=entity.__name__):
        await number.async_setup_entry(None, _entry(FakeCoordinator()), [].extend)

    assert bool(caplog.records) is not already_registered


async def test_free_entity_ids_log_no_warning(registry, rows, caplog):
    del registry, rows

    with caplog.at_level(logging.WARNING, logger=entity.__name__):
        await number.async_setup_entry(
            None, _entry(FakeCoordinator(), prefix="house"), [].extend
        )

    assert caplog.records == []


@pytest.mark.parametrize(
    ("profile", "device_type", "by_kind", "enabled_by_kind"),
    [
        (
            HS3,
            0x1610,
            {
                "sensor": 426,
                "binary_sensor": 129,
                "number": 77,
                "select": 19,
                "switch": 37,
                "time": 42,
                "text": 5,
                "button": 5,
            },
            {
                "sensor": 46,
                "binary_sensor": 129,
                "number": 2,
                "select": 2,
                "switch": 0,
                "time": 0,
                "text": 0,
                "button": 0,
            },
        ),
        (
            H2,
            0x005A,
            {
                "sensor": 220,
                "binary_sensor": 73,
                "number": 46,
                "select": 5,
                "switch": 16,
                "time": 28,
                "text": 0,
                "button": 4,
            },
            {
                "sensor": 39,
                "binary_sensor": 73,
                "number": 3,
                "select": 1,
                "switch": 0,
                "time": 0,
                "text": 0,
                "button": 0,
            },
        ),
    ],
)
def test_a_recognised_device_gets_the_entities_of_its_shape_with_the_core_enabled(
    profile, device_type, by_kind, enabled_by_kind
):
    registers = device_registers(
        fit=Fit(profile=profile, device_type=device_type, equipment=ALL_EQUIPMENT)
    )

    assert {
        kind.value: sum(row.kind is kind and row.exposed for row in registers)
        for kind in ALL_KINDS
    } == by_kind
    assert {
        kind.value: sum(
            row.kind is kind and row.core and row.exposed for row in registers
        )
        for kind in ALL_KINDS
    } == enabled_by_kind
