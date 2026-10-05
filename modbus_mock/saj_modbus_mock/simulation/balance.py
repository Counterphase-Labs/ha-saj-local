import dataclasses

from .control import Command, RequestKind


@dataclasses.dataclass(frozen=True, slots=True)
class BalanceInput:
    pv_available_w: float
    external_pv_w: float
    demand_w: float
    command: Command
    grid_connected: bool
    online: bool
    max_charge_w: float
    max_discharge_w: float
    pack_voltage_v: float
    shedding: bool


@dataclasses.dataclass(frozen=True, slots=True)
class BalanceResult:
    pv_w: float
    battery_w: float
    grid_w: float
    load_w: float
    curtailed_w: float
    shed_w: float


def _clamp(*, value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _desired_battery_w(
    *, inputs: BalanceInput, pv_w: float, net_demand_w: float
) -> float:
    request = inputs.command.request
    if request is None:
        return net_demand_w - pv_w
    if request.kind is RequestKind.BATTERY:
        return request.power_w
    if request.kind is RequestKind.INVERTER:
        return request.power_w - pv_w
    return net_demand_w - pv_w + request.power_w


def _limited_battery_w(*, inputs: BalanceInput, pv_w: float, desired_w: float) -> float:
    command = inputs.command
    discharge_cap = inputs.max_discharge_w if command.allow_discharge else 0.0
    charge_cap = inputs.max_charge_w
    if command.discharge_current_limit_a is not None:
        discharge_cap = min(
            discharge_cap, command.discharge_current_limit_a * inputs.pack_voltage_v
        )
    if command.charge_current_limit_a is not None:
        charge_cap = min(
            charge_cap, command.charge_current_limit_a * inputs.pack_voltage_v
        )
    battery_w = _clamp(value=desired_w, low=-charge_cap, high=discharge_cap)
    if (
        command.inverter_sell_limit_w is not None
        and command.inverter_buy_limit_w is not None
    ):
        inverter_w = _clamp(
            value=pv_w + battery_w,
            low=-command.inverter_buy_limit_w,
            high=command.inverter_sell_limit_w,
        )
        battery_w = _clamp(value=inverter_w - pv_w, low=-charge_cap, high=discharge_cap)
    return battery_w


def _capped_export(
    *,
    inputs: BalanceInput,
    pv_w: float,
    battery_w: float,
    net_demand_w: float,
) -> tuple[float, float, float]:
    """Trim PV, then battery discharge, so export stays under the export limit."""
    limit = inputs.command.export_limit_w
    grid_w = net_demand_w - pv_w - battery_w
    if limit is None or grid_w >= -limit:
        return pv_w, battery_w, 0.0
    excess = -limit - grid_w
    pv_cut = min(excess, pv_w)
    discharge_cut = min(excess - pv_cut, max(battery_w, 0.0))
    return pv_w - pv_cut, battery_w - discharge_cut, pv_cut


def _off_grid(*, inputs: BalanceInput, pv_available_w: float) -> BalanceResult:
    demand_w = inputs.demand_w
    served_w = 0.0 if inputs.shedding else demand_w
    wanted_w = served_w - pv_available_w
    battery_w = _clamp(
        value=wanted_w, low=-inputs.max_charge_w, high=inputs.max_discharge_w
    )
    pv_w = min(pv_available_w, served_w - battery_w)
    return BalanceResult(
        pv_w=pv_w,
        battery_w=battery_w,
        grid_w=0.0,
        load_w=served_w,
        curtailed_w=pv_available_w - pv_w,
        shed_w=demand_w - served_w,
    )


def solve_balance(*, inputs: BalanceInput) -> BalanceResult:
    """Flows satisfy pv + battery + grid = load; discharge and import are positive."""
    if not inputs.grid_connected:
        return _off_grid(inputs=inputs, pv_available_w=inputs.pv_available_w)
    net_demand_w = inputs.demand_w - inputs.external_pv_w
    if not inputs.online:
        return BalanceResult(
            pv_w=0.0,
            battery_w=0.0,
            grid_w=net_demand_w,
            load_w=inputs.demand_w,
            curtailed_w=inputs.pv_available_w,
            shed_w=0.0,
        )
    pv_limit = inputs.command.pv_limit_w
    pv_w = (
        inputs.pv_available_w
        if pv_limit is None
        else min(inputs.pv_available_w, pv_limit)
    )
    desired_w = _desired_battery_w(inputs=inputs, pv_w=pv_w, net_demand_w=net_demand_w)
    battery_w = _limited_battery_w(inputs=inputs, pv_w=pv_w, desired_w=desired_w)
    pv_after_w, battery_w, _export_cut_w = _capped_export(
        inputs=inputs,
        pv_w=pv_w,
        battery_w=battery_w,
        net_demand_w=net_demand_w,
    )
    return BalanceResult(
        pv_w=pv_after_w,
        battery_w=battery_w,
        grid_w=net_demand_w - pv_after_w - battery_w,
        load_w=inputs.demand_w,
        curtailed_w=inputs.pv_available_w - pv_after_w,
        shed_w=0.0,
    )
