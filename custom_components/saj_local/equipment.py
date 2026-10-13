import logging
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_DETECTED_EQUIPMENT,
    CONF_EQUIPMENT,
    CONF_FITTED_EQUIPMENT,
    CONF_HIGHEST_PACK_COUNT,
    installation_entities,
)
from .issues import sync_lapse_issues
from .saj.catalogue import absent_keys, pack_maximum
from .saj.detection import detect
from .saj.equipment import (
    BATTERY_PACK_COUNT,
    Detection,
    Setting,
    next_pack_limit,
    resolve,
    stored_fitted,
    to_probe,
)
from .saj.models import ALL_EQUIPMENT, Equipment

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .saj.client import RegisterReader
    from .saj.codec import Value
    from .saj.device import Device

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class EquipmentReport:
    setting: Setting
    detection: Detection | None
    remembered: bool
    lapsed: bool
    fitted: bool


@dataclass(frozen=True)
class PackReport:
    count_read: Value
    limit: int | None


def settings_of(*, stored: Mapping[str, str]) -> dict[Equipment, Setting]:
    return {Equipment(name): Setting(value) for name, value in stored.items()}


def configured_settings(*, entry: ConfigEntry) -> dict[Equipment, Setting]:
    return settings_of(stored=entry.options.get(CONF_EQUIPMENT, {}))


def detected_equipment(*, entry: ConfigEntry) -> frozenset[Equipment]:
    return frozenset(
        Equipment(name) for name in entry.data.get(CONF_DETECTED_EQUIPMENT, ())
    )


def resolved_equipment(*, entry: ConfigEntry) -> frozenset[Equipment]:
    return frozenset(
        Equipment(name) for name in entry.data.get(CONF_FITTED_EQUIPMENT, ())
    )


def stored_pack_limit(*, entry: ConfigEntry, inherited: bool = True) -> int | None:
    return entry.data.get(CONF_HIGHEST_PACK_COUNT) if inherited else None


def stored_fitted_equipment(
    *,
    entry: ConfigEntry,
    settings: Mapping[Equipment, Setting] | None = None,
    inherited: bool = True,
) -> frozenset[Equipment]:
    return stored_fitted(
        equipment=ALL_EQUIPMENT,
        settings=configured_settings(entry=entry) if settings is None else settings,
        resolved=resolved_equipment(entry=entry) if inherited else (),
    )


async def settle_equipment(
    *,
    hass: HomeAssistant,
    entry: ConfigEntry,
    client: RegisterReader,
    device: Device,
) -> tuple[Device, dict[Equipment, EquipmentReport], PackReport]:
    equipment = device.profile.equipment
    settings = configured_settings(entry=entry)
    detected = detected_equipment(entry=entry)
    resolved = resolved_equipment(entry=entry)
    battery = settings.get(Equipment.BATTERY, Setting.AUTOMATIC)
    maximum = pack_maximum(profile=device.profile)
    reads_pack_count = maximum > 1 and battery is not Setting.NOT_FITTED
    detection = await detect(
        client=client,
        device=device,
        probed=to_probe(settings=settings, equipment=equipment),
        also=(BATTERY_PACK_COUNT,) if reads_pack_count else (),
    )
    outcome = resolve(
        equipment=equipment,
        settings=settings,
        remembered=detected,
        detections=detection.detections,
    )
    count_read = detection.readings.get(BATTERY_PACK_COUNT)
    stored_limit = stored_pack_limit(entry=entry)
    limit = next_pack_limit(
        stored=stored_limit, reading=count_read, maximum=maximum, battery=battery
    )
    for lapsed in sorted(outcome.lapsed):
        _LOGGER.warning(
            "SAJ %s was detected before but its probe now reads %s;"
            " it stays fitted until it is set to Not fitted",
            lapsed,
            dict(detection.detections[lapsed].values),
        )
    await sync_lapse_issues(
        hass=hass, entry=entry, equipment=equipment, lapsed=outcome.lapsed
    )
    if outcome.fitted != resolved:
        _LOGGER.info(
            "SAJ fitted equipment changed from %s to %s",
            sorted(resolved),
            sorted(outcome.fitted),
        )
    if limit != stored_limit:
        _LOGGER.debug("SAJ battery pack limit moved from %s to %s", stored_limit, limit)
    if (
        outcome.remembered != detected
        or outcome.fitted != resolved
        or limit != stored_limit
    ):
        hass.config_entries.async_update_entry(
            entry,
            data=_settled_data(
                data=entry.data,
                remembered=outcome.remembered,
                fitted=outcome.fitted,
                limit=limit,
            ),
        )
    settled = replace(device, equipment=outcome.fitted, pack_limit=limit)
    _remove_absent_entities(hass=hass, entry=entry, device=settled)
    reports = {
        item: EquipmentReport(
            setting=settings.get(item, Setting.AUTOMATIC),
            detection=detection.detections.get(item),
            remembered=item in outcome.remembered,
            lapsed=item in outcome.lapsed,
            fitted=item in outcome.fitted,
        )
        for item in sorted(equipment)
    }
    return settled, reports, PackReport(count_read=count_read, limit=limit)


def _settled_data(
    *,
    data: Mapping[str, object],
    remembered: Collection[Equipment],
    fitted: Collection[Equipment],
    limit: int | None,
) -> dict[str, object]:
    settled = {
        **data,
        CONF_DETECTED_EQUIPMENT: sorted(remembered),
        CONF_FITTED_EQUIPMENT: sorted(fitted),
    }
    if limit is None:
        settled.pop(CONF_HIGHEST_PACK_COUNT, None)
    else:
        settled[CONF_HIGHEST_PACK_COUNT] = limit
    return settled


def _remove_absent_entities(
    *, hass: HomeAssistant, entry: ConfigEntry, device: Device
) -> None:
    absent = absent_keys(fit=device.fit)
    registry = er.async_get(hass)
    for key, registered in installation_entities(
        hass=hass, entry_id=entry.entry_id
    ).items():
        if key in absent:
            registry.async_remove(registered.entity_id)


def report_summary(
    *, reports: Mapping[Equipment, EquipmentReport]
) -> dict[str, object]:
    return {
        item.value: {
            "setting": report.setting.value,
            "probe_values": None
            if report.detection is None
            else dict(report.detection.values),
            "probe_answered": None
            if report.detection is None
            else report.detection.answered,
            "remembered": report.remembered,
            "remembered_but_not_detected": report.lapsed,
            "fitted": report.fitted,
        }
        for item, report in reports.items()
    }


def pack_summary(*, packs: PackReport) -> dict[str, object]:
    return {"count_read": packs.count_read, "limit_in_use": packs.limit}
