import dataclasses
import enum
from collections.abc import MutableMapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

SETTINGS_SLOTS = 7
BYTE_BITS = 8
BYTE_MASK = 0xFF
WEEKDAY_MASK = 0x7F
MINUTES_PER_HOUR = 60
PERCENT = 100.0
EMS_SCALE = 0.0001
EMS_NO_TIMEOUT = 0xFFFF
EMS_NO_PV_LIMIT_RAW = 0xFFFF
EMS_NO_PV_LIMIT = EMS_NO_PV_LIMIT_RAW * EMS_SCALE

APP_MODE = "app_mode"
CHARGE_ENABLE_MASK = "charge_slot_enable_mask"
DISCHARGE_ENABLE_MASK = "discharge_slot_enable_mask"
DISCHARGE_FLOOR_ON_GRID = "discharge_soc_lower_limit_on_grid"
DISCHARGE_FLOOR_OFF_GRID = "discharge_soc_lower_limit_off_grid"
CHARGE_CEILING = "charge_soc_upper_limit"
BACKUP_RESERVE = "backup_reserve_soc"
BACKUP_CHARGE_POWER = "backup_charge_power"
TOU_OUTSIDE_MODE = "tou_outside_mode"
ANTI_REFLUX_MODE = "anti_reflux_mode"
ANTI_REFLUX_POWER_LIMIT = "anti_reflux_power_limit"
EMS_ENABLE = "ems_enable"
EMS_TIMEOUT = "ems_timeout_s"
EMS_INVERTER_TARGET = "ems_inverter_target"
EMS_BATTERY_CHARGE_CURRENT = "ems_battery_charge_current_limit"
EMS_BATTERY_DISCHARGE_CURRENT = "ems_battery_discharge_current_limit"
EMS_BATTERY_TARGET = "ems_battery_target"
EMS_BUY_LIMIT = "ems_buy_limit"
EMS_SELL_LIMIT = "ems_sell_limit"
EMS_GRID_TARGET = "ems_grid_target"
EMS_PV_LIMIT = "ems_pv_limit"

EMS_INVERTER_BITS = 0b001001
EMS_BATTERY_BIT = 0b000010
EMS_GRID_BIT = 0b100000
EMS_EXIT_BIT = 0b001000
EMS_STANDARD_BIT = 0b000001
EMS_ACTIVE_BITS = EMS_INVERTER_BITS | EMS_BATTERY_BIT | EMS_GRID_BIT

ANTI_REFLUX_OFF = 0
STANDBY_OUTSIDE_TOU = 0

MODE_SELF_USE = 0
MODE_TIME_OF_USE = 1
MODE_BACKUP = 2
MODE_EMS = 6

Settings = MutableMapping[str, int | float | str]


def slot_key(*, kind: str, index: int, part: str) -> str:
    return f"{kind}_slot_{index}_{part}"


class RequestKind(enum.Enum):
    BATTERY = enum.auto()
    INVERTER = enum.auto()
    GRID = enum.auto()


@dataclasses.dataclass(frozen=True, slots=True)
class BatteryRequest:
    kind: RequestKind
    power_w: float


@dataclasses.dataclass(frozen=True, slots=True)
class Command:
    request: BatteryRequest | None = None
    allow_discharge: bool = True
    floor_soc: float = 0.0
    ceiling_soc: float = 1.0
    pv_limit_w: float | None = None
    export_limit_w: float | None = None
    inverter_sell_limit_w: float | None = None
    inverter_buy_limit_w: float | None = None
    charge_current_limit_a: float | None = None
    discharge_current_limit_a: float | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class SiteContext:
    rated_power_w: float
    inverters: int


def _number(*, settings: Settings, key: str, default: float = 0) -> float:
    value = settings.get(key, default)
    return float(value) if not isinstance(value, str) else float(default)


