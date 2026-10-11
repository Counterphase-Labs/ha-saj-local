from __future__ import annotations

import logging
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from custom_components.saj_local import equipment as equipment_module
from custom_components.saj_local.const import (
    CONF_DETECTED_EQUIPMENT,
    CONF_EQUIPMENT,
    CONF_FITTED_EQUIPMENT,
)
from custom_components.saj_local.equipment import (
    EquipmentReport,
    PackReport,
    configured_settings,
    detected_equipment,
    equipment_issue_id,
    pack_summary,
    remove_equipment_issues,
    report_summary,
    resolved_equipment,
    settle_equipment,
    stored_fitted_equipment,
    stored_pack_limit,
)
from custom_components.saj_local.saj.detection import Detected
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.equipment import Detection, Setting
from custom_components.saj_local.saj.models import Equipment

if TYPE_CHECKING:
    from custom_components.saj_local.saj.catalogue import Fit

BATTERY = Equipment.BATTERY
METER = Equipment.METER_B
PROFILE = SimpleNamespace(equipment=frozenset({BATTERY, METER}))
DEVICE = Device("SERIAL", 0x1610, 12000, PROFILE, detected=True)


class FakeConfigEntries:
    def __init__(self) -> None:
        self.updates: list[dict[str, object]] = []

    def async_update_entry(self, entry, *, data) -> None:
        self.updates.append(data)
        entry.data = data


class FakeRegistry:
    def __init__(self) -> None:
        self.removed: list[str] = []

    def async_remove(self, entity_id: str) -> None:
        self.removed.append(entity_id)


class FakeIssues:
    def __init__(self) -> None:
        self.created: dict[str, dict[str, object]] = {}
        self.deleted: list[str] = []
        self.IssueSeverity = SimpleNamespace(WARNING="warning")

    def async_create_issue(self, hass, domain, issue_id, **details) -> None:
        del hass
        self.created[issue_id] = {"domain": domain, **details}

    def async_delete_issue(self, hass, domain, issue_id) -> None:
        del hass, domain
        self.deleted.append(issue_id)


@dataclass
class FakeEntry:
    data: dict[str, object] = field(default_factory=dict)
    options: dict[str, object] = field(default_factory=dict)
    entry_id: str = "entry-1"
    title: str = "Roof inverter"


@dataclass
class Harness:
    hass: SimpleNamespace
    registry: FakeRegistry
    issues: FakeIssues
    probed: list[frozenset[Equipment]] = field(default_factory=list)
    registered: dict[str, SimpleNamespace] = field(default_factory=dict)
    asked_also: list[tuple[str, ...]] = field(default_factory=list)
    readings: dict[str, object] = field(default_factory=dict)
    absent: frozenset[str] = frozenset()
    fits: list[Fit] = field(default_factory=list)
    pack_maximum: int = 1


def _detection(item: Equipment, *, fitted: bool, **values: object) -> Detection:
    return Detection(equipment=item, fitted=fitted, answered=True, values=values)


@pytest.fixture
def harness(monkeypatch) -> Harness:
    registry = FakeRegistry()
    hass = SimpleNamespace(config_entries=FakeConfigEntries())
    issues = FakeIssues()
    harness = Harness(hass=hass, registry=registry, issues=issues)
    monkeypatch.setattr(
        equipment_module, "er", SimpleNamespace(async_get=lambda _hass: registry)
    )
    monkeypatch.setattr(equipment_module, "ir", issues)

    async def names(*, hass, selector_name):
        del hass
        assert selector_name == "equipment"
        return {"battery": "Battery", "meter_b": "Meter B"}

    monkeypatch.setattr(equipment_module, "selector_options", names)

    def absent_keys(*, fit):
        harness.fits.append(fit)
        return harness.absent

    monkeypatch.setattr(equipment_module, "absent_keys", absent_keys)

    def pack_maximum(*, profile):
        del profile
        return harness.pack_maximum

    monkeypatch.setattr(equipment_module, "pack_maximum", pack_maximum)
    monkeypatch.setattr(
        equipment_module,
        "installation_entities",
        lambda **_: dict(harness.registered),
    )
    return harness


def _probing(monkeypatch, harness: Harness, detections: dict[Equipment, Detection]):
    async def detect(*, client, device, probed, also=()):
        del client, device
        harness.probed.append(frozenset(probed))
        harness.asked_also.append(tuple(also))
        return Detected(
            detections={item: detections[item] for item in probed},
            readings=harness.readings,
        )

    monkeypatch.setattr(equipment_module, "detect", detect)


