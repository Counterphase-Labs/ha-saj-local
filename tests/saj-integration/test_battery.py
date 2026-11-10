import logging
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.saj_local import battery as battery_module
from custom_components.saj_local.battery import BatteryEstimates
from custom_components.saj_local.const import BATTERY_SAVE_INTERVAL
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.learner import (
    LearnerState,
    PowerReading,
    SocReading,
)
from custom_components.saj_local.saj.log import LabelledLogger
from custom_components.saj_local.saj.models import Equipment
from custom_components.saj_local.saj.models.h2 import PROFILE as H2
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from tests.coordinators import FakeStore

ESTIMATE_KEYS = {
    "battery_time_to_full",
    "battery_time_to_empty",
    "battery_stored_energy",
    "battery_available_energy",
}
TEN_KWH = LearnerState(
    energy_total=10.0,
    soc_total=100.0,
    power=PowerReading(time=0.0, power=0.0),
    reading=SocReading(time=0.0, soc=50.0),
)
VALUES = {
    "battery_power": 2000,
    "battery_soc": 50.0,
    "battery_charge_soc_limit": 100,
    "backup_reserve_soc": 30,
    "battery_discharge_soc_limit_on_grid": 10,
    "application_mode": 0,
    "operating_mode": 2,
}


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class FailingStore(FakeStore):
    def __init__(self, error: Exception) -> None:
        super().__init__()
        self.error = error

    async def async_load(self):
        raise self.error

    async def async_save(self, _data) -> None:
        raise self.error


def _device(*, profile=HS3, equipment=None) -> Device:
    return Device(
        serial="S",
        device_type=0x1610 if profile is HS3 else 0x005A,
        rated_power=6000,
        profile=profile,
        detected=True,
        **({} if equipment is None else {"equipment": equipment}),
    )


def _estimates(monkeypatch, *, store=None, profile=HS3, equipment=None):
    clock = Clock()
    store = FakeStore() if store is None else store
    monkeypatch.setattr(battery_module, "battery_store", lambda **_: store)
    estimates = BatteryEstimates(
        hass=SimpleNamespace(loop=SimpleNamespace(time=clock)),
        entry_id="entry",
        device=_device(profile=profile, equipment=equipment),
        log=LabelledLogger(logger=logging.getLogger("battery-test"), label="Roof"),
    )
    return estimates, store, clock


def _at(monkeypatch, seconds: float) -> None:
    monkeypatch.setattr(
        battery_module.dt_util,
        "utcnow",
        lambda: datetime.fromtimestamp(seconds, tz=UTC),
    )


def test_the_battery_totals_of_an_installation_have_their_own_versioned_file(
    monkeypatch,
):
    created = []

    class RecordingStore:
        def __init__(self, hass, version, key) -> None:
            created.append((hass, version, key))

    monkeypatch.setattr(battery_module, "Store", RecordingStore)
    hass = object()

    store = battery_module.battery_store(hass=hass, entry_id="entry-1")

    assert isinstance(store, RecordingStore)
    assert created == [(hass, 1, "saj_local.battery.entry-1")]


def test_the_estimates_are_the_four_battery_keys_of_a_system_with_a_battery(
    monkeypatch,
):
    estimates, _, _ = _estimates(monkeypatch)

    assert estimates.keys == ESTIMATE_KEYS


def test_a_system_without_a_battery_has_no_estimates(monkeypatch):
    estimates, _, _ = _estimates(monkeypatch, equipment=frozenset({Equipment.METER_A}))

    assert estimates.keys == frozenset()
    assert (
        estimates.update(read={"battery_power"}, values=VALUES, enabled=ESTIMATE_KEYS)
        == {}
    )


async def test_a_system_without_a_battery_loads_and_saves_nothing(monkeypatch):
    store = FakeStore(TEN_KWH.to_mapping())
    estimates, _, _ = _estimates(
        monkeypatch, store=store, equipment=frozenset({Equipment.METER_A})
    )

    await estimates.async_load()
    await estimates.async_save(force=True)

    assert store.saved == []


def test_the_estimates_follow_the_readings_of_the_poll(monkeypatch):
    estimates, store, _ = _estimates(monkeypatch)
    estimates._estimator.learner.state = TEN_KWH
    _at(monkeypatch, 60)

    shown = estimates.update(
        read={"battery_power"}, values=VALUES, enabled=ESTIMATE_KEYS
    )

    assert shown == {
        "battery_time_to_full": None,
        "battery_time_to_empty": 120,
        "battery_stored_energy": 5.0,
        "battery_available_energy": 4.0,
    }
    assert store.saved == []


