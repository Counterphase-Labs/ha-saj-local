from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import REDACTED

from .const import (
    CONF_ALLOW_CONTROL,
    CONF_MODEL,
    CONF_PREFIX,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN_PLACEHOLDER,
    KEY_PLACEHOLDER,
    SCHEDULE_ON,
    fixed_entity_id,
)
from .equipment import pack_summary, report_summary
from .issues import open_issue_keys, open_refusals
from .saj.budget import BUDGET_PER_MINUTE
from .saj.catalogue import device_registers
from .saj.definitions import Quantity
from .saj.faults import decode
from .saj.log import mask_serial

REDACTED_PREFIX = "[redacted]"
ADDRESS_FORMAT = "#06x"
WORD_FORMAT = "#06x"
AGE_DECIMALS = 1

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .saj.health import Break, Region
    from .saj.memory import FailureEntry, RegisterEntry, Snapshot


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    runtime = entry.runtime_data
    coordinator = runtime.coordinator
    poller = coordinator.poller
    now = hass.loop.time()
    return {
        "model_selection": entry.data[CONF_MODEL],
        "serial": mask_serial(serial=runtime.device.serial),
        "profile": runtime.device.profile.key,
        "profile_detected": runtime.device.detected,
        "profile_hand_verified": runtime.device.profile.hand_verified,
        "device_type": runtime.device.device_type,
        "rated_power_w": runtime.device.rated_power,
        "poll_interval_seconds": entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        ),
        "entity_id_pattern": fixed_entity_id(
            domain=DOMAIN_PLACEHOLDER,
            prefix=REDACTED_PREFIX if entry.options.get(CONF_PREFIX, "") else "",
            key=KEY_PLACEHOLDER,
        ),
        "equipment": report_summary(reports=runtime.equipment),
        "battery_packs": pack_summary(packs=runtime.packs),
        "enabled_keys": sorted(coordinator.enabled_keys),
        "connected": runtime.client.is_connected(),
        "last_update_success": coordinator.last_update_success,
        "last_error": coordinator.last_error,
        "cadences": [
            {
                "default": plan.default,
                "interval_seconds": plan.interval,
                "keys": sorted(plan.keys),
                "requests_per_read": plan.requests,
            }
            for plan in poller.cadence_plans()
        ],
        "planned_requests_per_minute": poller.planned_load(),
        "request_budget_per_minute": BUDGET_PER_MINUTE,
        "last_cycle_read": sorted(coordinator.last_read),
        "refused_keys": {
            key: {
                "exception_code": refusal.code,
                "consecutive_refusals": refusal.count,
                "suspended": refusal.retest_at is not None,
                "next_retest_in_seconds": None
                if refusal.retest_at is None
                else max(0.0, refusal.retest_at - now),
            }
            for key, refusal in poller.refusals.items()
        },
        "faults": _fault_summary(coordinator=coordinator),
        "repair_issues": {
            "open": open_issue_keys(hass=hass, entry=entry),
            "refused_keys": sorted(open_refusals(hass=hass, entry=entry)),
        },
        "failing_for_seconds": coordinator.guard.failing_for(now=now),
        "consecutive_failed_cycles": poller.consecutive_failures,
        "backoff_seconds": poller.backoff_seconds,
        "late_frames_discarded": runtime.client.late_frames_discarded,
        "stale_reconnects": poller.stale_reconnects,
        "unknown_codes": _unknown_codes(coordinator=coordinator),
        "breaks": [_break_summary(block=block) for block in _ordered(poller.breaks)],
        "narrowing": [_region_summary(region=region) for region in poller.narrowing],
        **_control_summary(entry=entry, coordinator=coordinator, now=now),
        "power_control": _power_control_summary(hass=hass, coordinator=coordinator),
        "register_snapshot": _snapshot_summary(
            snapshot=runtime.client.memory.snapshot(fit=runtime.device.fit)
        ),
    }


def _snapshot_summary(*, snapshot: Snapshot) -> dict[str, Any]:
    return {
        "registers": [_register_entry(entry=entry) for entry in snapshot.registers],
        "failed": [_failure_entry(entry=entry) for entry in snapshot.failed],
    }


def _register_entry(*, entry: RegisterEntry) -> dict[str, Any]:
    return {
        "address": format(entry.address, ADDRESS_FORMAT),
        "key": entry.key,
        "words": REDACTED
        if entry.private
        else [format(word, WORD_FORMAT) for word in entry.words],
        "age_seconds": round(entry.age_seconds, AGE_DECIMALS),
    }


