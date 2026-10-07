import pytest

from saj.device_type import format_device_type
from saj.errors import (
    ModelMismatchError,
    UnknownModelError,
    UnsupportedDeviceError,
)
from saj.profiles import AUTOMATIC, Profile, Resolution, resolve_profile

ALPHA = Profile(
    key="alpha",
    display_name="Alpha",
    device_types=frozenset({0x0001, 0x0002}),
    measurement_keys=frozenset({"power"}),
    hand_verified=True,
)
BETA = Profile(
    key="beta",
    display_name="Beta",
    device_types=frozenset({0x0010}),
    measurement_keys=frozenset({"power"}),
    hand_verified=False,
)
UNRECOGNISED_TYPE = 0x7777


@pytest.mark.parametrize(
    ("selection", "device_type", "expected"),
    [
        (AUTOMATIC, 0x0001, Resolution(profile=ALPHA, detected=True)),
        (AUTOMATIC, 0x0002, Resolution(profile=ALPHA, detected=True)),
        (AUTOMATIC, 0x0010, Resolution(profile=BETA, detected=True)),
        ("alpha", 0x0002, Resolution(profile=ALPHA, detected=True)),
        ("beta", UNRECOGNISED_TYPE, Resolution(profile=BETA, detected=False)),
        ("alpha", UNRECOGNISED_TYPE, Resolution(profile=ALPHA, detected=False)),
    ],
)
def test_resolution_returns_profile_with_detection_state(
    selection: str, device_type: int, expected: Resolution
):
    assert (
        resolve_profile(
            device_type=device_type, selection=selection, profiles=(ALPHA, BETA)
        )
        == expected
    )


def test_automatic_selection_of_unrecognised_type_reports_the_raw_type():
    with pytest.raises(UnsupportedDeviceError) as caught:
        resolve_profile(
            device_type=UNRECOGNISED_TYPE, selection=AUTOMATIC, profiles=(ALPHA, BETA)
        )

    assert caught.value.device_type == UNRECOGNISED_TYPE
    assert format_device_type(UNRECOGNISED_TYPE) in str(caught.value)


@pytest.mark.parametrize(
    ("selection", "device_type", "selected", "detected"),
    [
        ("alpha", 0x0010, ALPHA, BETA),
        ("beta", 0x0001, BETA, ALPHA),
    ],
)
def test_selection_contradicting_recognised_type_reports_both_profiles(
    selection: str, device_type: int, selected: Profile, detected: Profile
):
    with pytest.raises(ModelMismatchError) as caught:
        resolve_profile(
            device_type=device_type, selection=selection, profiles=(ALPHA, BETA)
        )

    assert caught.value.selected == selected
    assert caught.value.detected == detected


@pytest.mark.parametrize("device_type", [0x0001, UNRECOGNISED_TYPE])
def test_unknown_selection_is_rejected_with_the_selection(device_type: int):
    with pytest.raises(UnknownModelError) as caught:
        resolve_profile(
            device_type=device_type, selection="gamma", profiles=(ALPHA, BETA)
        )

    assert caught.value.selection == "gamma"