async def _settle_fully(harness: Harness, entry: FakeEntry):
    return await settle_equipment(
        hass=harness.hass, entry=entry, client=object(), device=DEVICE
    )


async def _settle(harness: Harness, entry: FakeEntry):
    device, reports, _ = await _settle_fully(harness, entry)
    return device, reports


@pytest.mark.parametrize(
    ("setting", "memory_and_probe", "outcome"),
    [
        (Setting.AUTOMATIC, (False, True), (True, True)),
        (Setting.AUTOMATIC, (False, False), (False, False)),
        (Setting.AUTOMATIC, (True, True), (True, True)),
        (Setting.AUTOMATIC, (True, False), (True, True)),
        (Setting.FITTED, (False, False), (True, False)),
        (Setting.FITTED, (True, False), (True, True)),
        (Setting.NOT_FITTED, (False, True), (False, False)),
        (Setting.NOT_FITTED, (True, True), (False, False)),
    ],
)
async def test_the_setting_the_memory_and_the_probe_decide_what_is_fitted(
    monkeypatch, harness, setting, memory_and_probe, outcome
):
    remembered, detected = memory_and_probe
    fitted, stored = outcome
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=detected),
            METER: _detection(METER, fitted=False),
        },
    )
    entry = FakeEntry(
        data={CONF_DETECTED_EQUIPMENT: ["battery"] if remembered else []},
        options={CONF_EQUIPMENT: {"battery": setting.value}},
    )

    device, reports = await _settle(harness, entry)

    assert (BATTERY in device.equipment) is fitted
    assert (BATTERY in detected_equipment(entry=entry)) is stored
    assert reports[BATTERY].fitted is fitted
    assert reports[BATTERY].setting is setting


@pytest.mark.parametrize(
    ("options", "probed"),
    [
        ({}, {BATTERY, METER}),
        ({"battery": "fitted"}, {METER}),
        ({"battery": "not_fitted", "meter_b": "fitted"}, set()),
        ({"battery": "automatic"}, {BATTERY, METER}),
    ],
)
async def test_only_equipment_on_automatic_is_probed(
    monkeypatch, harness, options, probed
):
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=True),
        },
    )

    await _settle(harness, FakeEntry(options={CONF_EQUIPMENT: options}))

    assert harness.probed == [probed]


async def test_the_remembered_set_is_stored_before_anything_else_only_when_it_changes(
    monkeypatch, harness, caplog
):
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=False),
        },
    )
    entry = FakeEntry(data={"host": "inverter"})

    with caplog.at_level(logging.INFO):
        await _settle(harness, entry)
        await _settle(harness, entry)

    assert harness.hass.config_entries.updates == [
        {
            "host": "inverter",
            CONF_DETECTED_EQUIPMENT: ["battery"],
            CONF_FITTED_EQUIPMENT: ["battery"],
        }
    ]
    changes = [r for r in caplog.records if "changed" in r.getMessage()]
    assert len(changes) == 1
    assert "battery" in changes[0].getMessage()


async def test_equipment_no_longer_detected_stays_fitted_and_warns_once(
    monkeypatch, harness, caplog
):
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=False, meter_b_status=0),
        },
    )
    entry = FakeEntry(
        data={
            CONF_DETECTED_EQUIPMENT: ["battery", "meter_b"],
            CONF_FITTED_EQUIPMENT: ["battery", "meter_b"],
        }
    )

    with caplog.at_level(logging.WARNING):
        device, reports = await _settle(harness, entry)

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "meter_b" in warnings[0].getMessage()
    assert "'meter_b_status': 0" in warnings[0].getMessage()
    assert device.equipment == {BATTERY, METER}
    assert reports[METER].lapsed is True
    assert reports[BATTERY].lapsed is False
    assert harness.hass.config_entries.updates == []


async def test_nothing_is_warned_for_equipment_that_was_never_detected(
    monkeypatch, harness, caplog
):
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=False),
            METER: _detection(METER, fitted=False),
        },
    )

    with caplog.at_level(logging.WARNING):
        await _settle(harness, FakeEntry())

    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []


