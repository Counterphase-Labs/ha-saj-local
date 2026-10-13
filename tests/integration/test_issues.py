import logging
from types import SimpleNamespace

import pytest
from homeassistant.helpers import issue_registry as real_issue_registry

from custom_components.saj_local import issues as issues_module
from custom_components.saj_local.issues import (
    ModelFinding,
    check_unreachable,
    clear_model_issues,
    clear_unreachable,
    equipment_issue_id,
    issue_id,
    log_fixed,
    model_finding,
    model_issue_open,
    open_issue_keys,
    open_refusals,
    raise_identity_issue,
    raise_model_issue,
    remove_issues,
    sync_lapse_issues,
    sync_refusals,
)
from custom_components.saj_local.saj import errors as saj_errors
from custom_components.saj_local.saj.guard import EndpointGuard
from custom_components.saj_local.saj.models import Equipment
from custom_components.saj_local.saj.poller import IdentityChangedError

ENTRY = SimpleNamespace(
    entry_id="entry-1",
    title="Roof inverter",
    unique_id="SERIAL-1",
    data={"host": "inverter", "port": 1502},
)
HASS = SimpleNamespace()
LABEL = "Roof inverter (xxxxxL-1)"
PROFILE_A = SimpleNamespace(key="a", display_name="HS3")
PROFILE_B = SimpleNamespace(key="b", display_name="H2")


class FakeIssues:
    IssueSeverity = real_issue_registry.IssueSeverity

    def __init__(self) -> None:
        self.issues: dict[str, SimpleNamespace] = {}
        self.deleted: list[str] = []

    def async_get(self, hass):
        assert hass is HASS
        return self

    def async_get_issue(self, domain, issue_id):
        assert domain == "saj_local"
        return self.issues.get(issue_id)

    def async_create_issue(self, hass, domain, issue_id, **details) -> None:
        assert hass is HASS
        self.issues[issue_id] = SimpleNamespace(domain=domain, **details)

    def async_delete_issue(self, hass, domain, issue_id) -> None:
        assert hass is HASS
        assert domain == "saj_local"
        self.deleted.append(issue_id)
        self.issues.pop(issue_id, None)


@pytest.fixture
def registry(monkeypatch) -> FakeIssues:
    fake = FakeIssues()
    monkeypatch.setattr(issues_module, "ir", fake)
    monkeypatch.setattr(issues_module, "installation_entities", lambda **_: {})
    return fake


def _id(key: str) -> str:
    return issue_id(entry_id="entry-1", key=key)


def test_an_issue_id_belongs_to_one_installation():
    assert _id("model_mismatch") == "entry-1_model_mismatch"
    assert (
        equipment_issue_id(entry_id="entry-1", equipment=Equipment.METER_B)
        == "entry-1_meter_b_not_detected"
    )


@pytest.mark.parametrize(
    ("error", "key", "placeholders"),
    [
        (
            saj_errors.ModelMismatchError(selected=PROFILE_A, detected=PROFILE_B),
            "model_mismatch",
            {"selected_model": "HS3", "detected_model": "H2"},
        ),
        (
            saj_errors.UnsupportedDeviceError(0x1234),
            "unsupported_device",
            {"device_type": "0x1234"},
        ),
        (
            IdentityChangedError(serial="OTHER"),
            "identity_mismatch",
            {"found_serial": "OTHER"},
        ),
    ],
)
def test_the_errors_that_say_the_device_is_not_the_configured_one_are_findings(
    error, key, placeholders
):
    finding = model_finding(error=error)

    assert finding.key == key
    assert finding.placeholders == placeholders


@pytest.mark.parametrize(
    "error",
    [saj_errors.UnknownModelError("x"), TimeoutError(), ValueError("bad")],
)
def test_any_other_error_is_no_model_finding(error):
    assert model_finding(error=error) is None


@pytest.mark.parametrize(
    ("finding", "named"),
    [
        (
            ModelFinding(
                key="model_mismatch",
                placeholders={"selected_model": "A", "detected_model": "B"},
            ),
            "B",
        ),
        (
            ModelFinding(key="identity_mismatch", placeholders={"found_serial": "S"}),
            "S",
        ),
        (
            ModelFinding(key="unsupported_device", placeholders={"device_type": "0x1"}),
            "0x1",
        ),
    ],
)
def test_a_finding_names_what_was_found_at_the_address(finding, named):
    assert finding.named == named


def test_a_model_mismatch_is_a_fixable_error_naming_both_models(registry):
    finding = ModelFinding(
        key="model_mismatch",
        placeholders={"selected_model": "HS3", "detected_model": "H2"},
    )

    raise_model_issue(hass=HASS, entry=ENTRY, finding=finding)

    issue = registry.issues[_id("model_mismatch")]
    assert issue.is_fixable is True
    assert issue.severity == "error"
    assert issue.translation_key == "model_mismatch"
    assert issue.translation_placeholders == {
        "installation": "Roof inverter",
        "selected_model": "HS3",
        "detected_model": "H2",
    }
    assert issue.data == {
        "entry_id": "entry-1",
        "issue": "model_mismatch",
        "named": "H2",
    }


