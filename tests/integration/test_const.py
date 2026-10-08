from types import SimpleNamespace

import pytest

from custom_components.saj_local import const


@pytest.mark.parametrize(
    ("prefix", "key", "object_id"),
    [
        ("", "pv_power", "saj_pv_power"),
        ("house", "pv_power", "saj_house_pv_power"),
        ("garage2", "battery_soc", "saj_garage2_battery_soc"),
    ],
)
def test_the_object_id_is_the_fixed_root_then_the_optional_prefix_then_the_key(
    prefix, key, object_id
):
    assert const.sensor_object_id(prefix=prefix, key=key) == object_id
    assert const.sensor_entity_id(prefix=prefix, key=key) == f"sensor.{object_id}"


class FakeRegistry:
    def __init__(self, registered) -> None:
        self.registered = registered

    def async_is_registered(self, entity_id) -> bool:
        return entity_id in self.registered


@pytest.mark.parametrize(
    ("registered", "states", "in_use"),
    [
        ({"sensor.a"}, {}, True),
        (set(), {"sensor.a": object()}, True),
        ({"sensor.a"}, {"sensor.a": object()}, True),
        ({"sensor.b"}, {"sensor.b": object()}, False),
        (set(), {}, False),
    ],
)
def test_an_entity_id_is_in_use_when_registered_or_when_it_has_a_state(
    monkeypatch, registered, states, *, in_use
):
    monkeypatch.setattr(const.er, "async_get", lambda _hass: FakeRegistry(registered))
    hass = SimpleNamespace(states=SimpleNamespace(get=states.get))

    assert const.entity_id_in_use(hass=hass, entity_id="sensor.a") is in_use
