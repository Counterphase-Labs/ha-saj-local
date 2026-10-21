import pytest

from saj_local_mock.link import (
    LINK_PARAMETERS,
    Action,
    Link,
    LinkFault,
    LinkSettings,
    LockoutState,
    RefusedBlock,
    changed_link,
    check_combination,
    link_values,
)

CLIENT = "10.0.0.9"
OTHER_CLIENT = "10.0.0.10"
SEQUENCES = range(1, 201)


def make_link(*, seed=7, **changes):
    return Link(seed=seed, settings=LinkSettings(**changes))


def ask(*, link, sequence=1, client=CLIENT, span=(0x10, 1), now=0.0):
    start, count = span
    return link.decide_request(
        client=client, sequence=sequence, start=start, count=count, now=now
    )


def test_a_link_with_no_fault_answers_every_request_at_once():
    link = Link(seed=7)

    decisions = [ask(link=link, sequence=sequence) for sequence in SEQUENCES]

    assert all(
        (d.action, d.fault, d.delay_s, d.late_duplicate)
        == (Action.ANSWER, None, 0.0, False)
        for d in decisions
    )
    assert link.decide_connection(client=CLIENT, now=0.0).fault is None


@pytest.mark.parametrize(
    ("changes", "action", "fault", "code"),
    [
        ({"offline": True}, Action.DROP, LinkFault.OFFLINE, 0),
        ({"unresponsive": True}, Action.NO_ANSWER, LinkFault.UNRESPONSIVE, 0),
        (
            {"dropped_connection_percent": 100},
            Action.DROP,
            LinkFault.DROPPED_CONNECTION,
            0,
        ),
        ({"no_answer_percent": 100}, Action.NO_ANSWER, LinkFault.NO_ANSWER, 0),
        (
            {"device_failure_percent": 100},
            Action.EXCEPTION,
            LinkFault.DEVICE_FAILURE,
            0x04,
        ),
        ({"busy_percent": 100}, Action.EXCEPTION, LinkFault.BUSY, 0x06),
        (
            {"refused_blocks": (RefusedBlock(start=0x0, end=0x1F, code=0x2B),)},
            Action.EXCEPTION,
            LinkFault.REFUSED_BLOCK,
            0x2B,
        ),
        (
            {"offline_seconds": 10, "offline_period_seconds": 60},
            Action.DROP,
            LinkFault.OFFLINE,
            0,
        ),
    ],
)
def test_each_setting_decides_how_the_request_is_answered(changes, action, fault, code):
    decision = ask(link=make_link(**changes))

    assert (decision.action, decision.fault, decision.exception_code) == (
        action,
        fault,
        code,
    )


ORDERED_SETTINGS = [
    (LinkFault.OFFLINE, {"offline": True}),
    (LinkFault.UNRESPONSIVE, {"unresponsive": True}),
    (LinkFault.LOCKOUT, {}),
    (LinkFault.DROPPED_CONNECTION, {"dropped_connection_percent": 100}),
    (LinkFault.NO_ANSWER, {"no_answer_percent": 100}),
    (
        LinkFault.REFUSED_BLOCK,
        {"refused_blocks": (RefusedBlock(start=0, end=0xFFFF, code=0),)},
    ),
    (LinkFault.DEVICE_FAILURE, {"device_failure_percent": 100}),
    (LinkFault.BUSY, {"busy_percent": 100}),
]


@pytest.mark.parametrize("position", range(len(ORDERED_SETTINGS)))
def test_the_first_check_that_applies_decides_in_the_documented_order(position):
    changes = {}
    for _, setting in ORDERED_SETTINGS[position:]:
        changes.update(setting)
    link = make_link(**changes)
    link.restore_lockout(state=LockoutState(addresses=(CLIENT,), whole_port=False))
    if position > 2:
        link.reset_module()

    decision = ask(link=link)

    assert decision.fault is ORDERED_SETTINGS[position][0]


@pytest.mark.parametrize(
    "field",
    [
        "no_answer_percent",
        "busy_percent",
        "device_failure_percent",
        "dropped_connection_percent",
        "late_duplicate_percent",
    ],
)
def test_a_chance_of_zero_never_applies_and_one_hundred_always_does(field):
    never = make_link(**{field: 0})
    always = make_link(**{field: 100})

    never_faults = [ask(link=never, sequence=n) for n in SEQUENCES]
    always_faults = [ask(link=always, sequence=n) for n in SEQUENCES]

    assert all(d.fault is None and not d.late_duplicate for d in never_faults)
    assert all(d.fault is not None or d.late_duplicate for d in always_faults)


