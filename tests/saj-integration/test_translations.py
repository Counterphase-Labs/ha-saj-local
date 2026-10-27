import functools
import json
import re
import string
from collections import Counter
from pathlib import Path

import pytest

from custom_components.saj_local.binary_sensor import CONTROL_ALLOWED_KEY
from custom_components.saj_local.config_flow import (
    ABORT_ALREADY_CONFIGURED,
    ABORT_PREFIX_UNAVAILABLE,
    ERROR_CONTROL_NOT_ALLOWED,
    ERROR_FUNCTION_SCHEDULED,
    ERROR_INVALID_EQUIPMENT,
    ERROR_SCHEDULE_IN_USE,
    ERROR_SCHEDULE_NOT_REGISTERED,
    NO_EQUIPMENT,
)
from custom_components.saj_local.const import (
    CONF_FUNCTION,
    CONF_SCHEDULE,
    EQUIPMENT_ISSUE_TRANSLATION_KEY,
    ISSUE_ENDPOINT_UNREACHABLE,
    ISSUE_IDENTITY_MISMATCH,
    ISSUE_MODEL_MISMATCH,
    ISSUE_REGISTERS_REFUSED,
    ISSUE_UNSUPPORTED_DEVICE,
)
from custom_components.saj_local.repairs import (
    ABORT_ENTRY_REMOVED,
    ERROR_DEVICE_CHANGED,
)
from custom_components.saj_local.saj.catalogue import (
    CATALOGUES,
    ENERGY_BLOCK,
    Fit,
    blocks_by_key,
)
from custom_components.saj_local.saj.definitions import EntityKind
from custom_components.saj_local.saj.equipment import Setting
from custom_components.saj_local.saj.models import (
    ALL_EQUIPMENT,
    Equipment,
    PowerFunction,
)

TRANSLATIONS = json.loads(
    (
        Path(__file__).parents[2] / "custom_components/saj_local/translations/en.json"
    ).read_text(encoding="utf-8")
)
ENTITY_TRANSLATIONS = TRANSLATIONS["entity"]
PROFILE_KEYS = sorted(CATALOGUES)
WRITE_PREFIXES = ("invalid_value_",)
WRITE_KEYS = {
    "control_not_enabled",
    "model_unverified",
    "protected_setting",
    "unknown_setting",
    "separate_registers",
    "link_unavailable",
    "write_allowance",
    "ems_timeout_too_short",
    "write_rejected",
    "write_unconfirmed",
    "write_mismatch",
    "no_power_target",
    "another_function_running",
    "unusable_power",
}
POWER_ENTITIES = {
    ("switch", function.switch_key): function for function in PowerFunction
} | {("number", function.target_key): function for function in PowerFunction}
CONTROL_ALLOWED = ("binary_sensor", CONTROL_ALLOWED_KEY)


TRANSLATIONS_DIRECTORY = (
    Path(__file__).parents[2] / "custom_components/saj_local/translations"
)
OTHER_LANGUAGE_FILES = sorted(
    path for path in TRANSLATIONS_DIRECTORY.glob("*.json") if path.stem != "en"
)


def _texts(node, path=()):
    """Return every text of a nested translation as a path-to-text mapping."""
    if isinstance(node, dict):
        return {
            found: text
            for key, child in node.items()
            for found, text in _texts(child, (*path, key)).items()
        }
    return {path: node}


