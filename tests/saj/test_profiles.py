from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from saj.device_type import format_device_type
from saj.errors import (
    ModelMismatchError,
    UnknownModelError,
    UnsupportedDeviceError,
)
from saj.models import (
    ENABLING_EVIDENCE,
    Evidence,
    Placement,
    Shape,
    Span,
    placements_by_evidence,
)
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from saj.profiles import AUTOMATIC, PROFILES, Resolution, resolve_profile
from tests.profiles import profile

if TYPE_CHECKING:
    from saj.models import Profile

ALPHA = profile(
    base=HS3,
    key="alpha",
    device_types={0x0001, 0x0002},
    hand_verified=True,
)
BETA = profile(base=HS3, key="beta", device_types={0x0010}, hand_verified=False)
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


@pytest.mark.parametrize(
    ("device_type", "shape"),
    [
        (0x0001, Shape(phases=1, strings=1)),
        (UNRECOGNISED_TYPE, Shape(phases=3, strings=4, assumed=True)),
    ],
)
def test_a_device_type_has_the_shape_its_profile_gives_or_the_assumed_maximum(
    device_type: int, shape: Shape
):
    profile_ = replace(ALPHA, maximum_shape=Shape(phases=3, strings=4))

    assert profile_.shape_of(device_type=device_type) == shape


@pytest.mark.parametrize(
    ("first", "last", "address", "words", "inside"),
    [
        (0x10, 0x1F, 0x10, 1, True),
        (0x10, 0x1F, 0x1F, 1, True),
        (0x10, 0x1F, 0x1E, 2, True),
        (0x10, 0x1F, 0x1F, 2, False),
        (0x10, 0x1F, 0x0F, 1, False),
        (0x10, 0x1F, 0x20, 1, False),
    ],
)
def test_a_span_contains_a_row_only_when_all_its_words_fit(
    first: int, last: int, address: int, words: int, *, inside: bool
):
    span = Span(name="block", first=first, last=last)

    assert span.contains(address=address, words=words) is inside


def test_placements_are_listed_by_evidence_in_the_order_given():
    placements = placements_by_evidence(
        groups={
            Evidence.VERIFIED: {"alpha": 0x10, "beta": 0x11},
            Evidence.DOCUMENTED: {"gamma": None},
        }
    )

    assert placements == (
        Placement(key="alpha", address=0x10, evidence=Evidence.VERIFIED),
        Placement(key="beta", address=0x11, evidence=Evidence.VERIFIED),
        Placement(key="gamma", address=None, evidence=Evidence.DOCUMENTED),
    )


@pytest.mark.parametrize(
    ("evidence", "enabling"),
    [
        (Evidence.VERIFIED, True),
        (Evidence.IMPLEMENTED, True),
        (Evidence.DOCUMENTED, False),
        (Evidence.RESPONDS_UNCHECKED, False),
        (Evidence.RESPONDS_UNDOCUMENTED, False),
    ],
)
def test_only_verified_and_implemented_evidence_enables_a_row(
    evidence: Evidence, *, enabling: bool
):
    assert (evidence in ENABLING_EVIDENCE) is enabling


@pytest.mark.parametrize(
    ("profile_", "types", "largest", "verified"),
    [
        (HS3, {0x1610: Shape(phases=3, strings=2)}, 32, True),
        (
            H2,
            {
                0x005A: Shape(phases=1, strings=2),
                0x005B: Shape(phases=1, strings=3),
            },
            56,
            False,
        ),
    ],
)
def test_the_shipped_models_declare_their_device_types_and_largest_request(
    profile_: Profile, types: dict[int, Shape], largest: int, *, verified: bool
):
    assert profile_.device_types == types
    assert profile_.largest_request == largest
    assert profile_.hand_verified is verified
    assert profile_.spans


def test_the_shipped_profiles_are_hs3_then_h2():
    assert [profile_.key for profile_ in PROFILES] == ["hs3", "h2"]
    assert resolve_profile(device_type=0x005B, selection=AUTOMATIC).profile is H2