def test_an_identity_mismatch_names_the_approved_serial_and_the_serial_found(
    registry,
):
    raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")

    issue = registry.issues[_id("identity_mismatch")]
    assert issue.is_fixable is True
    assert issue.translation_placeholders == {
        "installation": "Roof inverter",
        "found_serial": "OTHER",
        "approved_serial": "SERIAL-1",
    }
    assert issue.data == {
        "entry_id": "entry-1",
        "issue": "identity_mismatch",
        "named": "OTHER",
    }


def test_an_installation_without_a_serial_names_none_as_approved(registry):
    entry = SimpleNamespace(**{**vars(ENTRY), "unique_id": None})

    raise_identity_issue(hass=HASS, entry=entry, serial="OTHER")

    placeholders = registry.issues[_id("identity_mismatch")].translation_placeholders
    assert placeholders["approved_serial"] == ""


def test_an_unsupported_device_cannot_be_fixed_from_the_issue(registry):
    finding = ModelFinding(
        key="unsupported_device", placeholders={"device_type": "0x1234"}
    )

    raise_model_issue(hass=HASS, entry=ENTRY, finding=finding)

    assert registry.issues[_id("unsupported_device")].is_fixable is False


def test_only_one_model_issue_is_open_at_a_time(registry):
    raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")
    assert model_issue_open(hass=HASS, entry=ENTRY)

    raise_model_issue(
        hass=HASS,
        entry=ENTRY,
        finding=ModelFinding(
            key="unsupported_device", placeholders={"device_type": "0x1"}
        ),
    )

    assert list(registry.issues) == [_id("unsupported_device")]


def test_raising_a_model_issue_removes_an_open_unreachable_issue(registry):
    check_unreachable(hass=HASS, entry=ENTRY, guard=_guard(failing_for=1), now=2000)
    assert _id("endpoint_unreachable") in registry.issues

    raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")

    assert list(registry.issues) == [_id("identity_mismatch")]


def test_clearing_the_model_issues_removes_each_of_them(registry):
    raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")

    clear_model_issues(hass=HASS, entry=ENTRY)

    assert registry.issues == {}
    assert not model_issue_open(hass=HASS, entry=ENTRY)
    assert set(registry.deleted[-3:]) == {
        _id(key)
        for key in ("model_mismatch", "identity_mismatch", "unsupported_device")
    }


def test_an_issue_is_logged_once_when_raised_and_once_when_cleared(registry, caplog):
    with caplog.at_level(logging.INFO):
        raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")
        raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")
        clear_model_issues(hass=HASS, entry=ENTRY)
        clear_model_issues(hass=HASS, entry=ENTRY)

    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [
        (
            logging.WARNING,
            f"{LABEL}: Repair issue identity_mismatch raised",
        ),
        (
            logging.INFO,
            f"{LABEL}: Repair issue identity_mismatch cleared",
        ),
    ]


def test_a_fixed_issue_is_logged_as_cleared_in_the_same_form(caplog):
    with caplog.at_level(logging.INFO):
        log_fixed(entry=ENTRY, key="identity_mismatch")

    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [
        (logging.INFO, f"{LABEL}: Repair issue identity_mismatch cleared")
    ]


def _guard(*, failing_for: float | None) -> EndpointGuard:
    guard = EndpointGuard()
    if failing_for is not None:
        guard.failed(now=100.0, base_delay=10)
    return guard


@pytest.mark.parametrize(
    ("elapsed", "raised"),
    [(None, False), (0, False), (899, False), (900, True), (5000, True)],
)
def test_the_endpoint_is_unreachable_after_fifteen_minutes_of_failing(
    registry, elapsed, raised
):
    guard = _guard(failing_for=elapsed)

    check_unreachable(hass=HASS, entry=ENTRY, guard=guard, now=100.0 + (elapsed or 0))

    assert (_id("endpoint_unreachable") in registry.issues) is raised


def test_the_unreachable_issue_names_the_installation_and_where_it_was_reached(
    registry,
):
    check_unreachable(hass=HASS, entry=ENTRY, guard=_guard(failing_for=1), now=2000)

    issue = registry.issues[_id("endpoint_unreachable")]
    assert issue.is_fixable is False
    assert issue.severity == "error"
    assert issue.translation_placeholders == {
        "installation": "Roof inverter",
        "host": "inverter",
        "port": "1502",
    }


def test_the_unreachable_issue_names_the_default_port_when_none_was_saved(registry):
    entry = SimpleNamespace(**{**vars(ENTRY), "data": {"host": "inverter"}})

    check_unreachable(hass=HASS, entry=entry, guard=_guard(failing_for=1), now=2000)

    placeholders = registry.issues[_id("endpoint_unreachable")].translation_placeholders
    assert placeholders["port"] == "502"


