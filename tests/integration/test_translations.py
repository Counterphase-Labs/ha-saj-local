import json
from pathlib import Path

import pytest

from custom_components.saj_local.saj.catalogue import (
    CATALOGUES,
    ENERGY_BLOCK,
    blocks_by_key,
)
from custom_components.saj_local.saj.definitions import EntityKind

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
}


def _shipped_registers(*, profile_key: str):
    return CATALOGUES[profile_key].registers


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

    assert translated == set(rows)


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


def test_only_the_seven_entity_platforms_are_translated():
    assert set(ENTITY_TRANSLATIONS) <= {kind.value for kind in EntityKind}


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


def test_every_block_an_entity_can_be_listed_under_has_a_label():
    blocks = {
        block
        for profile_key in PROFILE_KEYS
        for block in blocks_by_key(
            profile=CATALOGUES[profile_key].profile, device_type=0
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
