import pytest

from saj.equipment import (
    Detection,
    Outcome,
    Setting,
    evaluate,
    met,
    next_pack_limit,
    resolve,
    stored_fitted,
    to_probe,
    valid_pack_count,
)
from saj.models import Comparison, Condition, Equipment, Probe

BATTERY = Equipment.BATTERY
METER = Equipment.METER_B
CHARGER = Equipment.EV_CHARGER


def _condition(comparison: Comparison, reference: int, key: str = "reading"):
    return Condition(key=key, comparison=comparison, reference=reference)


@pytest.mark.parametrize(
    ("comparison", "reference", "value", "expected"),
    [
        (Comparison.EQUALS, 1, 1, True),
        (Comparison.EQUALS, 1, 0, False),
        (Comparison.EQUALS, 1, 1.0, True),
        (Comparison.DIFFERS, 0, 24, True),
        (Comparison.DIFFERS, 0, 0, False),
        (Comparison.ABOVE, 1, 2, True),
        (Comparison.ABOVE, 1, 1, False),
        (Comparison.ABOVE, 1, 0, False),
        (Comparison.EQUALS, 1, None, False),
        (Comparison.DIFFERS, 0, None, False),
        (Comparison.ABOVE, 1, "text", False),
    ],
)
def test_a_condition_compares_a_reading_with_its_reference(
    comparison: Comparison, reference: int, value: object, *, expected: bool
):
    condition = _condition(comparison, reference)

    assert met(condition=condition, value=value) is expected


def _probe(*, unanswered: bool) -> Probe:
    return Probe(
        equipment=BATTERY,
        conditions=(
            _condition(Comparison.DIFFERS, 0, key="mode"),
            _condition(Comparison.ABOVE, 1, key="count"),
        ),
        unanswered=unanswered,
    )


@pytest.mark.parametrize(
    ("values", "fitted", "answered"),
    [
        ({"mode": 1, "count": 0}, True, True),
        ({"mode": 0, "count": 3}, True, True),
        ({"mode": 0, "count": 1}, False, True),
        ({"mode": None, "count": 3}, True, True),
        ({"mode": None, "count": 0}, False, True),
        ({"mode": 0, "count": None}, False, True),
        ({"mode": 5}, True, True),
    ],
)
def test_a_probe_finds_equipment_when_any_answered_condition_is_met(
    values: dict[str, object], *, fitted: bool, answered: bool
):
    detection = evaluate(probe=_probe(unanswered=False), values=values)

    assert (detection.fitted, detection.answered) == (fitted, answered)
    assert detection.equipment is BATTERY
    assert detection.values == values


@pytest.mark.parametrize("unanswered", [True, False])
@pytest.mark.parametrize(
    "values", [{}, {"mode": None, "count": None}, {"mode": "text"}]
)
def test_a_probe_nothing_answered_takes_its_unanswered_result(
    values: dict[str, object], *, unanswered: bool
):
    detection = evaluate(probe=_probe(unanswered=unanswered), values=values)

    assert detection.fitted is unanswered
    assert detection.answered is False


def test_a_probe_reads_each_key_once_in_condition_order():
    probe = Probe(
        equipment=METER,
        conditions=(
            _condition(Comparison.EQUALS, 1, key="a"),
            _condition(Comparison.ABOVE, 3, key="b"),
            _condition(Comparison.DIFFERS, 0, key="a"),
        ),
        unanswered=False,
    )

    assert probe.keys == ("a", "b")


@pytest.mark.parametrize(
    ("settings", "probed"),
    [
        ({}, {BATTERY, METER, CHARGER}),
        ({BATTERY: Setting.FITTED}, {METER, CHARGER}),
        ({METER: Setting.NOT_FITTED}, {BATTERY, CHARGER}),
        ({CHARGER: Setting.AUTOMATIC, BATTERY: Setting.NOT_FITTED}, {METER, CHARGER}),
    ],
)
def test_only_equipment_on_automatic_is_probed(
    settings: dict[Equipment, Setting], probed: set[Equipment]
):
    assert to_probe(settings=settings, equipment={BATTERY, METER, CHARGER}) == probed


def _detection(equipment: Equipment, *, fitted: bool) -> Detection:
    return Detection(equipment=equipment, fitted=fitted, answered=True, values={})


def _outcome(*, fitted: bool, kept: bool, lapsed: bool) -> Outcome:
    return Outcome(
        fitted=frozenset({BATTERY} if fitted else ()),
        remembered=frozenset({BATTERY} if kept else ()),
        lapsed=frozenset({BATTERY} if lapsed else ()),
    )