def test_only_the_enabled_estimates_are_shown(monkeypatch):
    estimates, _, _ = _estimates(monkeypatch)
    estimates._estimator.learner.state = TEN_KWH
    _at(monkeypatch, 60)

    shown = estimates.update(
        read={"battery_power"}, values=VALUES, enabled={"battery_stored_energy"}
    )

    assert set(shown) == {"battery_stored_energy"}


@pytest.mark.parametrize(
    ("read", "enabled"),
    [
        ({"battery_soc"}, ESTIMATE_KEYS),
        ({"battery_power"}, {"battery_power"}),
    ],
)
def test_nothing_is_estimated_without_a_battery_power_reading_or_an_enabled_estimate(
    monkeypatch, read, enabled
):
    estimates, _, _ = _estimates(monkeypatch)
    _at(monkeypatch, 60)

    assert estimates.update(read=read, values=VALUES, enabled=enabled) == {}


async def test_the_stored_totals_come_back_at_load(monkeypatch):
    estimates, _, _ = _estimates(monkeypatch, store=FakeStore(TEN_KWH.to_mapping()))

    await estimates.async_load()

    assert estimates._estimator.learner.state == TEN_KWH


async def test_a_system_without_a_stored_form_starts_with_empty_totals(monkeypatch):
    estimates, _, _ = _estimates(monkeypatch)

    await estimates.async_load()

    assert estimates._estimator.learner.state == LearnerState()


async def test_a_model_with_a_usable_capacity_keeps_no_totals(monkeypatch):
    store = FakeStore(TEN_KWH.to_mapping())
    estimates, _, clock = _estimates(monkeypatch, store=store, profile=H2)

    await estimates.async_load()
    clock.now += BATTERY_SAVE_INTERVAL
    await estimates.async_save()

    assert store.saved == []


@pytest.mark.parametrize(
    "failure",
    [
        FakeStore({"energy_total": "many"}),
        FakeStore(["not", "a", "mapping"]),
        FailingStore(HomeAssistantError("unsupported version")),
        FailingStore(NotImplementedError()),
        FailingStore(OSError("unreadable")),
    ],
)
async def test_a_store_that_cannot_be_read_logs_a_warning_and_starts_empty(
    monkeypatch, caplog, failure
):
    estimates, _, _ = _estimates(monkeypatch, store=failure)

    with caplog.at_level(logging.WARNING):
        await estimates.async_load()

    assert "could not be read" in caplog.text
    assert estimates._estimator.learner.state == LearnerState()


async def test_the_totals_are_saved_at_most_once_every_ten_minutes(monkeypatch):
    estimates, store, clock = _estimates(monkeypatch)
    learner = estimates._estimator.learner
    learner.state = TEN_KWH

    await estimates.async_save()
    clock.now += BATTERY_SAVE_INTERVAL - 1
    await estimates.async_save()
    assert store.saved == []

    clock.now += 1
    await estimates.async_save()
    assert store.saved == [TEN_KWH.to_mapping()]

    learner.state = LearnerState(energy_total=11.0, soc_total=100.0)
    clock.now += BATTERY_SAVE_INTERVAL - 1
    await estimates.async_save()
    assert len(store.saved) == 1


async def test_a_forced_save_writes_changed_totals_at_once_and_skips_unchanged(
    monkeypatch,
):
    estimates, store, _ = _estimates(monkeypatch)
    estimates._estimator.learner.state = TEN_KWH

    await estimates.async_save(force=True)
    await estimates.async_save(force=True)

    assert store.saved == [TEN_KWH.to_mapping()]


async def test_totals_that_cannot_be_written_stay_in_memory_and_are_tried_again(
    monkeypatch, caplog
):
    failing = FailingStore(OSError("disk full"))
    estimates, _, clock = _estimates(monkeypatch, store=failing)
    estimates._estimator.learner.state = TEN_KWH

    with caplog.at_level(logging.WARNING):
        await estimates.async_save(force=True)

    assert "could not be saved" in caplog.text
    assert estimates._estimator.learner.state == TEN_KWH
    monkeypatch.setattr(failing, "async_save", FakeStore().async_save)
    clock.now += BATTERY_SAVE_INTERVAL
    await estimates.async_save()
    assert estimates._saved_state == TEN_KWH
