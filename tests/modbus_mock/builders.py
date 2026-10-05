"""Hand-built scenario values; they are plain data, not collaborators."""

import dataclasses
from datetime import UTC, datetime

from saj_modbus_mock.models import MODELS
from saj_modbus_mock.scenario import (
    BatteryConfig,
    DeviceConfig,
    EvChargerConfig,
    FaultsConfig,
    LoadConfig,
    MetersConfig,
    ParallelConfig,
    Scenario,
    ServerConfig,
    SimulationConfig,
    SiteConfig,
)

START = datetime(2026, 6, 21, 5, 0, tzinfo=UTC)


def make_scenario(*, model: str = "hs3", **changes: object) -> Scenario:
    """A complete scenario; keyword changes replace a section or one field of it."""
    spec = MODELS[model]
    scenario = Scenario(
        device=DeviceConfig(
            model=spec, rated_power_w=spec.default_rated_power_w, serial_number="SN123"
        ),
        server=ServerConfig(port=0, unit_id=1, max_clients=2, response_delay_ms=0),
        simulation=SimulationConfig(seed=7, start=START, speed=1.0),
        site=SiteConfig(
            grid_connected=True,
            pv_strings=(3000, 3000),
            load=LoadConfig(base_w=300, peak_w=3000),
        ),
        battery=BatteryConfig(
            modules=2, module_capacity_ah=100, initial_soc_percent=50
        ),
        meters=MetersConfig(meter_a=True, meter_b=False),
        ev_charger=EvChargerConfig(
            installed=False, phases=3, max_power_w=11000, sessions=()
        ),
        parallel=ParallelConfig(inverters=1),
        faults=FaultsConfig(inverter_fault_bits=()),
    )
    for section, change in changes.items():
        current = getattr(scenario, section)
        replacement = (
            dataclasses.replace(current, **change)
            if isinstance(change, dict)
            else change
        )
        scenario = dataclasses.replace(scenario, **{section: replacement})
    return scenario


def by_address(*, fields):
    return {field.address: field for field in fields}


def by_name(*, fields):
    return {field.name: field for field in fields}


def all_fields(*, blocks):
    return [field for block in blocks for field in block.fields]


def arguments_of(*, calls, name):
    return next(arguments for called, arguments in calls if called == name)


def block_at(*, blocks, address):
    return next(block for block in blocks if block.contains(address=address))
