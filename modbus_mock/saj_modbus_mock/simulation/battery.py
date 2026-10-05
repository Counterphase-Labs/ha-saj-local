SECONDS_PER_HOUR = 3_600
MODULE_NOMINAL_VOLTAGE_V = 51.2
MAX_C_RATE_PER_HOUR = 0.5
VOLTAGE_SWING = 0.1
THROUGHPUT_PER_CYCLE_FACTOR = 2
BASE_TEMPERATURE_C = 24.0
TEMPERATURE_RISE_C = 8.0
FULL_HEALTH_PERCENT = 100.0
PERCENT = 100.0


class BatteryBank:
    def __init__(
        self,
        *,
        modules: int,
        module_capacity_ah: int,
        pack_voltage_v: float,
        initial_soc: float,
    ) -> None:
        self.modules = modules
        self.module_capacity_ah = module_capacity_ah
        self._pack_voltage_v = pack_voltage_v
        self.soc = initial_soc if modules else 0.0
        self.throughput_wh = 0.0

    @property
    def capacity_wh(self) -> float:
        return self.modules * self.module_capacity_ah * MODULE_NOMINAL_VOLTAGE_V

    @property
    def capacity_ah(self) -> int:
        return self.modules * self.module_capacity_ah

    def power_limit_w(self, *, rated_power_w: float) -> float:
        return min(rated_power_w, self.capacity_wh * MAX_C_RATE_PER_HOUR)

    def max_discharge_w(
        self,
        *,
        floor_soc: float,
        rated_power_w: float,
        dt_s: float,
    ) -> float:
        available_wh = max(0.0, self.soc - floor_soc) * self.capacity_wh
        return min(
            self.power_limit_w(rated_power_w=rated_power_w),
            available_wh * SECONDS_PER_HOUR / dt_s,
        )

    def max_charge_w(
        self,
        *,
        ceiling_soc: float,
        rated_power_w: float,
        dt_s: float,
    ) -> float:
        headroom_wh = max(0.0, ceiling_soc - self.soc) * self.capacity_wh
        return min(
            self.power_limit_w(rated_power_w=rated_power_w),
            headroom_wh * SECONDS_PER_HOUR / dt_s,
        )

    def apply(self, *, power_w: float, dt_s: float) -> None:
        if not self.modules:
            return
        energy_wh = power_w * dt_s / SECONDS_PER_HOUR
        self.soc -= energy_wh / self.capacity_wh
        self.throughput_wh += abs(energy_wh)

    def pack_voltage_v(self) -> float:
        return self._pack_voltage_v * (1 - VOLTAGE_SWING + VOLTAGE_SWING * self.soc)

    def temperature_c(self, *, power_w: float, rated_power_w: float) -> float:
        return BASE_TEMPERATURE_C + TEMPERATURE_RISE_C * min(
            1.0, abs(power_w) / rated_power_w
        )

    def cycles(self) -> int:
        return int(
            self.throughput_wh / (THROUGHPUT_PER_CYCLE_FACTOR * self.capacity_wh)
        )
