from dataclasses import replace

import pytest

from saj.codec import Range
from saj.control import Write
from saj.device import Device
from saj.errors import (
    AnotherFunctionRunningError,
    NoPowerTargetError,
    UnusablePowerError,
)
from saj.models import (
    ALL_EQUIPMENT,
    EnableBitMethod,
    Equipment,
    OperatingModeMethod,
    PowerFunction,
)
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from saj.power_control import (
    Action,
    ActionKind,
    Blocker,
    Situation,
    Wish,
    decide,
    power_controls,
    power_functions,
    require_none_running,
    require_target,
)
from tests.profiles import profile

DEVICE_TYPE = 1
HS3_RATED = 12000
H2_RATED = 8000
BATTERY = PowerFunction.BATTERY
GRID = PowerFunction.GRID
INVERTER = PowerFunction.INVERTER
BATTERY_ENABLE = "ems_battery_control"
BATTERY_TARGET = "ems_battery_power_target"
GRID_ENABLE = "ems_grid_control"
GRID_TARGET = "ems_grid_power_target"
INVERTER_ENABLE = "ems_inverter_control_with_timeout_exit"
INVERTER_PARTNER = "ems_inverter_control"
INVERTER_TARGET = "ems_inverter_power_target"
MODE = "application_mode"
DIRECTION = "passive_mode"
CHARGE = "passive_battery_charge_power"
DISCHARGE = "passive_battery_discharge_power"
HS3_KEYS = (
    BATTERY_ENABLE,
    BATTERY_TARGET,
    GRID_ENABLE,
    GRID_TARGET,
    INVERTER_ENABLE,
    INVERTER_PARTNER,
    INVERTER_TARGET,
)
H2_KEYS = (MODE, DIRECTION, CHARGE, DISCHARGE)
PASSIVE = 3
SELF_USE = 0
STANDBY = 0
DISCHARGING = 1
CHARGING = 2
HS3_STATEMENT = {
    BATTERY: EnableBitMethod(enable_key=BATTERY_ENABLE, target_key=BATTERY_TARGET),
    GRID: EnableBitMethod(enable_key=GRID_ENABLE, target_key=GRID_TARGET),
    INVERTER: EnableBitMethod(
        enable_key=INVERTER_ENABLE,
        target_key=INVERTER_TARGET,
        alternate_keys=(INVERTER_PARTNER,),
    ),
}
H2_STATEMENT = {
    BATTERY: OperatingModeMethod(
        mode_key=MODE,
        passive_mode=PASSIVE,
        default_mode=SELF_USE,
        direction_key=DIRECTION,
        standby=STANDBY,
        discharge=DISCHARGING,
        charge=CHARGING,
        charge_power_key=CHARGE,
        discharge_power_key=DISCHARGE,
    )
}


def _device(
    *,
    base,
    keys,
    statement,
    rated_power,
    equipment=ALL_EQUIPMENT,
) -> Device:
    model_profile = replace(
        profile(
            base=base,
            key="alpha",
            device_types={DEVICE_TYPE},
            hand_verified=True,
            keys=keys,
        ),
        power_control=statement,
    )
    return Device(
        serial="S",
        device_type=DEVICE_TYPE,
        rated_power=rated_power,
        profile=model_profile,
        detected=True,
        equipment=frozenset(equipment),
    )


def _hs3(*, rated_power=HS3_RATED, equipment=ALL_EQUIPMENT, keys=HS3_KEYS) -> Device:
    return _device(
        base=HS3,
        keys=keys,
        statement=HS3_STATEMENT,
        rated_power=rated_power,
        equipment=equipment,
    )


def _h2(*, rated_power=H2_RATED, equipment=ALL_EQUIPMENT, keys=H2_KEYS) -> Device:
    return _device(
        base=H2,
        keys=keys,
        statement=H2_STATEMENT,
        rated_power=rated_power,
        equipment=equipment,
    )


def _control(device: Device, function: PowerFunction = BATTERY):
    return power_controls(device=device)[function]