def _in_window(*, moment: datetime, start_raw: int, end_raw: int) -> bool:
    now = moment.hour * MINUTES_PER_HOUR + moment.minute
    start = (start_raw >> BYTE_BITS) * MINUTES_PER_HOUR + (start_raw & BYTE_MASK)
    end = (end_raw >> BYTE_BITS) * MINUTES_PER_HOUR + (end_raw & BYTE_MASK)
    if start == end:
        return False
    if start < end:
        return start <= now < end
    return now >= start or now < end


def schedule_power_percent(
    *,
    settings: Settings,
    kind: str,
    enable_key: str,
    moment: datetime,
) -> float | None:
    """Power share of the first enabled slot whose window and weekday match now."""
    enabled = int(_number(settings=settings, key=enable_key))
    for index in range(1, SETTINGS_SLOTS + 1):
        if not enabled >> (index - 1) & 1:
            continue
        days_power = int(
            _number(
                settings=settings,
                key=slot_key(kind=kind, index=index, part="days_power"),
            ),
        )
        weekday_mask = (days_power >> BYTE_BITS) & WEEKDAY_MASK
        weekday_hit = (weekday_mask >> moment.weekday()) & 1
        window_hit = _in_window(
            moment=moment,
            start_raw=int(
                _number(
                    settings=settings,
                    key=slot_key(kind=kind, index=index, part="start"),
                )
            ),
            end_raw=int(
                _number(
                    settings=settings, key=slot_key(kind=kind, index=index, part="end")
                )
            ),
        )
        if weekday_hit and window_hit:
            return float(days_power & BYTE_MASK)
    return None


