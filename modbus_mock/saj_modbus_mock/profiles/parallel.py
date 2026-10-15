"""Parallel-system block, served by every model that documents it."""

from typing import TYPE_CHECKING

from .fields import I16, I32, U16, counter_group, fixed, live

if TYPE_CHECKING:
    from saj_modbus_mock.registers import Field
    from saj_modbus_mock.scenario import Scenario

POWER_REGISTERS = (
    (0x4204, 0x420C, "pv_w", U16),
    (0x4205, 0x420D, "battery_w", I16),
    (0x4206, 0x420E, "grid_w", I16),
    (0x4207, 0x420F, "load_w", U16),
    (0x4208, 0x4210, "backup_w", I16),
    (0x420A, 0x4211, "grid_load_w", I16),
)
# The H2 document gives each power as one 16-bit register and no high word.
SINGLE_POWER_REGISTERS = (
    (0x4204, "pv_w", U16),
    (0x4205, "battery_w", I16),
    (0x4206, "grid_w", I16),
    (0x4207, "load_w", I16),
    (0x4208, "backup_w", U16),
    (0x420A, "grid_load_w", U16),
)
ENERGY_GROUPS = (
    (0x4215, "pv", "pv"),
    (0x421D, "bat_charge", "battery_charge"),
    (0x4225, "bat_discharge", "battery_discharge"),
    (0x422D, "sell", "sell_one"),
    (0x4235, "", "sell_two"),
    (0x423D, "", "sell_three"),
    (0x4245, "feed_in", "feed_in_one"),
    (0x424D, "", "feed_in_two"),
    (0x4255, "", "feed_in_three"),
    (0x425D, "load", "load"),
)
EXTENDED_ENERGY_GROUPS = (
    (0x4265, "feed_in", "vector_feed_in"),
    (0x426D, "sell", "vector_sell"),
    (0x4275, "ext_pv", "pv_meter"),
)


def parallel_fields(*, scenario: Scenario, extended: bool) -> list[Field]:
    """Serve the HS3 layout when `extended`, else the narrower H2 layout."""
    inverters = scenario.parallel.inverters
    fields = [
        fixed(address=0x4200, name="parallel_mode", value=0),
        fixed(address=0x4201, name="parallel_id", value=0),
        fixed(address=0x4202, name="parallel_count", value=inverters),
        fixed(address=0x4203, name="parallel_real_count", value=inverters),
        live(address=0x4209, name="parallel_soc", source="parallel_soc_percent"),
        live(
            address=0x420B,
            name="parallel_total_capacity",
            source="parallel_capacity_ah",
        ),
    ]
    if extended:
        fields.append(
            live(
                address=0x4212,
                name="parallel_meter_b_power",
                source="ext_pv_w",
                enc=I32,
            )
        )
        fields += _split_powers()
    else:
        fields += [
            live(
                address=address,
                name=f"parallel_{key}",
                source=f"parallel_{key}",
                enc=encoding,
            )
            for address, key, encoding in SINGLE_POWER_REGISTERS
        ]
    groups = ENERGY_GROUPS + (EXTENDED_ENERGY_GROUPS if extended else ())
    for start, base, name in groups:
        fields += counter_group(
            start=start,
            base=base,
            name=f"parallel_{name}",
            present=bool(base),
            parallel=True,
        )
    return fields


def _split_powers() -> list[Field]:
    fields: list[Field] = []
    for low, high, key, high_encoding in POWER_REGISTERS:
        fields.append(
            live(address=low, name=f"parallel_{key}_low", source=f"parallel_{key}_low")
        )
        fields.append(
            live(
                address=high,
                name=f"parallel_{key}_high",
                source=f"parallel_{key}_high",
                enc=high_encoding,
            )
        )
    return fields