@pytest.mark.parametrize(
    ("rated_power", "function", "limit"),
    [
        (HS3_RATED, BATTERY, 12000),
        (8000, GRID, 8000),
        (HS3_RATED, INVERTER, 12000),
    ],
)
def test_the_enable_bit_range_is_minus_to_plus_the_rated_power(
    rated_power: int, function: PowerFunction, limit: int
):
    span = _control(_hs3(rated_power=rated_power), function).target_range

    assert span == Range(minimum=-limit, maximum=limit)


@pytest.mark.parametrize(
    ("rated_power", "watts", "share"),
    [
        (HS3_RATED, -600, -5.0),
        (HS3_RATED, 1200, 10.0),
        (HS3_RATED, 601, 5.01),
        (HS3_RATED, 1, 0.01),
        (HS3_RATED, 0, 0),
        (HS3_RATED, -12000, -100.0),
        (8000, -600, -7.5),
        (8000, 12, 0.15),
    ],
)
def test_a_power_is_sent_as_the_share_of_the_rated_power_in_the_steps_of_the_row(
    rated_power: int, watts: int, share: float
):
    control = _control(_hs3(rated_power=rated_power))

    (write,) = control.change(watts=watts, values={})

    assert write == Write(key=BATTERY_TARGET, value=share)


@pytest.mark.parametrize(
    ("rated_power", "share", "watts"),
    [(HS3_RATED, -5.0, -600), (HS3_RATED, 5.01, 601), (8000, -7.5, -600)],
)
def test_the_power_held_is_read_back_from_the_target_row_in_whole_watts(
    rated_power: int, share: float, watts: int
):
    control = _control(_hs3(rated_power=rated_power))

    assert control.held(values={BATTERY_TARGET: share}) == watts


@pytest.mark.parametrize("values", [{}, {BATTERY_TARGET: None}, {BATTERY_TARGET: "x"}])
def test_the_power_held_is_unknown_without_a_number_in_the_target_row(values: dict):
    assert _control(_hs3()).held(values=values) is None


@pytest.mark.parametrize(
    ("values", "running"),
    [
        ({BATTERY_ENABLE: 1}, True),
        ({BATTERY_ENABLE: 0}, False),
        ({}, None),
        ({BATTERY_ENABLE: None}, None),
        ({BATTERY_ENABLE: True}, None),
    ],
)
def test_an_enable_bit_function_runs_while_its_bit_is_set(values: dict, running):
    assert _control(_hs3()).running(values=values) is running


@pytest.mark.parametrize(
    ("main", "alternate", "running"),
    [
        (1, 1, True),
        (1, 0, True),
        (1, None, True),
        (0, 1, True),
        (None, 1, True),
        (0, 0, False),
        (0, None, None),
        (None, 0, None),
        (None, None, None),
    ],
)
def test_a_function_runs_on_any_set_form_and_is_not_off_on_one_clear_form_alone(
    main, alternate, running
):
    values = {INVERTER_ENABLE: main, INVERTER_PARTNER: alternate}

    assert _control(_hs3(), INVERTER).running(values=values) is running


@pytest.mark.parametrize(
    ("function", "enable", "target", "partners"),
    [
        (BATTERY, BATTERY_ENABLE, BATTERY_TARGET, {}),
        (GRID, GRID_ENABLE, GRID_TARGET, {}),
        (INVERTER, INVERTER_ENABLE, INVERTER_TARGET, {INVERTER_PARTNER: 0}),
    ],
)
def test_an_enable_bit_start_writes_the_target_then_the_bit_with_its_exclusive_partners(
    function: PowerFunction, enable: str, target: str, partners: dict
):
    control = _control(_hs3(), function)

    start = control.start(watts=-600, prior=None)

    assert start.writes == (
        Write(key=target, value=-5.0),
        Write(key=enable, value=1, also=partners, inspect_timeout=True),
    )
    assert start.remember is None