def _placeholders(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


ENGLISH_TEXTS = _texts(TRANSLATIONS)


@pytest.mark.parametrize("path", OTHER_LANGUAGE_FILES, ids=lambda path: path.stem)
def test_every_language_has_the_keys_and_placeholders_of_english(path):
    texts = _texts(json.loads(path.read_text(encoding="utf-8")))

    assert sorted(ENGLISH_TEXTS.keys() - texts.keys()) == []
    assert sorted(texts.keys() - ENGLISH_TEXTS.keys()) == []
    assert [
        key
        for key, text in texts.items()
        if _placeholders(text) != _placeholders(ENGLISH_TEXTS[key])
    ] == []


def test_the_language_comparison_finds_a_missing_key_and_a_changed_placeholder():
    english = _texts({"a": {"b": "Hello {name}"}, "c": "Text"})
    other = _texts({"a": {"b": "Hallo {nom}"}, "d": "Text"})

    assert english.keys() - other.keys() == {("c",)}
    assert other.keys() - english.keys() == {("d",)}
    assert _placeholders(other[("a", "b")]) != _placeholders(english[("a", "b")])


def _shipped_registers(*, profile_key: str):
    return [row for row in CATALOGUES[profile_key].registers if row.exposed]


@pytest.mark.parametrize("profile_key", PROFILE_KEYS)
def test_every_row_at_the_maximum_shape_has_a_display_name_under_its_platform(
    profile_key,
):
    missing = [
        row.key
        for row in _shipped_registers(profile_key=profile_key)
        if not ENTITY_TRANSLATIONS.get(row.kind.value, {}).get(row.key, {}).get("name")
    ]

    assert missing == []


@pytest.mark.parametrize("profile_key", PROFILE_KEYS)
def test_every_option_of_an_enumerated_row_has_a_label(profile_key):
    missing = [
        (row.key, option)
        for row in _shipped_registers(profile_key=profile_key)
        if row.options is not None
        for option in row.options.values()
        if not ENTITY_TRANSLATIONS[row.kind.value][row.key].get("state", {}).get(option)
    ]

    assert missing == []


def test_there_are_no_translations_for_rows_that_do_not_exist():
    rows = {
        (row.kind.value, row.key): row
        for profile_key in PROFILE_KEYS
        for row in _shipped_registers(profile_key=profile_key)
    }
    translated = {
        (platform, key)
        for platform, entries in ENTITY_TRANSLATIONS.items()
        for key in entries
    }

    assert translated == set(rows) | set(POWER_ENTITIES) | {CONTROL_ALLOWED}


def test_there_are_no_option_labels_for_options_a_row_does_not_have():
    options_of: dict[tuple[str, str], set[str]] = {}
    for profile_key in PROFILE_KEYS:
        for row in _shipped_registers(profile_key=profile_key):
            if row.options is not None:
                options_of.setdefault((row.kind.value, row.key), set()).update(
                    row.options.values()
                )
    labelled = {
        (platform, key): set(entry["state"])
        for platform, entries in ENTITY_TRANSLATIONS.items()
        for key, entry in entries.items()
        if "state" in entry
    }

    assert labelled == options_of


def test_the_entity_platforms_are_the_entity_kinds():
    assert set(ENTITY_TRANSLATIONS) == {kind.value for kind in EntityKind}


def test_the_not_enabled_error_names_where_to_switch_control_on():
    message = TRANSLATIONS["exceptions"]["control_not_enabled"]["message"]

    assert "Configure" in message
    assert "Allow control" in message


def test_every_write_error_message_says_the_state_of_the_inverter():
    states = ("was not changed", "was changed", "unknown state")
    messages = {
        key: entry["message"]
        for key, entry in TRANSLATIONS["exceptions"].items()
        if key.startswith(WRITE_PREFIXES) or key in WRITE_KEYS
    }

    assert messages
    assert [
        key for key, text in messages.items() if not any(s in text for s in states)
    ] == []


def test_the_control_confirmation_warns_about_reverse_current_protection():
    description = TRANSLATIONS["options"]["step"]["confirm_control"]["description"]

    assert "reverse-current protection" in description
    assert "automations" in description


@pytest.mark.parametrize(
    ("flow", "step"), [("config", "confirm_control"), ("options", "confirm_control")]
)
def test_the_control_confirmation_states_the_cost_of_enabling_the_control_set(
    flow, step
):
    description = TRANSLATIONS[flow]["step"][step]["description"]

    assert {"{count}", "{before}", "{after}", "{budget}"} <= set(
        re.findall(r"\{\w+\}", description)
    )
    assert "wait" in description.lower()


def test_only_the_setup_confirmation_counts_control_entities_as_an_upper_limit():
    setup = TRANSLATIONS["config"]["step"]["confirm_control"]["description"]
    configure = TRANSLATIONS["options"]["step"]["confirm_control"]["description"]

    assert "up to {count}" in setup
    assert "up to" not in configure


def test_every_block_an_entity_can_be_listed_under_has_a_label():
    blocks = {
        block
        for profile_key in PROFILE_KEYS
        for block in blocks_by_key(
            fit=Fit(
                profile=CATALOGUES[profile_key].profile,
                device_type=0,
                equipment=ALL_EQUIPMENT,
            )
        ).values()
    }

    assert blocks <= set(TRANSLATIONS["selector"]["block"]["options"])


def test_there_are_no_labels_for_blocks_that_no_profile_has():
    spans = {
        span.name
        for profile_key in PROFILE_KEYS
        for span in CATALOGUES[profile_key].profile.spans
    }

    assert set(TRANSLATIONS["selector"]["block"]["options"]) == spans | {ENERGY_BLOCK}


@pytest.mark.parametrize("step", ["review_group", "review_group_over_budget"])
def test_the_polling_group_result_steps_label_both_choices(step):
    result = TRANSLATIONS["config_subentries"]["polling_group"]["step"][step]

    assert result["description"]
    assert set(result["menu_options"]) == {"save_group", "change_selection"}


def test_only_the_over_budget_texts_state_that_cadences_run_slower():
    group = TRANSLATIONS["config_subentries"]["polling_group"]["step"]

    assert "slower" in group["review_group_over_budget"]["description"]
    assert "slower" not in group["review_group"]["description"]
    assert "slower" in TRANSLATIONS["options"]["step"]["confirm_load"]["description"]


def test_the_disabled_option_label_names_the_entity_it_qualifies():
    label = TRANSLATIONS["selector"]["entity_state"]["options"]["disabled"]

    assert (
        label.format(entity="Realtime: Grid power") == "Realtime: Grid power (disabled)"
    )


EQUIPMENT_SECTION = TRANSLATIONS["options"]["step"]["init"]["sections"]["equipment"]


def test_the_equipment_section_names_and_describes_every_piece_of_equipment():
    names = {item.value for item in Equipment}

    assert set(EQUIPMENT_SECTION["data"]) == names
    assert set(EQUIPMENT_SECTION["data_description"]) == names


def test_the_equipment_section_states_what_is_treated_as_fitted():
    assert "{equipment_fitted}" in EQUIPMENT_SECTION["description"]


def test_every_equipment_and_every_setting_has_a_selector_label():
    selectors = TRANSLATIONS["selector"]

    assert set(selectors["equipment"]["options"]) == {
        *(item.value for item in Equipment),
        NO_EQUIPMENT,
    }
    assert set(selectors["equipment_setting"]["options"]) == {
        setting.value for setting in Setting
    }


def test_an_invalid_equipment_choice_has_an_error_text():
    assert TRANSLATIONS["options"]["error"][ERROR_INVALID_EQUIPMENT]


ISSUES = TRANSLATIONS["issues"]
ERROR_ALREADY_CONFIGURED = ABORT_ALREADY_CONFIGURED


def test_the_equipment_issue_names_the_installation_and_the_equipment_and_what_to_do():
    issue = ISSUES[EQUIPMENT_ISSUE_TRANSLATION_KEY]

    assert "{equipment}" in issue["title"]
    assert "{installation}" in issue["description"]
    assert "{equipment}" in issue["description"]
    assert "Configure" in issue["description"]
    assert "Not fitted" in issue["description"]


def test_there_is_a_translation_for_every_issue_the_integration_raises():
    assert set(ISSUES) == {
        EQUIPMENT_ISSUE_TRANSLATION_KEY,
        ISSUE_MODEL_MISMATCH,
        ISSUE_IDENTITY_MISMATCH,
        ISSUE_UNSUPPORTED_DEVICE,
        ISSUE_REGISTERS_REFUSED,
        ISSUE_ENDPOINT_UNREACHABLE,
    }


DESCRIPTION = ("description",)
CONFIRM_DESCRIPTION = ("fix_flow", "step", "confirm", "description")


@pytest.mark.parametrize(
    ("key", "where", "placeholders"),
    [
        (ISSUE_UNSUPPORTED_DEVICE, DESCRIPTION, {"installation", "device_type"}),
        (ISSUE_ENDPOINT_UNREACHABLE, DESCRIPTION, {"installation", "host", "port"}),
        (
            ISSUE_MODEL_MISMATCH,
            CONFIRM_DESCRIPTION,
            {"installation", "selected_model", "model", "serial"},
        ),
        (
            ISSUE_IDENTITY_MISMATCH,
            CONFIRM_DESCRIPTION,
            {"installation", "approved_serial", "model", "serial"},
        ),
        (
            ISSUE_REGISTERS_REFUSED,
            CONFIRM_DESCRIPTION,
            {"installation", "entities"},
        ),
    ],
)
def test_each_issue_says_what_happened_with_the_values_it_is_raised_with(
    key, where, placeholders
):
    issue = ISSUES[key]
    text = issue["title"] + functools.reduce(
        lambda node, step: node[step], where, issue
    )

    assert placeholders <= {
        name for _, name, _, _ in string.Formatter().parse(text) if name
    }
    assert {
        name for _, name, _, _ in string.Formatter().parse(text) if name
    } <= placeholders


@pytest.mark.parametrize(
    "key", [ISSUE_MODEL_MISMATCH, ISSUE_IDENTITY_MISMATCH, ISSUE_REGISTERS_REFUSED]
)
def test_a_fixable_issue_has_a_confirm_step_with_a_title_and_description(key):
    confirm = ISSUES[key]["fix_flow"]["step"]["confirm"]

    assert confirm["title"]
    assert "{installation}" in confirm["description"]


@pytest.mark.parametrize("key", [ISSUE_MODEL_MISMATCH, ISSUE_IDENTITY_MISMATCH])
def test_a_model_fix_shows_what_was_detected_and_every_way_it_can_fail(key):
    flow = ISSUES[key]["fix_flow"]

    assert "{model}" in flow["step"]["confirm"]["description"]
    assert "{serial}" in flow["step"]["confirm"]["description"]
    assert set(flow["error"]) == {
        "cannot_connect",
        "timeout",
        "read_rejected",
        "invalid_device_data",
        "unsupported_device",
        ERROR_ALREADY_CONFIGURED,
        ERROR_DEVICE_CHANGED,
    }
    assert set(flow["abort"]) == {
        ABORT_ENTRY_REMOVED,
        ABORT_ALREADY_CONFIGURED,
        ABORT_PREFIX_UNAVAILABLE,
    }


@pytest.mark.parametrize("key", [ISSUE_UNSUPPORTED_DEVICE, ISSUE_ENDPOINT_UNREACHABLE])
def test_an_issue_that_cannot_be_fixed_here_has_no_fix_flow(key):
    assert "fix_flow" not in ISSUES[key]


def test_every_power_control_switch_and_target_has_a_display_name():
    missing = [
        (platform, key)
        for platform, key in POWER_ENTITIES
        if not ENTITY_TRANSLATIONS[platform].get(key, {}).get("name")
    ]

    assert missing == []


def test_the_control_allowed_entity_has_a_name():
    platform, key = CONTROL_ALLOWED

    assert ENTITY_TRANSLATIONS[platform][key]["name"]


def test_every_power_function_has_a_selector_label():
    options = TRANSLATIONS["selector"]["power_function"]["options"]

    assert set(options) == {function.value for function in PowerFunction}


POWER_SCHEDULE = TRANSLATIONS["config_subentries"]["power_schedule"]


@pytest.mark.parametrize("step", ["user", "reconfigure"])
def test_the_power_schedule_form_labels_and_explains_both_fields(step):
    form = POWER_SCHEDULE["step"][step]

    assert form["title"]
    assert "power" in form["description"]
    assert set(form["data"]) == {CONF_FUNCTION, CONF_SCHEDULE}
    assert set(form["data_description"]) == {CONF_FUNCTION, CONF_SCHEDULE}


def test_every_refusal_of_the_power_schedule_form_has_its_own_message():
    errors = POWER_SCHEDULE["error"]

    assert set(errors) == {
        ERROR_CONTROL_NOT_ALLOWED,
        ERROR_FUNCTION_SCHEDULED,
        ERROR_SCHEDULE_IN_USE,
        ERROR_SCHEDULE_NOT_REGISTERED,
    }
    assert len(set(errors.values())) == len(errors)


def test_the_power_schedule_names_its_type_and_its_saved_result():
    assert POWER_SCHEDULE["entry_type"]
    assert POWER_SCHEDULE["initiate_flow"]["user"]
    assert POWER_SCHEDULE["abort"]["reconfigure_successful"]


def test_no_two_entities_share_a_display_name():
    names = [
        entry["name"]
        for entries in ENTITY_TRANSLATIONS.values()
        for entry in entries.values()
    ]

    assert sorted(name for name, count in Counter(names).items() if count > 1) == []