def test_a_chance_in_between_applies_to_some_requests_only():
    link = make_link(no_answer_percent=50)

    faults = [ask(link=link, sequence=n).fault for n in SEQUENCES]

    assert None in faults
    assert LinkFault.NO_ANSWER in faults


def test_the_same_seed_and_sequence_give_the_same_decision_whatever_came_before():
    settings = {"no_answer_percent": 30, "busy_percent": 30, "jitter_ms": 50}
    first = make_link(seed=3, **settings)
    second = make_link(seed=3, **settings)
    ask(link=second, sequence=999)

    assert [ask(link=first, sequence=n) for n in SEQUENCES] == [
        ask(link=second, sequence=n) for n in SEQUENCES
    ]


def test_a_different_seed_gives_different_draws():
    settings = {"no_answer_percent": 50}

    first = [ask(link=make_link(seed=1, **settings), sequence=n) for n in SEQUENCES]
    second = [ask(link=make_link(seed=2, **settings), sequence=n) for n in SEQUENCES]

    assert first != second


@pytest.mark.parametrize(
    ("changes", "low", "high"),
    [
        ({"latency_ms": 100}, 0.1, 0.1),
        ({"latency_ms": 100, "jitter_ms": 40}, 0.06, 0.14),
        ({"latency_ms": 0, "jitter_ms": 40}, 0.0, 0.04),
    ],
)
def test_latency_is_the_set_value_plus_or_minus_the_jitter_and_never_negative(
    changes, low, high
):
    link = make_link(**changes)

    delays = [ask(link=link, sequence=n).delay_s for n in SEQUENCES]

    assert low <= min(delays)
    assert max(delays) <= high
    if changes.get("jitter_ms"):
        assert len(set(delays)) > 1


@pytest.mark.parametrize(
    ("start", "count", "refused"),
    [
        (0x100, 1, True),
        (0x1FF, 1, True),
        (0x0F0, 0x20, True),
        (0x1F0, 0x20, True),
        (0x0FF, 1, False),
        (0x200, 1, False),
        (0x0FF, 2, True),
    ],
)
def test_a_read_or_write_touching_a_refused_block_answers_that_blocks_code(
    start, count, refused
):
    link = make_link(refused_blocks=(RefusedBlock(start=0x100, end=0x1FF, code=0),))

    decision = ask(link=link, span=(start, count))

    assert (decision.action, decision.exception_code) == (
        (Action.EXCEPTION, 0) if refused else (Action.ANSWER, 0)
    )


def test_each_refused_block_answers_its_own_code():
    link = make_link(
        refused_blocks=(
            RefusedBlock(start=0x100, end=0x1FF, code=0),
            RefusedBlock(start=0x200, end=0x2FF, code=0xC8),
        )
    )

    assert ask(link=link, span=(0x210, 1)).exception_code == 0xC8


@pytest.mark.parametrize(
    ("changes", "now", "offline"),
    [
        ({"offline_seconds": 10, "offline_period_seconds": 60}, 0.0, True),
        ({"offline_seconds": 10, "offline_period_seconds": 60}, 9.9, True),
        ({"offline_seconds": 10, "offline_period_seconds": 60}, 10.0, False),
        ({"offline_seconds": 10, "offline_period_seconds": 60}, 59.0, False),
        ({"offline_seconds": 10, "offline_period_seconds": 60}, 125.0, True),
        ({"offline_seconds": 10, "offline_period_seconds": 0}, 5.0, False),
        ({"offline_seconds": 0, "offline_period_seconds": 60}, 5.0, False),
        ({"offline": True}, 30.0, True),
        ({}, 5.0, False),
    ],
)
def test_the_module_is_offline_when_set_or_inside_the_offline_part_of_its_period(
    changes, now, offline
):
    link = make_link(**changes)

    assert link.is_offline(now=now) is offline
    assert link.module_state(now=now).offline is offline
    assert (link.decide_connection(client=CLIENT, now=now).fault is not None) is offline


def test_an_unresponsive_module_still_accepts_connections():
    link = make_link(unresponsive=True)

    assert link.decide_connection(client=CLIENT, now=0.0).fault is None
    assert link.module_state(now=0.0).unresponsive