@pytest.mark.parametrize(
    ("function", "enable", "partners"),
    [
        (BATTERY, BATTERY_ENABLE, {}),
        (GRID, GRID_ENABLE, {}),
        (INVERTER, INVERTER_ENABLE, {INVERTER_PARTNER: 0}),
    ],
)
def test_an_enable_bit_stop_clears_every_form_of_the_bit_and_leaves_the_target(
    function: PowerFunction, enable: str, partners: dict
):
    control = _control(_hs3(), function)

    assert control.stop(remembered=None) == (Write(key=enable, value=0, also=partners),)


def test_an_enable_bit_function_is_kept_alive_by_its_target_and_remembers_nothing():
    control = _control(_hs3())

    assert control.beat_key == BATTERY_TARGET
    assert control.prior_key is None
    assert control.state_keys == {BATTERY_ENABLE}


def test_the_state_rows_of_an_enable_bit_function_are_all_of_its_forms():
    control = _control(_hs3(), INVERTER)

    assert control.state_keys == {INVERTER_ENABLE, INVERTER_PARTNER}


@pytest.mark.parametrize(("rated_power", "limit"), [(H2_RATED, 8800), (10000, 11000)])
def test_the_operating_mode_range_is_minus_to_plus_110_percent_of_the_rated_power(
    rated_power: int, limit: int
):
    span = _control(_h2(rated_power=rated_power)).target_range

    assert span == Range(minimum=-limit, maximum=limit)


@pytest.mark.parametrize(
    ("watts", "power_key", "share", "direction"),
    [
        (-600, CHARGE, 7.5, CHARGING),
        (600, DISCHARGE, 7.5, DISCHARGING),
        (-8800, CHARGE, 110.0, CHARGING),
        (4, DISCHARGE, 0.1, DISCHARGING),
    ],
)
def test_an_operating_mode_start_sets_the_power_then_passive_mode_then_the_direction(
    watts: int, power_key: str, share: float, direction: int
):
    start = _control(_h2()).start(watts=watts, prior=SELF_USE)

    assert start.writes == (
        Write(key=power_key, value=share),
        Write(key=MODE, value=PASSIVE),
        Write(key=DIRECTION, value=direction),
    )


def test_an_operating_mode_start_at_zero_watts_is_standby_and_writes_no_power():
    start = _control(_h2()).start(watts=0, prior=SELF_USE)

    assert start.writes == (
        Write(key=MODE, value=PASSIVE),
        Write(key=DIRECTION, value=STANDBY),
    )


@pytest.mark.parametrize(
    ("prior", "remembered"),
    [(SELF_USE, 0), (1.0, 1), (12, 12), (PASSIVE, None), (None, None)],
)
def test_the_application_mode_is_remembered_unless_it_is_already_passive_or_unknown(
    prior, remembered
):
    start = _control(_h2()).start(watts=-600, prior=prior)

    assert start.remember == remembered


def test_an_operating_mode_function_reads_the_application_mode_before_it_starts():
    control = _control(_h2())

    assert control.prior_key == MODE
    assert control.beat_key is None
    assert control.state_keys == {MODE, DIRECTION, CHARGE, DISCHARGE}


@pytest.mark.parametrize(
    ("watts", "values", "expected"),
    [
        (-600, {DIRECTION: CHARGING}, (Write(key=CHARGE, value=7.5),)),
        (600, {DIRECTION: DISCHARGING}, (Write(key=DISCHARGE, value=7.5),)),
        (
            600,
            {DIRECTION: CHARGING},
            (
                Write(key=DISCHARGE, value=7.5),
                Write(key=DIRECTION, value=DISCHARGING),
            ),
        ),
        (
            -600,
            {},
            (Write(key=CHARGE, value=7.5), Write(key=DIRECTION, value=CHARGING)),
        ),
        (0, {DIRECTION: CHARGING}, (Write(key=DIRECTION, value=STANDBY),)),
        (0, {DIRECTION: STANDBY}, ()),
    ],
)
def test_a_change_of_power_writes_the_direction_only_when_it_changes(
    watts: int, values: dict, expected: tuple
):
    assert _control(_h2()).change(watts=watts, values=values) == expected


