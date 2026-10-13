import pytest
from homeassistant.components.number import NumberDeviceClass, NumberMode
from homeassistant.const import EntityCategory, UnitOfPower
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.saj_local import entity, number, switch
from custom_components.saj_local.saj.codec import Range
from custom_components.saj_local.saj.definitions import EntityKind
from custom_components.saj_local.saj.errors import (
    AnotherFunctionRunningError,
    NoPowerTargetError,
    UnusablePowerError,
    WriteRejectedError,
)
from custom_components.saj_local.saj.models import PowerFunction
from tests.entities import ENTRY_ID, FakeCoordinator

BATTERY = PowerFunction.BATTERY
GRID = PowerFunction.GRID
INVERTER = PowerFunction.INVERTER
PLATFORMS = {EntityKind.SWITCH: switch, EntityKind.NUMBER: number}
KEY_SUFFIX = {EntityKind.SWITCH: "power_control", EntityKind.NUMBER: "power_target"}
LIMITS = Range(minimum=-8800, maximum=8800)


def _coordinator(*functions: PowerFunction) -> FakeCoordinator:
    coordinator = FakeCoordinator()
    coordinator.power_offered = functions
    coordinator.power_limits = LIMITS
    return coordinator


def _switch(coordinator=None, function=BATTERY) -> switch.SajPowerSwitch:
    return switch.SajPowerSwitch(
        coordinator=coordinator or _coordinator(function),
        function=function,
        identity=entity.EntityIdentity(
            domain="switch", key=f"{function}_power_control", prefix=""
        ),
    )


def _number(coordinator=None, function=BATTERY) -> number.SajPowerNumber:
    return number.SajPowerNumber(
        coordinator=coordinator or _coordinator(function),
        function=function,
        identity=entity.EntityIdentity(
            domain="number", key=f"{function}_power_target", prefix=""
        ),
    )


def _entry(coordinator, **options):
    return type(
        "Entry",
        (),
        {
            "runtime_data": type("Runtime", (), {"coordinator": coordinator})(),
            "options": options,
            "entry_id": ENTRY_ID,
        },
    )()


@pytest.fixture(autouse=True)
def no_catalogue_rows_or_registry_conflicts(monkeypatch):
    monkeypatch.setattr(entity, "device_registers", lambda **_: [])
    monkeypatch.setattr(entity, "_warn_about_displaced_entities", lambda **_: None)


@pytest.mark.parametrize("kind", PLATFORMS)
@pytest.mark.parametrize(
    "functions",
    [(BATTERY,), (BATTERY, GRID, INVERTER), ()],
)
async def test_a_switch_and_a_target_are_created_for_each_function_reported(
    kind, functions
):
    created = []

    await PLATFORMS[kind].async_setup_entry(
        None, _entry(_coordinator(*functions)), created.extend
    )

    assert [built.key for built in created] == [
        f"{function}_{KEY_SUFFIX[kind]}" for function in functions
    ]
    assert [built.function for built in created] == list(functions)


@pytest.mark.parametrize("kind", PLATFORMS)
@pytest.mark.parametrize(("prefix", "middle"), [("", ""), ("house", "house_")])
async def test_the_ids_follow_the_fixed_rule_with_the_prefix_when_one_is_set(
    kind, prefix, middle
):
    created = []

    await PLATFORMS[kind].async_setup_entry(
        None, _entry(_coordinator(BATTERY), prefix=prefix), created.extend
    )

    (built,) = created
    assert built.entity_id == f"{kind}.saj_{middle}battery_{KEY_SUFFIX[kind]}"
    assert built.unique_id == f"{ENTRY_ID}_battery_{KEY_SUFFIX[kind]}"
    assert built.coordinator_context == f"battery_{KEY_SUFFIX[kind]}"


@pytest.mark.parametrize("built", [_switch(), _number()], ids=["switch", "number"])
def test_power_control_entities_are_disabled_configuration_entities(built):
    assert built.entity_registry_enabled_default is False
    assert built.entity_category is EntityCategory.CONFIG
    assert built.translation_key == built.key
    assert built.device_info["identifiers"] == {("saj_local", ENTRY_ID)}


