from datetime import timedelta
from typing import TYPE_CHECKING

from . import profiles
from .clock import Clock
from .device import Device, initial_settings
from .registers import EPOCH, Field, FieldValue
from .simulation import control as ctl
from .simulation.plant import Plant
from .simulation.telemetry import build_telemetry

if TYPE_CHECKING:
    from collections.abc import Callable

    from .scenario import Scenario

COMMAND_CLEAR_FAULTS = "cmd_clear_faults"
COMMAND_RESTART = "cmd_restart"
COMMAND_CLEAR_POWER_HISTORY = "cmd_clear_power_history"
COMMAND_FACTORY_RESET = "cmd_factory_reset"
COMMAND_SET_CLOCK = "cmd_set_clock"
STANDARD_EMS_BIT = 1


class Machine:
    """One simulated inverter: clock, physics, settings and the register map."""

    def __init__(self, *, scenario: Scenario, monotonic: Callable[[], float]) -> None:
        self.scenario = scenario
        blocks = profiles.build_blocks(scenario=scenario)
        self._initial = initial_settings(blocks=blocks)
        self.settings: dict[str, FieldValue] = dict(self._initial)
        self.clock = Clock(
            start=scenario.simulation.start,
            speed=scenario.simulation.speed,
            monotonic=monotonic,
        )
        self.plant = Plant(scenario=scenario, settings=self.settings)
        self._ems_enable = 0
        self._settings_changes = 0
        self._saved_app_mode: FieldValue = 0
        self.device = Device(
            blocks=blocks,
            overrun_code=profiles.overrun_code(scenario=scenario),
            telemetry=self.telemetry,
            settings=self.settings,
            observer=self,
        )

    def _setting(self, *, key: str) -> float:
        value = self.settings.get(key, 0)
        return 0.0 if isinstance(value, str) else float(value)

    def _mirrors(self) -> dict[str, float]:
        ems = int(self._setting(key=ctl.EMS_ENABLE))
        running = ctl.MODE_EMS if ems else self._setting(key=ctl.APP_MODE)
        return {
            "running_mode": float(running),
            "mirror_charge_ceiling": self._setting(key=ctl.CHARGE_CEILING),
            "mirror_discharge_floor": self._setting(key=ctl.DISCHARGE_FLOOR_ON_GRID),
            "mirror_reserve": self._setting(key=ctl.BACKUP_RESERVE),
            "mirror_meter_mode": self._setting(key="meter_enable"),
            "mirror_ev_mode": self._setting(key="ev_mode"),
        }

    def telemetry(self) -> dict[str, float]:
        self.plant.advance(moment=self.clock.now())
        self._sync_ems()
        data = build_telemetry(plant=self.plant)
        data.update(self._mirrors())
        data["settings_change_serial"] = float(self._settings_changes)
        return data

    def _sync_ems(self) -> None:
        enable = int(self._setting(key=ctl.EMS_ENABLE))
        previous = self._ems_enable
        if enable == previous:
            return
        if enable & STANDARD_EMS_BIT and not previous & STANDARD_EMS_BIT:
            self._saved_app_mode = self.settings[ctl.APP_MODE]
            self.settings[ctl.APP_MODE] = ctl.MODE_EMS
        if previous & STANDARD_EMS_BIT and not enable & STANDARD_EMS_BIT:
            self.settings[ctl.APP_MODE] = self._saved_app_mode
        if enable and not previous:
            self.plant.controller.keepalive(second=self.plant.second)
        self._ems_enable = enable

    def _touch(self, *, field: Field) -> None:
        if (
            field.keepalive_bit
            and int(self._setting(key=ctl.EMS_ENABLE)) & field.keepalive_bit
        ):
            self.plant.controller.keepalive(second=self.plant.second)

    def field_read(self, *, field: Field) -> None:
        self._touch(field=field)

    def field_written(self, *, field: Field, value: FieldValue) -> None:
        if field.readable:
            self._settings_changes += 1
        self._touch(field=field)
        self._sync_ems()
        self._run_command(name=field.name, value=value)

    def _run_command(self, *, name: str, value: FieldValue) -> None:
        if name == COMMAND_CLEAR_FAULTS:
            self.plant.fault_bits = ()
        elif name == COMMAND_RESTART:
            self.plant.restart()
        elif name == COMMAND_CLEAR_POWER_HISTORY:
            self.plant.ledger.clear()
        elif name == COMMAND_FACTORY_RESET:
            self.settings.update(self._initial)
            self._ems_enable = 0
        elif name == COMMAND_SET_CLOCK:
            moment = EPOCH + timedelta(seconds=float(value))
            self.clock.set(moment=moment)
            self.plant.jump_to(moment=moment)