@pytest.mark.parametrize(
    ("remembered", "mode"), [(None, SELF_USE), (1, 1), (SELF_USE, SELF_USE)]
)
def test_an_operating_mode_stop_sets_standby_then_puts_the_mode_back(
    remembered, mode: int
):
    assert _control(_h2()).stop(remembered=remembered) == (
        Write(key=DIRECTION, value=STANDBY),
        Write(key=MODE, value=mode),
    )


@pytest.mark.parametrize(
    ("values", "running"),
    [
        ({MODE: PASSIVE, DIRECTION: CHARGING}, True),
        ({MODE: PASSIVE, DIRECTION: DISCHARGING}, True),
        ({MODE: PASSIVE, DIRECTION: STANDBY}, True),
        ({MODE: PASSIVE}, True),
        ({MODE: SELF_USE, DIRECTION: CHARGING}, False),
        ({MODE: SELF_USE, DIRECTION: STANDBY}, False),
        ({MODE: SELF_USE}, False),
        ({DIRECTION: CHARGING}, None),
        ({}, None),
    ],
)
def test_an_operating_mode_function_runs_whenever_the_inverter_is_in_its_mode(
    values: dict, running
):
    assert _control(_h2()).running(values=values) is running


@pytest.mark.parametrize(
    ("values", "watts"),
    [
        ({DIRECTION: CHARGING, CHARGE: 7.5}, -600),
        ({DIRECTION: DISCHARGING, DISCHARGE: 7.5}, 600),
        ({DIRECTION: STANDBY}, 0),
        ({DIRECTION: CHARGING}, None),
        ({DIRECTION: DISCHARGING}, None),
        ({DIRECTION: 9, CHARGE: 7.5}, None),
        ({CHARGE: 7.5}, None),
    ],
)
def test_the_power_held_is_that_of_the_row_of_the_direction_negative_for_charge(
    values: dict, watts
):
    assert _control(_h2()).held(values=values) == watts


@pytest.mark.parametrize(
    ("raw", "usable"),
    [
        (-600, -600),
        (600.0, 600),
        (0, 0),
        (12000, 12000),
        (-12000, -12000),
        (12001, None),
        (-12001, None),
        (0.5, None),
        (True, None),
        ("600", None),
        (None, None),
    ],
)
def test_only_a_whole_number_of_watts_inside_the_range_is_usable(raw, usable):
    assert _control(_hs3()).usable(raw=raw) == usable


def test_requiring_a_usable_power_names_the_range_when_it_is_not():
    control = _control(_hs3())

    assert control.require_usable(raw=600.0) == 600
    with pytest.raises(UnusablePowerError) as caught:
        control.require_usable(raw=12001)
    assert (caught.value.minimum, caught.value.maximum) == (-12000, 12000)


@pytest.mark.parametrize(
    ("equipment", "keys", "expected"),
    [
        (ALL_EQUIPMENT, HS3_KEYS, (BATTERY, GRID, INVERTER)),
        (ALL_EQUIPMENT - {Equipment.BATTERY}, HS3_KEYS, (GRID, INVERTER)),
        (ALL_EQUIPMENT - {Equipment.METER_A}, HS3_KEYS, (BATTERY, INVERTER)),
        (frozenset(), HS3_KEYS, (INVERTER,)),
        (
            ALL_EQUIPMENT,
            tuple(key for key in HS3_KEYS if key != GRID_TARGET),
            (BATTERY, INVERTER),
        ),
        (ALL_EQUIPMENT, (BATTERY_ENABLE,), ()),
    ],
)
def test_a_device_has_the_functions_its_model_states_with_rows_and_fitted_equipment(
    equipment, keys, expected
):
    device = _hs3(equipment=equipment, keys=keys)

    assert power_functions(fit=device.fit) == expected