@pytest.mark.parametrize(
    ("absent", "removed"),
    [
        (frozenset(), []),
        (frozenset({"meter_b_l1_power"}), ["sensor.saj_meter_b_l1_power"]),
        (
            frozenset({"battery_soc", "meter_b_l1_power", "never_registered"}),
            ["sensor.saj_battery_soc", "sensor.saj_meter_b_l1_power"],
        ),
    ],
)
async def test_registry_entries_of_absent_rows_are_removed_and_no_others(
    monkeypatch, harness, absent, removed
):
    _probing(
        monkeypatch,
        harness,
        {item: _detection(item, fitted=True) for item in (BATTERY, METER)},
    )
    harness.absent = absent
    harness.registered = {
        key: SimpleNamespace(entity_id=f"sensor.saj_{key}")
        for key in ("pv_power", "battery_soc", "meter_b_l1_power", "unknown_row")
    }

    await _settle(harness, FakeEntry())

    assert sorted(harness.registry.removed) == sorted(removed)


async def test_the_rows_that_are_absent_are_judged_by_the_fit_that_was_settled(
    monkeypatch, harness
):
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=False),
        },
    )
    harness.pack_maximum = 4
    harness.readings = {"battery_pack_count": 2}

    await _settle(harness, FakeEntry())

    (fit,) = harness.fits
    assert fit.equipment == {BATTERY}
    assert fit.pack_limit == 2


async def test_the_report_keeps_the_raw_probe_values_and_the_state_of_each_equipment(
    monkeypatch, harness
):
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True, battery_protocol=24),
            METER: _detection(METER, fitted=False, meter_b_status=0),
        },
    )
    entry = FakeEntry(options={CONF_EQUIPMENT: {"meter_b": "fitted"}})

    _, reports = await _settle(harness, entry)

    assert reports == {
        BATTERY: EquipmentReport(
            setting=Setting.AUTOMATIC,
            detection=_detection(BATTERY, fitted=True, battery_protocol=24),
            remembered=True,
            lapsed=False,
            fitted=True,
        ),
        METER: EquipmentReport(
            setting=Setting.FITTED,
            detection=None,
            remembered=False,
            lapsed=False,
            fitted=True,
        ),
    }


def test_the_summary_names_each_equipment_with_its_setting_probe_and_result():
    reports = {
        BATTERY: EquipmentReport(
            setting=Setting.AUTOMATIC,
            detection=_detection(BATTERY, fitted=True, battery_protocol=24),
            remembered=True,
            lapsed=False,
            fitted=True,
        ),
        METER: EquipmentReport(
            setting=Setting.NOT_FITTED,
            detection=None,
            remembered=False,
            lapsed=True,
            fitted=False,
        ),
    }

    assert report_summary(reports=reports) == {
        "battery": {
            "setting": "automatic",
            "probe_values": {"battery_protocol": 24},
            "probe_answered": True,
            "remembered": True,
            "remembered_but_not_detected": False,
            "fitted": True,
        },
        "meter_b": {
            "setting": "not_fitted",
            "probe_values": None,
            "probe_answered": None,
            "remembered": False,
            "remembered_but_not_detected": True,
            "fitted": False,
        },
    }


@pytest.mark.parametrize(
    ("options", "data", "inherited", "fitted"),
    [
        ({}, {}, True, set()),
        ({}, {CONF_FITTED_EQUIPMENT: ["battery"]}, True, {BATTERY}),
        ({}, {CONF_FITTED_EQUIPMENT: ["battery"]}, False, set()),
        ({CONF_EQUIPMENT: {"meter_b": "fitted"}}, {}, True, {METER}),
        ({CONF_EQUIPMENT: {"meter_b": "fitted"}}, {}, False, {METER}),
        (
            {CONF_EQUIPMENT: {"battery": "not_fitted"}},
            {CONF_FITTED_EQUIPMENT: ["battery"]},
            True,
            set(),
        ),
        ({}, {CONF_DETECTED_EQUIPMENT: ["battery"]}, True, set()),
    ],
)
def test_the_stored_view_follows_the_saved_settings_and_the_last_resolved_set(
    options, data, inherited, fitted
):
    entry = FakeEntry(data=data, options=options)

    assert stored_fitted_equipment(entry=entry, inherited=inherited) == fitted


def test_the_stored_view_can_apply_settings_that_are_not_saved_yet():
    entry = FakeEntry(
        data={CONF_FITTED_EQUIPMENT: ["battery"]},
        options={CONF_EQUIPMENT: {"battery": "not_fitted"}},
    )

    fitted = stored_fitted_equipment(
        entry=entry, settings={BATTERY: Setting.AUTOMATIC, METER: Setting.FITTED}
    )

    assert fitted == {BATTERY, METER}


