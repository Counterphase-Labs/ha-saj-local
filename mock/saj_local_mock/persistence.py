"""Keeps the running state across restarts. Without a mounted folder it does nothing."""

import asyncio
import hashlib
import json
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping
    from pathlib import Path

    from .scenario import Scenario

STATE_VERSION = 1
DEFAULT_STATE_PATH = "/data/state.json"
MINIMUM_SAVE_GAP_S = 1.0
PERIODIC_SAVE_GAP_S = 60.0
TICK_S = 1.0
TEMPORARY_SUFFIX = ".tmp"
LOGGER = logging.getLogger(__name__)


def scenario_hash(*, scenario: Scenario) -> str:
    """Identifies the scenario a saved state belongs to; any change to it differs."""
    return hashlib.sha256(repr(scenario).encode()).hexdigest()


class StateStore:
    """The state file. Without a mounted folder it does nothing."""

    def __init__(
        self,
        *,
        path: Path,
        scenario_hash: str,
        is_mount: Callable[[Path], bool] = os.path.ismount,
    ) -> None:
        self._path = path
        self._scenario_hash = scenario_hash
        self._failing = False
        self.enabled = is_mount(path.parent)
        if not self.enabled:
            LOGGER.warning(
                "nothing is mounted at %s, so changes will not be kept",
                path.parent,
            )

    def load(self) -> Mapping[str, object] | None:
        """The saved state, or None when there is none or it is for another scenario."""
        if not self.enabled or not self._path.exists():
            return None
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            LOGGER.warning(
                "saved state could not be read (%s); starting from the scenario", error
            )
            return None
        if not isinstance(payload, dict) or payload.get("version") != STATE_VERSION:
            LOGGER.warning(
                "saved state has an unknown format; starting from the scenario"
            )
            return None
        if payload.get("scenario_hash") != self._scenario_hash:
            LOGGER.warning(
                "the scenario changed since the state was saved;"
                " starting from the scenario"
            )
            return None
        state = payload.get("state")
        return state if isinstance(state, dict) else None

    def save(self, *, snapshot: Mapping[str, object]) -> None:
        """Write to a temporary name and rename, so a crash never leaves half a file."""
        if not self.enabled:
            return
        payload = {
            "version": STATE_VERSION,
            "scenario_hash": self._scenario_hash,
            "state": snapshot,
        }
        temporary = self._path.with_name(self._path.name + TEMPORARY_SUFFIX)
        try:
            temporary.write_text(json.dumps(payload), encoding="utf-8")
            temporary.replace(self._path)
        except OSError as error:
            if not self._failing:
                LOGGER.warning(
                    "state could not be saved (%s); changes will not be kept", error
                )
            self._failing = True
            return
        self._failing = False

    def delete(self) -> None:
        if not self.enabled:
            return
        self._path.unlink(missing_ok=True)


class Saver:
    """Decides when to save: soon after a change, and now and then while running."""

    def __init__(
        self,
        *,
        store: StateStore,
        snapshot: Callable[[], Mapping[str, object]],
        monotonic: Callable[[], float],
        pause: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._store = store
        self._snapshot = snapshot
        self._monotonic = monotonic
        self._pause = pause
        self._dirty = False
        self._last_save = monotonic()

    def changed(self) -> None:
        self._dirty = True

    def flush(self) -> None:
        self._store.save(snapshot=self._snapshot())
        self._dirty = False
        self._last_save = self._monotonic()

    def tick(self) -> None:
        since_save = self._monotonic() - self._last_save
        if (
            self._dirty and since_save >= MINIMUM_SAVE_GAP_S
        ) or since_save >= PERIODIC_SAVE_GAP_S:
            self.flush()

    async def run(self) -> None:
        while True:
            await self._pause(TICK_S)
            self.tick()