@pytest.mark.parametrize(
    ("equipment", "expected"),
    [(ALL_EQUIPMENT, (BATTERY,)), (ALL_EQUIPMENT - {Equipment.BATTERY}, ())],
)
def test_an_operating_mode_device_has_battery_only_with_a_battery(equipment, expected):
    assert power_functions(fit=_h2(equipment=equipment).fit) == expected


def test_a_model_that_states_nothing_has_no_functions_whatever_its_rows():
    device = replace(
        _hs3(), profile=replace(_hs3().profile, power_control={}, key="bravo")
    )

    assert power_functions(fit=device.fit) == ()
    assert power_controls(device=device) == {}


def test_the_controls_of_a_device_are_built_for_every_function_whose_rows_it_has():
    device = _hs3(equipment=ALL_EQUIPMENT - {Equipment.METER_A})

    assert set(power_controls(device=device)) == {BATTERY, GRID, INVERTER}
    assert power_functions(fit=device.fit) == (BATTERY, INVERTER)


def test_a_start_is_refused_without_a_target():
    with pytest.raises(NoPowerTargetError) as caught:
        require_target(function=BATTERY, targets={GRID: 5})

    assert caught.value.function is BATTERY


def test_a_start_with_a_target_returns_it():
    assert require_target(function=BATTERY, targets={BATTERY: -600}) == -600


@pytest.mark.parametrize("running", [(GRID,), (BATTERY, INVERTER)])
def test_a_start_is_refused_naming_another_function_that_is_running(running: tuple):
    with pytest.raises(AnotherFunctionRunningError) as caught:
        require_none_running(function=BATTERY, running=running)

    assert caught.value.running in set(running) - {BATTERY}


@pytest.mark.parametrize("running", [(), (BATTERY,)])
def test_a_function_running_alone_does_not_block_its_own_start(running: tuple):
    require_none_running(function=BATTERY, running=running)


def _decide(wishes: dict, **changes: object) -> tuple[Action, ...]:
    controls = power_controls(device=_hs3())
    functions = changes.pop("functions", (BATTERY, GRID, INVERTER))
    situation = Situation(
        controls={function: controls[function] for function in functions},
        running=(),
        owned=(),
        started={},
        targets={},
    )
    return decide(wishes=wishes, situation=replace(situation, **changes))


ON = Wish(on=True)
OFF = Wish(on=False)


def _action(kind: ActionKind, function=BATTERY, *, watts=None, blocker=None):
    return Action(kind, function, watts=watts, blocker=blocker)


@pytest.mark.parametrize(
    ("wish", "targets", "expected"),
    [
        (ON, {BATTERY: -600}, _action(ActionKind.START)),
        (Wish(on=True, power=-300), {}, _action(ActionKind.START, watts=-300)),
        (
            Wish(on=True, power=-300.0),
            {BATTERY: 5},
            _action(ActionKind.START, watts=-300),
        ),
        (ON, {}, _action(ActionKind.BLOCKED, blocker=Blocker.NO_TARGET)),
    ],
    ids=["from-target", "from-block", "block-wins-over-target", "no-power-at-all"],
)
def test_a_schedule_turning_on_starts_the_function_at_the_block_power_or_the_target(
    wish: Wish, targets: dict, expected: Action
):
    assert _decide({BATTERY: wish}, targets=targets) == (expected,)


@pytest.mark.parametrize("power", [0.5, "600", True, 12001, -12001, [1]])
@pytest.mark.parametrize("started", [{}, {BATTERY: None}])
def test_a_block_power_that_cannot_be_used_blocks_and_writes_nothing(power, started):
    actions = _decide(
        {BATTERY: Wish(on=True, power=power)},
        started=started,
        targets={BATTERY: 1},
        running=(BATTERY,),
    )

    assert actions == (_action(ActionKind.BLOCKED, blocker=Blocker.UNUSABLE_POWER),)


@pytest.mark.parametrize(
    ("wish", "expected"),
    [
        (ON, _action(ActionKind.TAKE_OVER)),
        (Wish(on=True, power=-300), _action(ActionKind.TAKE_OVER, watts=-300)),
    ],
)
def test_a_function_already_running_when_its_schedule_turns_on_is_taken_over(
    wish: Wish, expected: Action
):
    assert _decide({BATTERY: wish}, running=(BATTERY,)) == (expected,)


