import pytest

import saj.device as device_module
from saj.catalogue import Fit
from saj.device import Device, identify
from saj.errors import ModelMismatchError, UnsupportedDeviceError
from saj.models import Equipment
from saj.models.hs3 import PROFILE as HS3
from saj.profiles import AUTOMATIC, Resolution
from tests.profiles import profile
from tests.saj.fakes import FakeClient

RECOGNISED_TYPE = 0x0001
UNRECOGNISED_TYPE = 0x7777
RATED_POWER = 6000
FIRST = profile(
    base=HS3, key="first", device_types={RECOGNISED_TYPE}, keys=(), hand_verified=True
)
SECOND = profile(
    base=HS3, key="second", device_types={0x0002}, keys=(), hand_verified=False
)


def _words(text: bytes) -> tuple[int, ...]:
    padded = text.ljust(20, b"\0")
    return tuple(
        int.from_bytes(padded[index : index + 2], "big") for index in range(0, 20, 2)
    )


def _client(
    *, device_type: int = RECOGNISED_TYPE, serial: bytes = b"UNIT-0001"
) -> FakeClient:
    return FakeClient(
        {
            (0x8F00, 2): (device_type, RATED_POWER),
            (0x8F03, 10): _words(serial),
        }
    )


class StubResolver:
    def __init__(self, outcome: Resolution | Exception) -> None:
        self.outcome = outcome
        self.calls: list[tuple[int, str]] = []

    def __call__(self, device_type: int, selection: str) -> Resolution:
        self.calls.append((device_type, selection))
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def _resolver(monkeypatch, outcome: Resolution | Exception) -> StubResolver:
    resolver = StubResolver(outcome)
    monkeypatch.setattr(device_module, "resolve_profile", resolver)
    return resolver


async def test_identify_reads_type_and_power_together_then_serial(monkeypatch):
    _resolver(monkeypatch, Resolution(profile=FIRST, detected=True))
    client = _client()

    device = await identify(client)

    assert device == Device(
        serial="UNIT-0001",
        device_type=RECOGNISED_TYPE,
        rated_power=RATED_POWER,
        profile=FIRST,
        detected=True,
    )
    assert client.reads == [(0x8F00, 2), (0x8F03, 10)]


@pytest.mark.parametrize("detected", [True, False])
async def test_identify_passes_selection_through_and_reports_resolution(
    monkeypatch, *, detected: bool
):
    resolver = _resolver(monkeypatch, Resolution(profile=SECOND, detected=detected))

    device = await identify(_client(device_type=UNRECOGNISED_TYPE), "second")

    assert resolver.calls == [(UNRECOGNISED_TYPE, "second")]
    assert device.profile == SECOND
    assert device.detected is detected
    assert device.device_type == UNRECOGNISED_TYPE


@pytest.mark.parametrize(
    "error",
    [
        UnsupportedDeviceError(UNRECOGNISED_TYPE),
        ModelMismatchError(selected=FIRST, detected=SECOND),
    ],
)
async def test_identify_propagates_resolution_errors_before_reading_serial(
    monkeypatch, error: Exception
):
    _resolver(monkeypatch, error)
    client = _client()

    with pytest.raises(type(error)):
        await identify(client, AUTOMATIC)
    assert client.reads == [(0x8F00, 2)]


@pytest.mark.parametrize(
    ("serial", "message"),
    [
        (b"\0" * 20, "Invalid serial number"),
        (b"BAD\0ID", "Invalid serial number"),
        (b"   ", "Invalid serial number"),
        (b"\xff", "Invalid serial number encoding"),
    ],
)
async def test_identify_rejects_empty_or_invalid_serial(
    monkeypatch, serial: bytes, message: str
):
    _resolver(monkeypatch, Resolution(profile=FIRST, detected=True))
    with pytest.raises(ValueError, match=message):
        await identify(_client(serial=serial))


@pytest.mark.parametrize(
    ("fitted", "pack_limit"),
    [
        (frozenset(), None),
        (frozenset({Equipment.BATTERY}), 2),
        (frozenset(Equipment), None),
    ],
)
def test_a_device_fit_names_its_profile_type_fitted_equipment_and_pack_limit(
    fitted: frozenset[Equipment], pack_limit: int | None
):
    device = Device(
        serial="UNIT-0001",
        device_type=RECOGNISED_TYPE,
        rated_power=RATED_POWER,
        profile=FIRST,
        detected=True,
        equipment=fitted,
        pack_limit=pack_limit,
    )

    assert device.fit == Fit(
        profile=FIRST,
        device_type=RECOGNISED_TYPE,
        equipment=fitted,
        pack_limit=pack_limit,
    )


async def test_identify_treats_all_equipment_as_fitted_until_it_is_detected(
    monkeypatch,
):
    _resolver(monkeypatch, Resolution(profile=FIRST, detected=True))

    device = await identify(_client())

    assert device.equipment == frozenset(Equipment)


@pytest.mark.parametrize("detected", [True, False])
def test_a_device_description_names_model_type_power_and_how_it_was_found(
    *, detected: bool
):
    device = Device(
        serial="UNIT-0001",
        device_type=RECOGNISED_TYPE,
        rated_power=RATED_POWER,
        profile=FIRST,
        detected=detected,
    )

    description = device.description

    assert FIRST.key in description
    assert str(RATED_POWER) in description
    assert description.endswith("detected" if detected else "assumed")