def test_offline_refuses_a_connection_for_the_offline_fault():
    link = make_link(offline=True)

    assert link.decide_connection(client=CLIENT, now=0.0).fault is LinkFault.OFFLINE


def lockout_link(**changes):
    return make_link(lockout_requests=3, lockout_window_seconds=10, **changes)


def test_a_client_above_the_threshold_in_the_window_is_locked_out_with_its_connection():
    link = lockout_link()

    decisions = [ask(link=link, now=float(second)) for second in range(5)]

    assert [d.fault for d in decisions] == [
        None,
        None,
        None,
        LinkFault.LOCKOUT,
        LinkFault.LOCKOUT,
    ]
    assert decisions[3].action is Action.DROP
    assert link.decide_connection(client=CLIENT, now=5.0).fault is LinkFault.LOCKOUT


def test_a_lockout_refuses_only_the_client_unless_the_whole_port_is_chosen():
    link = lockout_link()
    for second in range(4):
        ask(link=link, now=float(second))

    assert link.decide_connection(client=OTHER_CLIENT, now=5.0).fault is None
    assert ask(link=link, client=OTHER_CLIENT, now=5.0).fault is None
    assert link.lockout_state() == LockoutState(addresses=(CLIENT,), whole_port=False)


def test_a_whole_port_lockout_refuses_every_client():
    link = lockout_link(lockout_whole_port=True)
    for second in range(4):
        ask(link=link, now=float(second))

    assert link.decide_connection(client=OTHER_CLIENT, now=5.0).fault is (
        LinkFault.LOCKOUT
    )
    assert ask(link=link, client=OTHER_CLIENT, now=5.0).fault is LinkFault.LOCKOUT
    assert link.lockout_state() == LockoutState(addresses=(), whole_port=True)


def test_requests_spread_beyond_the_window_never_lock_a_client_out():
    link = lockout_link()

    decisions = [ask(link=link, now=float(second * 11)) for second in range(20)]

    assert all(d.fault is None for d in decisions)


def test_a_lockout_outlives_the_window_and_ends_only_when_the_module_is_reset():
    link = lockout_link()
    for second in range(4):
        ask(link=link, now=float(second))

    assert ask(link=link, now=10_000.0).fault is LinkFault.LOCKOUT

    link.reset_module()

    assert ask(link=link, now=10_001.0).fault is None
    assert link.decide_connection(client=CLIENT, now=10_001.0).fault is None
    assert link.lockout_state() == LockoutState(addresses=(), whole_port=False)


def test_reset_forgets_the_requests_counted_towards_a_lockout():
    link = lockout_link()
    for second in range(3):
        ask(link=link, now=float(second))
    link.reset_module()

    assert ask(link=link, now=3.0).fault is None


def test_a_zero_threshold_never_locks_a_client_out():
    link = make_link(lockout_requests=0, lockout_window_seconds=10)

    decisions = [ask(link=link, now=0.0, sequence=n) for n in SEQUENCES]

    assert all(d.fault is None for d in decisions)


def test_a_zero_second_window_counts_only_requests_at_the_same_instant():
    link = make_link(lockout_requests=1, lockout_window_seconds=0)

    assert ask(link=link, now=1.0).fault is None
    assert ask(link=link, now=2.0).fault is None
    assert ask(link=link, now=2.0).fault is LinkFault.LOCKOUT


def test_a_lockout_state_can_be_restored_into_a_new_link():
    saved = LockoutState(addresses=(OTHER_CLIENT, CLIENT), whole_port=False)
    link = Link(seed=1)

    link.restore_lockout(state=saved)

    assert link.lockout_state() == LockoutState(
        addresses=(OTHER_CLIENT, CLIENT), whole_port=False
    )
    assert link.decide_connection(client=CLIENT, now=0.0).fault is LinkFault.LOCKOUT


def test_the_module_state_reports_what_is_in_force_as_json():
    link = make_link(unresponsive=True, offline=True)
    link.restore_lockout(state=LockoutState(addresses=(CLIENT,), whole_port=False))

    assert link.module_state(now=0.0).to_json() == {
        "status": "offline",
        "offline": True,
        "unresponsive": True,
        "locked_out": True,
        "locked_addresses": [CLIENT],
        "whole_port": False,
    }
    assert Link(seed=1).module_state(now=0.0).to_json()["locked_out"] is False