@pytest.mark.parametrize(
    ("setting", "remembered", "detected", "expected"),
    [
        (
            Setting.AUTOMATIC,
            False,
            True,
            _outcome(fitted=True, kept=True, lapsed=False),
        ),
        (
            Setting.AUTOMATIC,
            False,
            False,
            _outcome(fitted=False, kept=False, lapsed=False),
        ),
        (Setting.AUTOMATIC, True, True, _outcome(fitted=True, kept=True, lapsed=False)),
        (Setting.AUTOMATIC, True, False, _outcome(fitted=True, kept=True, lapsed=True)),
        (Setting.FITTED, False, False, _outcome(fitted=True, kept=False, lapsed=False)),
        (Setting.FITTED, False, True, _outcome(fitted=True, kept=False, lapsed=False)),
        (Setting.FITTED, True, False, _outcome(fitted=True, kept=True, lapsed=False)),
        (
            Setting.NOT_FITTED,
            False,
            True,
            _outcome(fitted=False, kept=False, lapsed=False),
        ),
        (
            Setting.NOT_FITTED,
            True,
            True,
            _outcome(fitted=False, kept=False, lapsed=False),
        ),
        (
            Setting.NOT_FITTED,
            True,
            False,
            _outcome(fitted=False, kept=False, lapsed=False),
        ),
    ],
)
def test_a_setting_a_memory_and_a_probe_decide_what_is_fitted_and_remembered(
    setting: Setting, expected: Outcome, *, remembered: bool, detected: bool
):
    outcome = resolve(
        equipment={BATTERY},
        settings={BATTERY: setting},
        remembered={BATTERY} if remembered else set(),
        detections={BATTERY: _detection(BATTERY, fitted=detected)},
    )

    assert outcome == expected


def test_each_equipment_is_resolved_on_its_own_and_unknown_memory_is_dropped():
    outcome = resolve(
        equipment={BATTERY, METER},
        settings={},
        remembered={BATTERY, CHARGER},
        detections={
            BATTERY: _detection(BATTERY, fitted=False),
            METER: _detection(METER, fitted=True),
        },
    )

    assert outcome.fitted == {BATTERY, METER}
    assert outcome.remembered == {BATTERY, METER}
    assert outcome.lapsed == {BATTERY}


@pytest.mark.parametrize(
    ("settings", "resolved", "fitted"),
    [
        ({}, {BATTERY}, {BATTERY}),
        ({}, set(), set()),
        ({BATTERY: Setting.FITTED}, set(), {BATTERY}),
        ({BATTERY: Setting.NOT_FITTED}, {BATTERY}, set()),
        ({METER: Setting.FITTED}, {BATTERY}, {BATTERY, METER}),
    ],
)
def test_the_stored_view_of_what_is_fitted_follows_setting_then_last_resolved_set(
    settings: dict[Equipment, Setting],
    resolved: set[Equipment],
    fitted: set[Equipment],
):
    assert (
        stored_fitted(equipment={BATTERY, METER}, settings=settings, resolved=resolved)
        == fitted
    )


@pytest.mark.parametrize(
    ("answered", "remembered_before", "expected"),
    [
        (True, False, _outcome(fitted=True, kept=True, lapsed=False)),
        (False, False, _outcome(fitted=True, kept=False, lapsed=False)),
        (False, True, _outcome(fitted=True, kept=True, lapsed=False)),
    ],
)
def test_only_an_answered_probe_makes_equipment_remembered(
    expected: Outcome, *, answered: bool, remembered_before: bool
):
    detection = Detection(equipment=BATTERY, fitted=True, answered=answered, values={})

    outcome = resolve(
        equipment={BATTERY},
        settings={},
        remembered={BATTERY} if remembered_before else set(),
        detections={BATTERY: detection},
    )

    assert outcome == expected


@pytest.mark.parametrize(
    ("reading", "maximum", "expected"),
    [
        (1, 4, 1),
        (4, 4, 4),
        (2, 4, 2),
        (0, 4, None),
        (5, 4, None),
        (-1, 4, None),
        (None, 4, None),
        ("two", 4, None),
        (2.0, 4, None),
    ],
)
def test_only_a_pack_count_from_one_to_the_maximum_is_valid(reading, maximum, expected):
    assert valid_pack_count(reading=reading, maximum=maximum) == expected


@pytest.mark.parametrize(
    ("stored", "reading", "battery", "expected"),
    [
        (None, 2, Setting.AUTOMATIC, 2),
        (None, 3, Setting.FITTED, 3),
        (2, 3, Setting.AUTOMATIC, 3),
        (3, 2, Setting.AUTOMATIC, 3),
        (3, 0, Setting.AUTOMATIC, 3),
        (3, 9, Setting.AUTOMATIC, 3),
        (3, None, Setting.AUTOMATIC, 3),
        (None, 0, Setting.AUTOMATIC, None),
        (None, 9, Setting.FITTED, None),
        (3, 4, Setting.NOT_FITTED, None),
        (3, None, Setting.NOT_FITTED, None),
    ],
)
def test_the_pack_limit_is_the_highest_valid_count_seen_and_forgotten_with_the_battery(
    stored, reading, battery, expected
):
    assert (
        next_pack_limit(stored=stored, reading=reading, maximum=4, battery=battery)
        == expected
    )
