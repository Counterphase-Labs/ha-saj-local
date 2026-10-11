import pytest

from saj.catalogue import Fit
from saj.health import Break
from saj.load import installation_load, planned_load, requests_per_read
from saj.models import ALL_EQUIPMENT, Equipment
from saj.models.hs3 import PROFILE as HS3
from saj.schedule import Cadence
from tests.profiles import profile

DEVICE_TYPE = 1
BLOCK_KEYS = frozenset({"pv_power", "battery_power", "grid_power"})
FAR_KEYS = frozenset({"operating_mode", "battery_soc"})
PROFILE = profile(
    base=HS3,
    key="alpha",
    device_types={DEVICE_TYPE},
    keys=(*BLOCK_KEYS, *FAR_KEYS),
    hand_verified=True,
)
SECONDS_PER_MINUTE = 60


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        (set(), 0),
        (BLOCK_KEYS, 1),
        ({"pv_power"}, 1),
        (FAR_KEYS, 2),
        (BLOCK_KEYS | FAR_KEYS, 3),
        ({"unknown"}, 0),
    ],
)
def test_requests_for_one_read_count_blocks_not_rows(keys: set[str], expected: int):
    assert (
        requests_per_read(
            fit=Fit(profile=PROFILE, device_type=DEVICE_TYPE, equipment=ALL_EQUIPMENT),
            keys=keys,
        )
        == expected
    )


def test_a_break_adds_the_requests_it_forces():
    keys = {"pv_power", "grid_power"}
    gap = Break(before=0x40A6, after=0x40A6)

    requests = requests_per_read(
        fit=Fit(profile=PROFILE, device_type=DEVICE_TYPE, equipment=ALL_EQUIPMENT),
        keys=keys,
        breaks=[gap],
    )

    assert requests == 2


def _load(cadences: list[Cadence], enabled: set[str] | None = None) -> float:
    return planned_load(
        fit=Fit(profile=PROFILE, device_type=DEVICE_TYPE, equipment=ALL_EQUIPMENT),
        enabled=enabled,
        cadences=cadences,
    )


@pytest.mark.parametrize(
    ("cadences", "enabled", "expected"),
    [
        ([], None, 0),
        ([Cadence(interval=60, keys=BLOCK_KEYS | FAR_KEYS, default=True)], None, 3),
        ([Cadence(interval=30, keys=FAR_KEYS, default=True)], None, 4),
        (
            [
                Cadence(interval=60, keys=FAR_KEYS, default=True),
                Cadence(interval=10, keys=BLOCK_KEYS),
            ],
            None,
            2 + 6,
        ),
        (
            [
                Cadence(interval=60, keys=FAR_KEYS, default=True),
                Cadence(interval=10, keys=BLOCK_KEYS),
            ],
            set(FAR_KEYS),
            2,
        ),
        (
            [
                Cadence(interval=60, keys=FAR_KEYS, default=True),
                Cadence(interval=10, keys=BLOCK_KEYS),
            ],
            {"operating_mode", "pv_power", "grid_power"},
            1 + 6,
        ),
    ],
)
def test_the_planned_load_sums_each_cadence_planned_on_its_own(
    cadences: list[Cadence], enabled: set[str] | None, expected: float
):
    assert _load(cadences, enabled) == expected


ALL_KEYS = BLOCK_KEYS | FAR_KEYS


@pytest.mark.parametrize(
    ("enabled", "default_interval", "groups", "expected"),
    [
        (ALL_KEYS, 60, [], 3),
        (ALL_KEYS, 30, [], 6),
        (FAR_KEYS, 60, [], 2),
        (set(), 60, [], 0),
        (ALL_KEYS, 60, [Cadence(interval=10, keys=BLOCK_KEYS)], 2 + 6),
        (ALL_KEYS, 60, [Cadence(interval=10, keys=frozenset({"pv_power"}))], 2 + 1 + 6),
        (FAR_KEYS, 60, [Cadence(interval=10, keys=BLOCK_KEYS)], 2),
        (ALL_KEYS, 60, [Cadence(interval=10, keys=frozenset({"unsupported"}))], 3),
    ],
)
def test_the_installation_load_defaults_what_no_group_claims_and_counts_enabled_rows(
    enabled: set[str],
    default_interval: int,
    groups: list[Cadence],
    expected: float,
):
    load = installation_load(
        fit=Fit(profile=PROFILE, device_type=DEVICE_TYPE, equipment=ALL_EQUIPMENT),
        enabled=enabled,
        default_interval=default_interval,
        groups=groups,
    )

    assert load == expected


def test_a_write_only_key_adds_no_load_to_a_cadence():
    selected = profile(
        base=HS3,
        key="beta",
        device_types={DEVICE_TYPE},
        keys=("pv_power", "ems_grid_power_target"),
        hand_verified=True,
    )
    cadences = [
        Cadence(interval=60, keys=frozenset({"pv_power", "ems_grid_power_target"}))
    ]

    assert (
        installation_load(
            fit=Fit(profile=selected, device_type=DEVICE_TYPE, equipment=ALL_EQUIPMENT),
            enabled={"pv_power", "ems_grid_power_target"},
            default_interval=60,
            groups=[
                Cadence(interval=10, keys=frozenset({"ems_grid_power_target"})),
            ],
        )
        == 1
    )
    assert (
        requests_per_read(
            fit=Fit(profile=selected, device_type=DEVICE_TYPE, equipment=ALL_EQUIPMENT),
            keys=cadences[0].keys,
        )
        == 1
    )


@pytest.mark.parametrize(
    ("equipment", "expected"),
    [
        (frozenset(), 1),
        (frozenset({Equipment.BATTERY}), 2),
    ],
)
def test_requests_for_one_read_leave_out_equipment_that_is_not_fitted(
    equipment: frozenset[Equipment], expected: int
):
    fit = Fit(profile=PROFILE, device_type=DEVICE_TYPE, equipment=equipment)

    assert requests_per_read(fit=fit, keys={"pv_power", "battery_soc"}) == expected


@pytest.mark.parametrize(
    ("equipment", "expected"),
    [
        (frozenset(), 2),
        (frozenset({Equipment.BATTERY}), 3),
    ],
)
def test_the_installation_load_leaves_out_equipment_that_is_not_fitted(
    equipment: frozenset[Equipment], expected: int
):
    fit = Fit(profile=PROFILE, device_type=DEVICE_TYPE, equipment=equipment)

    load = installation_load(
        fit=fit,
        enabled=ALL_KEYS,
        default_interval=60,
        groups=[],
    )

    assert load == expected