def test_a_whole_port_lockout_shows_as_locked_out_in_the_module_state():
    link = Link(seed=1)
    link.restore_lockout(state=LockoutState(addresses=(), whole_port=True))

    state = link.module_state(now=0.0)

    assert (state.locked_out, state.whole_port, state.locked_addresses) == (
        True,
        True,
        (),
    )


def test_replacing_the_settings_keeps_a_lockout_in_force():
    link = lockout_link()
    for second in range(4):
        ask(link=link, now=float(second))

    link.replace_settings(settings=LinkSettings())

    assert link.settings == LinkSettings()
    assert ask(link=link, now=5.0).fault is LinkFault.LOCKOUT


def test_dropping_connections_now_is_signalled_each_time_it_is_asked():
    link = Link(seed=1)
    before = link.drop_generation

    link.drop_connections_now()
    link.drop_connections_now()

    assert link.drop_generation == before + 2


@pytest.mark.parametrize(
    ("changes", "status"),
    [
        ({}, "online"),
        ({"unresponsive": True}, "unresponsive"),
        ({"offline": True}, "offline"),
        ({"offline": True, "unresponsive": True}, "offline"),
    ],
)
def test_the_module_status_names_the_fault_in_force(changes, status):
    assert make_link(**changes).module_state(now=0.0).status == status


@pytest.mark.parametrize("whole_port", [True, False])
def test_a_locked_out_module_has_the_locked_out_status(whole_port):
    link = Link(seed=1)
    addresses = () if whole_port else (CLIENT,)
    link.restore_lockout(state=LockoutState(addresses=addresses, whole_port=whole_port))

    assert link.module_state(now=0.0).status == "locked_out"


def test_a_new_seed_changes_the_draws_and_the_old_one_brings_them_back():
    link = make_link(busy_percent=50, seed=1)

    def faults():
        return [ask(link=link, sequence=n).fault for n in SEQUENCES]

    first = faults()
    link.set_seed(seed=2)
    second = faults()
    link.set_seed(seed=1)

    assert first != second
    assert faults() == first


@pytest.mark.parametrize(
    ("span", "code"),
    [
        ((0x10, 1), 7),
        ((0x0F, 2), 7),
        ((0x20, 1), 7),
        ((0x21, 1), None),
        ((0x0E, 2), None),
    ],
)
def test_the_refused_code_is_that_of_a_block_the_span_overlaps(span, code):
    link = make_link(refused_blocks=(RefusedBlock(start=0x10, end=0x20, code=7),))
    start, count = span

    assert link.refused_code(start=start, count=count) == code


def test_the_link_values_name_every_setting_and_list_the_refused_blocks():
    values = link_values(
        settings=LinkSettings(
            latency_ms=5, refused_blocks=(RefusedBlock(start=1, end=2, code=3),)
        )
    )

    assert set(values) == {parameter.name for parameter in LINK_PARAMETERS} | {
        "refused_blocks"
    }
    assert values["latency_ms"] == 5
    assert values["refused_blocks"] == [{"start": 1, "end": 2, "code": 3}]


def test_the_changed_link_settings_are_those_that_differ_by_name():
    scenario = LinkSettings(latency_ms=5)
    running = LinkSettings(
        latency_ms=6, offline=True, refused_blocks=(RefusedBlock(1, 2, 3),)
    )

    assert changed_link(settings=running, scenario=scenario) == [
        "latency_ms",
        "offline",
        "refused_blocks",
    ]
    assert changed_link(settings=scenario, scenario=scenario) == []


@pytest.mark.parametrize(
    ("changes", "problem"),
    [
        ({}, None),
        ({"offline_seconds": 10, "offline_period_seconds": 10}, None),
        (
            {"offline_seconds": 11, "offline_period_seconds": 10},
            ("offline_seconds", "must be <= offline_period_seconds"),
        ),
        ({"lockout_requests": 5, "lockout_window_seconds": 1}, None),
        (
            {"lockout_requests": 5},
            ("lockout_window_seconds", "must be >= 1 when lockout_requests is set"),
        ),
    ],
)
def test_settings_that_only_make_sense_together_are_checked_together(changes, problem):
    assert check_combination(settings=LinkSettings(**changes)) == problem