async def test_equipment_assumed_for_an_unanswered_probe_is_fitted_but_never_remembered(
    monkeypatch, harness, caplog
):
    unanswered = Detection(equipment=BATTERY, fitted=True, answered=False, values={})
    _probing(
        monkeypatch,
        harness,
        {BATTERY: unanswered, METER: _detection(METER, fitted=False)},
    )
    entry = FakeEntry()

    device, reports = await _settle(harness, entry)

    assert device.equipment == {BATTERY}
    assert detected_equipment(entry=entry) == set()
    assert resolved_equipment(entry=entry) == {BATTERY}
    assert reports[BATTERY].remembered is False

    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=False, battery_protocol=0),
            METER: _detection(METER, fitted=False),
        },
    )
    harness.registered = {"battery_soc": SimpleNamespace(entity_id="sensor.soc")}
    harness.absent = frozenset({"battery_soc"})

    with caplog.at_level(logging.WARNING):
        device, reports = await _settle(harness, entry)

    assert device.equipment == set()
    assert harness.registry.removed == ["sensor.soc"]
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []
    assert resolved_equipment(entry=entry) == set()


async def test_an_answered_fitted_probe_is_remembered_and_stored_with_the_fitted_set(
    monkeypatch, harness
):
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=False),
        },
    )
    entry = FakeEntry()

    await _settle(harness, entry)

    assert detected_equipment(entry=entry) == {BATTERY}
    assert resolved_equipment(entry=entry) == {BATTERY}


@pytest.mark.parametrize(
    ("saved", "logged"),
    [
        (({CONF_FITTED_EQUIPMENT: ["battery"]}, {"meter_b": "fitted"}), True),
        (({CONF_FITTED_EQUIPMENT: ["battery"]}, {}), False),
        (({CONF_FITTED_EQUIPMENT: ["battery", "meter_b"]}, {}), True),
    ],
)
async def test_the_change_is_logged_only_when_the_fitted_set_changes(
    monkeypatch, harness, caplog, saved, *, logged
):
    data, options = saved
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=False),
        },
    )
    entry = FakeEntry(data=data, options={CONF_EQUIPMENT: options})

    with caplog.at_level(logging.INFO):
        await _settle(harness, entry)

    assert any("changed" in r.getMessage() for r in caplog.records) is logged
    assert harness.hass.config_entries.updates


def test_settings_are_read_as_enumerations():
    entry = FakeEntry(options={CONF_EQUIPMENT: {"ev_charger": "not_fitted"}})

    assert configured_settings(entry=entry) == {
        Equipment.EV_CHARGER: Setting.NOT_FITTED
    }


LAPSE_ISSUE = equipment_issue_id(entry_id="entry-1", equipment=METER)
REMEMBERED_METER = {
    CONF_DETECTED_EQUIPMENT: ["battery", "meter_b"],
    CONF_FITTED_EQUIPMENT: ["battery", "meter_b"],
}


def _meter_reads(monkeypatch, harness, *, fitted: bool) -> None:
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=fitted),
        },
    )


async def test_equipment_that_was_detected_and_now_is_not_raises_a_repair_issue(
    monkeypatch, harness
):
    _meter_reads(monkeypatch, harness, fitted=False)

    await _settle(harness, FakeEntry(data=REMEMBERED_METER))

    assert harness.issues.created == {
        LAPSE_ISSUE: {
            "domain": "saj_local",
            "is_fixable": False,
            "severity": "warning",
            "translation_key": "equipment_not_detected",
            "translation_placeholders": {
                "installation": "Roof inverter",
                "equipment": "Meter B",
            },
        }
    }


@pytest.mark.parametrize(
    ("data", "options", "meter_fitted"),
    [
        ({}, {}, False),
        (REMEMBERED_METER, {}, True),
        (REMEMBERED_METER, {CONF_EQUIPMENT: {"meter_b": "fitted"}}, False),
        (REMEMBERED_METER, {CONF_EQUIPMENT: {"meter_b": "not_fitted"}}, False),
    ],
)
async def test_no_repair_issue_is_raised_unless_remembered_equipment_lapsed(
    monkeypatch, harness, data, options, meter_fitted
):
    _meter_reads(monkeypatch, harness, fitted=meter_fitted)

    await _settle(harness, FakeEntry(data=data, options=options))

    assert harness.issues.created == {}
    assert LAPSE_ISSUE in harness.issues.deleted