@pytest.mark.parametrize("running", [(GRID,), (GRID, INVERTER)])
def test_a_start_is_held_back_while_a_different_function_runs(running: tuple):
    actions = _decide({BATTERY: ON}, running=running, targets={BATTERY: -600})

    assert actions == (_action(ActionKind.BLOCKED, blocker=Blocker.ANOTHER_RUNNING),)


def test_two_functions_wanted_at_once_start_the_first_and_hold_back_the_second():
    actions = _decide({BATTERY: ON, GRID: ON}, targets={BATTERY: -600, GRID: 100})

    assert actions == (
        _action(ActionKind.START),
        _action(ActionKind.BLOCKED, GRID, blocker=Blocker.ANOTHER_RUNNING),
    )


@pytest.mark.parametrize(
    ("wish", "running", "started", "expected"),
    [
        (ON, (BATTERY,), {BATTERY: None}, ()),
        (Wish(on=True, power=-300), (BATTERY,), {BATTERY: -300}, ()),
        (ON, (), {BATTERY: None}, ()),
        (Wish(on=True, power=-300), (), {BATTERY: None}, ()),
        (
            Wish(on=True, power=-300),
            (BATTERY,),
            {BATTERY: None},
            (_action(ActionKind.CHANGE_POWER, watts=-300),),
        ),
        (
            Wish(on=True, power=-400),
            (BATTERY,),
            {BATTERY: -300},
            (_action(ActionKind.CHANGE_POWER, watts=-400),),
        ),
    ],
    ids=[
        "started-nothing-to-do",
        "same-power-nothing-to-do",
        "switched-off-by-hand-stays-off",
        "switched-off-by-hand-new-power-stays-off",
        "first-block-power-after-start",
        "moved-to-another-block-power",
    ],
)
def test_after_a_successful_start_only_a_new_block_power_is_acted_on(
    wish: Wish, running: tuple, started: dict, expected: tuple
):
    actions = _decide({BATTERY: wish}, running=running, started=started)

    assert actions == expected


@pytest.mark.parametrize(
    ("owned", "started", "expected"),
    [
        ((BATTERY,), {BATTERY: None}, (_action(ActionKind.STOP),)),
        ((), {BATTERY: None}, (_action(ActionKind.FORGET),)),
        ((BATTERY,), {}, ()),
        ((), {}, ()),
    ],
)
def test_a_schedule_turning_off_stops_what_it_started_and_owned(
    owned: tuple, started: dict, expected: tuple
):
    assert _decide({BATTERY: OFF}, owned=owned, started=started) == expected


def test_a_function_the_system_does_not_have_is_left_alone():
    actions = _decide(
        {BATTERY: ON, INVERTER: OFF},
        functions=(BATTERY,),
        targets={BATTERY: 1},
        started={INVERTER: None},
        owned=(INVERTER,),
    )

    assert actions == (_action(ActionKind.START),)


def test_with_nothing_wanted_and_nothing_started_nothing_is_decided():
    assert _decide({}, running=(BATTERY,), owned=(BATTERY,)) == ()


def test_zero_watts_then_minus_600_changes_the_power_of_an_operating_mode_function():
    control = _control(_h2())
    standby = {MODE: PASSIVE, DIRECTION: STANDBY}
    running = (BATTERY,) if control.running(values=standby) else ()

    actions = decide(
        wishes={BATTERY: Wish(on=True, power=-600)},
        situation=Situation(
            controls={BATTERY: control},
            running=running,
            owned=(BATTERY,),
            started={BATTERY: 0},
            targets={},
        ),
    )

    assert actions == (_action(ActionKind.CHANGE_POWER, watts=-600),)
    assert control.change(watts=-600, values=standby) == (
        Write(key=CHARGE, value=7.5),
        Write(key=DIRECTION, value=CHARGING),
    )