def test_no_unreachable_issue_is_raised_while_a_model_issue_is_open(registry):
    raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")

    check_unreachable(hass=HASS, entry=ENTRY, guard=_guard(failing_for=1), now=2000)

    assert _id("endpoint_unreachable") not in registry.issues


def test_the_unreachable_issue_is_cleared_at_a_good_read(registry):
    check_unreachable(hass=HASS, entry=ENTRY, guard=_guard(failing_for=1), now=2000)

    clear_unreachable(hass=HASS, entry=ENTRY)

    assert registry.issues == {}


def test_refused_registers_are_listed_by_name_and_by_key_when_nothing_names_them(
    registry, monkeypatch
):
    monkeypatch.setattr(
        issues_module,
        "installation_entities",
        lambda **_: {
            "pv_power": SimpleNamespace(name="Roof power", original_name="Solar power"),
            "grid_power": SimpleNamespace(name=None, original_name="Grid power"),
        },
    )

    sync_refusals(
        hass=HASS, entry=ENTRY, keys={"pv_power", "grid_power", "ems_timeout"}
    )

    issue = registry.issues[_id("registers_refused")]
    assert issue.is_fixable is True
    assert issue.severity == "warning"
    assert issue.translation_placeholders == {
        "installation": "Roof inverter",
        "entities": "ems_timeout, Grid power, Roof power",
    }
    assert issue.data == {
        "entry_id": "entry-1",
        "keys": "ems_timeout,grid_power,pv_power",
    }


def test_the_refusal_issue_remembers_its_keys_for_the_next_load(registry):
    assert open_refusals(hass=HASS, entry=ENTRY) == frozenset()

    sync_refusals(hass=HASS, entry=ENTRY, keys={"pv_power", "grid_power"})

    assert open_refusals(hass=HASS, entry=ENTRY) == {"pv_power", "grid_power"}


def test_the_refusal_issue_without_data_remembers_nothing(registry):
    registry.issues[_id("registers_refused")] = SimpleNamespace(data=None)

    assert open_refusals(hass=HASS, entry=ENTRY) == frozenset()


def test_the_refusal_issue_goes_when_no_key_is_left(registry):
    sync_refusals(hass=HASS, entry=ENTRY, keys={"pv_power"})

    sync_refusals(hass=HASS, entry=ENTRY, keys=set())

    assert registry.issues == {}


@pytest.fixture
def names(monkeypatch):
    async def selector(*, hass, selector_name):
        assert hass is HASS
        assert selector_name == "equipment"
        return {"battery": "Battery", "meter_b": "Meter B"}

    monkeypatch.setattr(issues_module, "selector_options", selector)


async def test_equipment_that_lapsed_gets_a_warning_and_the_rest_lose_theirs(
    registry, names
):
    await sync_lapse_issues(
        hass=HASS,
        entry=ENTRY,
        equipment={Equipment.BATTERY, Equipment.METER_B},
        lapsed={Equipment.METER_B},
    )

    lapse = registry.issues["entry-1_meter_b_not_detected"]
    assert lapse.is_fixable is False
    assert lapse.severity == "warning"
    assert lapse.translation_key == "equipment_not_detected"
    assert lapse.translation_placeholders == {
        "installation": "Roof inverter",
        "equipment": "Meter B",
    }
    assert registry.deleted == ["entry-1_battery_not_detected"]


async def test_no_equipment_names_are_looked_up_when_nothing_lapsed(registry):
    await sync_lapse_issues(
        hass=HASS, entry=ENTRY, equipment={Equipment.BATTERY}, lapsed=set()
    )

    assert registry.deleted == ["entry-1_battery_not_detected"]


def test_the_open_issues_of_an_installation_are_listed_by_kind(registry):
    raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")
    sync_refusals(hass=HASS, entry=ENTRY, keys={"pv_power"})
    registry.issues["entry-1_meter_b_not_detected"] = SimpleNamespace(data=None)

    assert open_issue_keys(hass=HASS, entry=ENTRY) == [
        "identity_mismatch",
        "registers_refused",
        "equipment_not_detected:meter_b",
    ]


def test_removing_the_installation_removes_every_issue_it_raised(registry):
    raise_identity_issue(hass=HASS, entry=ENTRY, serial="OTHER")
    sync_refusals(hass=HASS, entry=ENTRY, keys={"pv_power"})
    check_unreachable(hass=HASS, entry=ENTRY, guard=_guard(failing_for=1), now=2000)
    registry.issues["entry-1_battery_not_detected"] = SimpleNamespace(data=None)

    remove_issues(hass=HASS, entry=ENTRY)

    assert registry.issues == {}
    assert set(registry.deleted) == {
        *(f"entry-1_{item.value}_not_detected" for item in Equipment),
        *(
            _id(key)
            for key in (
                "model_mismatch",
                "identity_mismatch",
                "unsupported_device",
                "registers_refused",
                "endpoint_unreachable",
            )
        ),
    }