class Controller:
    def __init__(self, *, settings: Settings, context: SiteContext) -> None:
        self._settings = settings
        self._context = context
        self._last_keepalive_s = 0

    def keepalive(self, *, second: int) -> None:
        self._last_keepalive_s = second

    def ems_active_bits(self) -> int:
        return int(_number(settings=self._settings, key=EMS_ENABLE)) & EMS_ACTIVE_BITS

    def _expire_ems(self, *, second: int) -> None:
        enable = int(_number(settings=self._settings, key=EMS_ENABLE))
        timeout = int(
            _number(settings=self._settings, key=EMS_TIMEOUT, default=EMS_NO_TIMEOUT)
        )
        if not enable or timeout == EMS_NO_TIMEOUT:
            return
        if second - self._last_keepalive_s <= timeout:
            return
        for bits, key in (
            (EMS_INVERTER_BITS, EMS_INVERTER_TARGET),
            (EMS_BATTERY_BIT, EMS_BATTERY_TARGET),
            (EMS_GRID_BIT, EMS_GRID_TARGET),
        ):
            if enable & bits:
                self._settings[key] = 0
        if enable & EMS_EXIT_BIT:
            self._settings[EMS_ENABLE] = 0
        self._last_keepalive_s = second

    def _limits(self, *, command: Command) -> Command:
        rated = self._context.rated_power_w
        pv_share = _number(
            settings=self._settings, key=EMS_PV_LIMIT, default=EMS_NO_PV_LIMIT
        )
        unrestricted = round(pv_share / EMS_SCALE) == EMS_NO_PV_LIMIT_RAW
        return dataclasses.replace(
            command,
            pv_limit_w=None if unrestricted else pv_share * rated,
            inverter_sell_limit_w=_number(
                settings=self._settings, key=EMS_SELL_LIMIT, default=1.0
            )
            * rated,
            inverter_buy_limit_w=_number(
                settings=self._settings, key=EMS_BUY_LIMIT, default=1.0
            )
            * rated,
            charge_current_limit_a=_number(
                settings=self._settings, key=EMS_BATTERY_CHARGE_CURRENT
            ),
            discharge_current_limit_a=_number(
                settings=self._settings, key=EMS_BATTERY_DISCHARGE_CURRENT
            ),
        )

    def _target_request(self, *, meter_a_online: bool) -> BatteryRequest | None:
        rated = self._context.rated_power_w
        bits = self.ems_active_bits()
        if bits & EMS_INVERTER_BITS:
            share = _number(settings=self._settings, key=EMS_INVERTER_TARGET)
            return BatteryRequest(kind=RequestKind.INVERTER, power_w=share * rated)
        if bits & EMS_BATTERY_BIT:
            share = _number(settings=self._settings, key=EMS_BATTERY_TARGET)
            return BatteryRequest(kind=RequestKind.BATTERY, power_w=share * rated)
        grid_capable = meter_a_online and self._context.inverters == 1
        if bits & EMS_GRID_BIT and grid_capable:
            share = _number(settings=self._settings, key=EMS_GRID_TARGET)
            return BatteryRequest(kind=RequestKind.GRID, power_w=share * rated)
        return None

    def _bounds(self, *, command: Command, grid_connected: bool) -> Command:
        floor_key = (
            DISCHARGE_FLOOR_ON_GRID if grid_connected else DISCHARGE_FLOOR_OFF_GRID
        )
        floor = _number(settings=self._settings, key=floor_key) / PERCENT
        ceiling = (
            _number(settings=self._settings, key=CHARGE_CEILING, default=PERCENT)
            / PERCENT
        )
        export_limit = None
        if (
            int(_number(settings=self._settings, key=ANTI_REFLUX_MODE))
            != ANTI_REFLUX_OFF
        ):
            share = _number(settings=self._settings, key=ANTI_REFLUX_POWER_LIMIT)
            export_limit = share * self._context.rated_power_w
        return dataclasses.replace(
            command, floor_soc=floor, ceiling_soc=ceiling, export_limit_w=export_limit
        )

    def _mode_command(self, *, moment: datetime, soc: float) -> Command:
        mode = int(_number(settings=self._settings, key=APP_MODE))
        if mode == MODE_EMS:
            return Command(
                request=BatteryRequest(kind=RequestKind.BATTERY, power_w=0.0)
            )
        if mode == MODE_BACKUP:
            return self._backup_command(soc=soc)
        if mode == MODE_TIME_OF_USE:
            return self._time_of_use_command(moment=moment)
        return Command()

    def _backup_command(self, *, soc: float) -> Command:
        reserve = _number(settings=self._settings, key=BACKUP_RESERVE) / PERCENT
        if soc >= reserve:
            return Command(allow_discharge=False)
        charge_w = (
            _number(settings=self._settings, key=BACKUP_CHARGE_POWER)
            / PERCENT
            * self._context.rated_power_w
        )
        return Command(
            request=BatteryRequest(kind=RequestKind.BATTERY, power_w=-charge_w),
            allow_discharge=False,
        )

    def _time_of_use_command(self, *, moment: datetime) -> Command:
        rated = self._context.rated_power_w
        charge = schedule_power_percent(
            settings=self._settings,
            kind="charge",
            enable_key=CHARGE_ENABLE_MASK,
            moment=moment,
        )
        if charge is not None:
            return Command(
                request=BatteryRequest(
                    kind=RequestKind.BATTERY, power_w=-charge / PERCENT * rated
                )
            )
        discharge = schedule_power_percent(
            settings=self._settings,
            kind="discharge",
            enable_key=DISCHARGE_ENABLE_MASK,
            moment=moment,
        )
        if discharge is not None:
            return Command(
                request=BatteryRequest(
                    kind=RequestKind.BATTERY, power_w=discharge / PERCENT * rated
                )
            )
        outside = int(_number(settings=self._settings, key=TOU_OUTSIDE_MODE))
        if outside == STANDBY_OUTSIDE_TOU:
            return Command(
                request=BatteryRequest(kind=RequestKind.BATTERY, power_w=0.0)
            )
        return Command()

    def command(
        self,
        *,
        moment: datetime,
        second: int,
        soc: float,
        grid_connected: bool,
        meter_a_online: bool,
    ) -> Command:
        self._expire_ems(second=second)
        target = self._target_request(meter_a_online=meter_a_online)
        if target is not None:
            base = self._limits(command=Command(request=target))
        else:
            base = self._mode_command(moment=moment, soc=soc)
        return self._bounds(command=base, grid_connected=grid_connected)