def _failure_entry(*, entry: FailureEntry) -> dict[str, Any]:
    return {
        "address": format(entry.address, ADDRESS_FORMAT),
        "count": entry.count,
        "outcome": entry.outcome.value,
        "exception_code": entry.exception_code,
        "age_seconds": round(entry.age_seconds, AGE_DECIMALS),
    }


def _control_summary(
    *, entry: ConfigEntry, coordinator: Any, now: float
) -> dict[str, Any]:
    allowance = coordinator.guard.allowance
    writes = coordinator.writes
    last = writes.last
    return {
        "control_enabled": entry.options.get(CONF_ALLOW_CONTROL, False),
        "write_allowance": {
            "limit": allowance.limit,
            "window_seconds": allowance.window,
            "used": allowance.used(now=now),
        },
        "writes_acknowledged": writes.acknowledged,
        "writes_rejected": writes.rejected,
        "writes_unconfirmed": writes.unconfirmed,
        "last_write": None
        if last is None
        else {
            "key": last.key,
            "outcome": last.outcome,
            "exception_code": last.exception_code,
        },
        "ems_heartbeat_interval_seconds": coordinator.heartbeat_interval,
        "ems_functions_owned": sorted(coordinator.ems.owned),
        "ems_beats_sent": writes.beats_sent,
        "ems_beats_dropped": writes.beats_dropped,
    }


def _power_control_summary(*, hass: HomeAssistant, coordinator: Any) -> dict[str, Any]:
    return {
        "functions": {
            function.value: {
                "method": coordinator.power_controls[function].method_name,
                "running": coordinator.power_running(function=function),
                "owned": function in coordinator.ems.owned,
            }
            for function in coordinator.power_offered
        },
        "schedules": [
            {
                "function": schedule.function.value,
                "schedule": schedule.entity_id,
                "on": _schedule_on(hass=hass, entity_id=schedule.entity_id),
                "outstanding": coordinator.outstanding.get(schedule.function),
            }
            for schedule in coordinator.schedules
        ],
    }


def _schedule_on(*, hass: HomeAssistant, entity_id: str) -> bool:
    state = hass.states.get(entity_id)
    return state is not None and state.state == SCHEDULE_ON


def _ordered(breaks: Iterable[Break]) -> list[Break]:
    return sorted(breaks, key=lambda block: (block.before, block.after))


def _break_summary(*, block: Break) -> dict[str, str]:
    return {
        "before": format(block.before, ADDRESS_FORMAT),
        "after": format(block.after, ADDRESS_FORMAT),
    }


def _region_summary(*, region: Region) -> dict[str, str | int]:
    return {
        **_break_summary(block=region.hull),
        "rows": len(region.rows),
    }


def _unknown_codes(*, coordinator: Any) -> dict[str, float]:
    if coordinator.data is None:
        return {}
    device = coordinator.device
    codes: dict[str, float] = {}
    for register in device_registers(fit=device.fit):
        value = coordinator.data.get(key=register.key)
        if (
            register.options is not None
            and isinstance(value, int | float)
            and int(value) not in register.options
        ):
            codes[register.key] = value
    return codes


def _fault_summary(*, coordinator: Any) -> dict[str, Any]:
    device = coordinator.device
    registers = device_registers(fit=device.fit)
    fault_map = device.profile.faults
    values = coordinator.data.values if coordinator.data is not None else {}
    summary: dict[str, Any] = {}
    for equipment in dict.fromkeys(
        register.equipment for register in registers if not register.exposed
    ):
        names = {
            register.key
            for register in registers
            if not register.exposed and register.equipment == equipment
        }
        words = fault_map.registers_of(
            values={key: value for key, value in values.items() if key in names}
        )
        decoded = decode(fault_map=fault_map, words=words)
        summary["inverter" if equipment is None else equipment.value] = {
            "words": {
                format(register, ADDRESS_FORMAT): format(value, "#010x")
                for register, value in words.items()
            },
            "active": sorted(decoded.active),
            "unrecognised": sorted(str(source) for source in decoded.unrecognised),
        }
    summary["pack_codes"] = {
        register.key: values[register.key]
        for register in registers
        if register.quantity is Quantity.PROBLEM
        and register.combination is None
        and register.key in values
    }
    return summary
