from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import BATTERY_SAVE_INTERVAL, BATTERY_STORAGE_VERSION, DOMAIN
from .saj.catalogue import estimate_keys
from .saj.estimator import BATTERY_POWER, BatteryEstimator, BatteryReading
from .saj.learner import LearnerState, LearnerStateError

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from homeassistant.core import HomeAssistant

    from .saj.codec import Value
    from .saj.device import Device
    from .saj.log import LabelledLogger

LOAD_ERRORS = (HomeAssistantError, NotImplementedError, OSError, LearnerStateError)
SAVE_ERRORS = (HomeAssistantError, OSError)


def battery_store(*, hass: HomeAssistant, entry_id: str) -> Store[dict[str, Any]]:
    return Store(hass, BATTERY_STORAGE_VERSION, f"{DOMAIN}.battery.{entry_id}")


class BatteryEstimates:
    def __init__(
        self,
        *,
        hass: HomeAssistant,
        entry_id: str,
        device: Device,
        log: LabelledLogger,
    ) -> None:
        self.keys = estimate_keys(fit=device.fit)
        self._estimator = (
            BatteryEstimator(profile=device.profile) if self.keys else None
        )
        self._store = battery_store(hass=hass, entry_id=entry_id)
        self._clock = hass.loop.time
        self._log = log
        self._saved_state = LearnerState()
        self._saved_at = self._clock()

    async def async_load(self) -> None:
        learner = None if self._estimator is None else self._estimator.learner
        if learner is None:
            return
        try:
            stored = await self._store.async_load()
            if stored is not None:
                learner.state = LearnerState.from_mapping(stored)
        except LOAD_ERRORS as error:
            self._log.warning(
                "The stored battery capacity could not be read (%s);"
                " learning starts again",
                type(error).__name__,
            )
            return
        self._saved_state = learner.state

    def update(
        self,
        *,
        read: Collection[str],
        values: Mapping[str, Value],
        enabled: Collection[str],
    ) -> dict[str, Value]:
        wanted = self.keys & set(enabled)
        if self._estimator is None or BATTERY_POWER not in read or not wanted:
            return {}
        estimates = self._estimator.update(
            reading=BatteryReading.of(values=values, read=read),
            time=dt_util.utcnow().timestamp(),
        )
        shown: dict[str, Value] = {
            "battery_time_to_full": estimates.time_to_full,
            "battery_time_to_empty": estimates.time_to_empty,
            "battery_stored_energy": estimates.stored_energy,
            "battery_available_energy": estimates.available_energy,
        }
        return {key: value for key, value in shown.items() if key in wanted}

    async def async_save(self, *, force: bool = False) -> None:
        learner = None if self._estimator is None else self._estimator.learner
        now = self._clock()
        if (
            learner is None
            or learner.state == self._saved_state
            or (not force and now - self._saved_at < BATTERY_SAVE_INTERVAL)
        ):
            return
        self._saved_at = now
        try:
            await self._store.async_save(learner.state.to_mapping())
        except SAVE_ERRORS as error:
            self._log.warning(
                "The learned battery capacity could not be saved (%s);"
                " it stays in memory",
                type(error).__name__,
            )
            return
        self._saved_state = learner.state