async def test_the_repair_issue_is_removed_at_the_setup_that_detects_it_again(
    monkeypatch, harness
):
    entry = FakeEntry(data=REMEMBERED_METER)
    _meter_reads(monkeypatch, harness, fitted=False)
    await _settle(harness, entry)
    assert harness.issues.deleted.count(LAPSE_ISSUE) == 0

    _meter_reads(monkeypatch, harness, fitted=True)
    await _settle(harness, entry)

    assert harness.issues.deleted.count(LAPSE_ISSUE) == 1


def test_removing_the_installation_removes_the_issue_of_every_equipment(harness):
    remove_equipment_issues(hass=harness.hass, entry=FakeEntry())

    assert harness.issues.deleted == [
        equipment_issue_id(entry_id="entry-1", equipment=item) for item in Equipment
    ]


PACK_COUNT = "battery_pack_count"
HIGHEST = "highest_pack_count"


def _battery_reads(monkeypatch, harness) -> None:
    _probing(
        monkeypatch,
        harness,
        {
            BATTERY: _detection(BATTERY, fitted=True),
            METER: _detection(METER, fitted=False),
        },
    )


@pytest.mark.parametrize(
    ("maximum", "battery", "asked"),
    [
        (4, None, [(PACK_COUNT,)]),
        (4, "automatic", [(PACK_COUNT,)]),
        (4, "fitted", [(PACK_COUNT,)]),
        (4, "not_fitted", [()]),
        (1, None, [()]),
        (1, "fitted", [()]),
    ],
)
async def test_the_pack_count_is_read_only_for_a_battery_and_a_model_with_several_packs(
    monkeypatch, harness, maximum, battery, asked
):
    _battery_reads(monkeypatch, harness)
    harness.pack_maximum = maximum
    options = {} if battery is None else {CONF_EQUIPMENT: {"battery": battery}}

    await _settle(harness, FakeEntry(options=options))

    assert harness.asked_also == asked


@pytest.mark.parametrize(
    ("stored", "reading", "limit"),
    [
        (None, 2, 2),
        (None, 4, 4),
        (2, 3, 3),
        (3, 2, 3),
        (3, 0, 3),
        (3, 5, 3),
        (3, None, 3),
        (None, 0, None),
        (None, 5, None),
        (None, None, None),
    ],
)
async def test_the_highest_valid_pack_count_seen_is_the_limit_and_never_goes_down(
    monkeypatch, harness, stored, reading, limit
):
    _battery_reads(monkeypatch, harness)
    harness.pack_maximum = 4
    harness.readings = {PACK_COUNT: reading}
    entry = FakeEntry(data={} if stored is None else {HIGHEST: stored})

    device, _, packs = await _settle_fully(harness, entry)

    assert device.pack_limit == limit
    assert packs.limit == limit
    assert packs.count_read == reading
    assert entry.data.get(HIGHEST) == limit


async def test_a_battery_set_to_not_fitted_forgets_the_pack_limit(monkeypatch, harness):
    _battery_reads(monkeypatch, harness)
    harness.pack_maximum = 4
    entry = FakeEntry(
        data={HIGHEST: 3}, options={CONF_EQUIPMENT: {"battery": "not_fitted"}}
    )

    device, _, packs = await _settle_fully(harness, entry)

    assert device.pack_limit is None
    assert packs.limit is None
    assert HIGHEST not in entry.data


async def test_an_unchanged_pack_limit_is_not_stored_again(monkeypatch, harness):
    _battery_reads(monkeypatch, harness)
    harness.pack_maximum = 4
    harness.readings = {PACK_COUNT: 2}
    entry = FakeEntry()

    await _settle(harness, entry)
    await _settle(harness, entry)

    assert len(harness.hass.config_entries.updates) == 1


@pytest.mark.parametrize(("inherited", "limit"), [(True, 3), (False, None)])
def test_the_stored_pack_limit_is_inherited_unless_the_unit_was_replaced(
    inherited, limit
):
    entry = FakeEntry(data={HIGHEST: 3})

    assert stored_pack_limit(entry=entry, inherited=inherited) == limit


def test_the_pack_summary_names_the_count_read_and_the_limit_in_use():
    assert pack_summary(packs=PackReport(count_read=3, limit=2)) == {
        "count_read": 3,
        "limit_in_use": 2,
    }