async def test_the_registry_is_checked_for_the_ids_of_the_new_entities(monkeypatch):
    asked = []
    monkeypatch.setattr(
        entity,
        "_warn_about_displaced_entities",
        lambda **asked_for: asked.append(asked_for),
    )

    await number.async_setup_entry(
        None, _entry(_coordinator(BATTERY, GRID), prefix="house"), [].extend
    )

    call = asked[-1]
    assert call["keys"] == ["battery_power_target", "grid_power_target"]
    assert (call["kind"], call["prefix"], call["entry"].entry_id) == (
        EntityKind.NUMBER,
        "house",
        ENTRY_ID,
    )


@pytest.mark.parametrize(
    ("running", "is_on"), [(True, True), (False, False), (None, None)]
)
def test_the_switch_is_on_while_the_inverter_reports_the_function_running(
    running, is_on
):
    coordinator = _coordinator(GRID)
    coordinator.power_state[GRID] = running

    assert _switch(coordinator, GRID).is_on is is_on


@pytest.mark.parametrize(
    ("action", "method"),
    [("async_turn_on", "async_power_on"), ("async_turn_off", "async_power_off")],
)
async def test_turning_the_switch_asks_the_coordinator_for_its_function(action, method):
    coordinator = _coordinator(GRID)

    await getattr(_switch(coordinator, GRID), action)()

    getattr(coordinator, method).assert_awaited_once_with(function=GRID)


NAMES = {"battery": "Batterie", "grid": "Netz", "inverter": "Wechselrichter"}


@pytest.fixture
def translated_names(monkeypatch):
    async def names(*, hass, selector_name):
        assert (hass, selector_name) == (None, "power_function")
        return NAMES

    monkeypatch.setattr(entity, "selector_options", names)


@pytest.mark.parametrize("action", ["async_turn_on", "async_turn_off"])
@pytest.mark.parametrize(
    ("error", "key", "placeholders"),
    [
        (
            NoPowerTargetError(function=BATTERY),
            "no_power_target",
            {"function": "Batterie"},
        ),
        (
            AnotherFunctionRunningError(running=GRID),
            "another_function_running",
            {"running": "Netz"},
        ),
    ],
)
async def test_a_refused_switch_surfaces_its_own_message_naming_the_function_translated(
    translated_names, action, error, key, placeholders
):
    del translated_names
    coordinator = _coordinator(BATTERY)
    coordinator.async_power_on.side_effect = error
    coordinator.async_power_off.side_effect = error

    with pytest.raises(ServiceValidationError) as caught:
        await getattr(_switch(coordinator), action)()

    assert caught.value.translation_key == key
    assert caught.value.translation_placeholders == placeholders


def test_the_target_shows_the_power_the_coordinator_gives_in_watts():
    coordinator = _coordinator(BATTERY)
    coordinator.power_shown[BATTERY] = -600
    built = _number(coordinator)

    assert built.native_value == -600
    assert built.native_unit_of_measurement == UnitOfPower.WATT
    assert built.device_class is NumberDeviceClass.POWER
    assert (built.native_min_value, built.native_max_value) == (-8800, 8800)
    assert built.native_step == 1
    assert built.mode is NumberMode.BOX


def test_the_target_is_unknown_until_one_is_set():
    assert _number().native_value is None


async def test_setting_the_target_hands_the_value_in_watts_to_the_coordinator():
    coordinator = _coordinator(INVERTER)

    await _number(coordinator, INVERTER).async_set_native_value(-600.0)

    coordinator.async_set_power_target.assert_awaited_once_with(
        function=INVERTER, raw=-600.0
    )


@pytest.mark.parametrize(
    ("error", "key"),
    [
        (UnusablePowerError(minimum=-8800, maximum=8800), "unusable_power"),
        (WriteRejectedError(exception_code=2), "write_rejected"),
    ],
)
async def test_a_target_that_is_refused_surfaces_its_own_translated_message(
    translated_names, error, key
):
    del translated_names
    coordinator = _coordinator(BATTERY)
    coordinator.async_set_power_target.side_effect = error

    with pytest.raises(HomeAssistantError) as caught:
        await _number(coordinator).async_set_native_value(1)

    assert caught.value.translation_key == key
