from dataclasses import replace

import pytest

import saj.detection as detection_module
from saj.client import ModbusError, ModbusErrorMessage
from saj.detection import Detected, detect
from saj.device import Device
from saj.equipment import Detection
from saj.models import Comparison, Condition, Equipment, Probe
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from saj.telemetry import Readout
from tests.profiles import profile
from tests.saj.fakes import MemoryClient

BATTERY = Probe(
    equipment=Equipment.BATTERY,
    conditions=(
        Condition(key="battery_protocol", comparison=Comparison.DIFFERS, reference=0),
    ),
    unanswered=True,
)
METER = Probe(
    equipment=Equipment.METER_B,
    conditions=(
        Condition(key="meter_b_status", comparison=Comparison.EQUALS, reference=1),
    ),
    unanswered=False,
)


class StubReader:
    def __init__(self, outcome: Readout | Exception) -> None:
        self.outcome = outcome
        self.asked: list[tuple[str, ...]] = []

    async def __call__(self, *, client, device, enabled):
        del client, device
        self.asked.append(tuple(enabled))
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def _device(*probes: Probe) -> Device:
    shipped = profile(
        base=HS3, key="alpha", device_types={1}, keys=(), hand_verified=True
    )
    return Device(
        serial="S",
        device_type=1,
        rated_power=6000,
        profile=replace(shipped, probes=probes),
        detected=True,
    )


def _reader(monkeypatch, outcome: Readout | Exception) -> StubReader:
    reader = StubReader(outcome)
    monkeypatch.setattr(detection_module, "read_telemetry", reader)
    return reader


def _answer(**values: object) -> Readout:
    return Readout(values=values, refusals={})


async def test_every_probe_is_read_in_one_request_and_judged(monkeypatch):
    reader = _reader(monkeypatch, _answer(battery_protocol=24, meter_b_status=0))

    detected = await detect(
        client=object(),
        device=_device(BATTERY, METER),
        probed={Equipment.BATTERY, Equipment.METER_B},
    )

    assert reader.asked == [("battery_protocol", "meter_b_status")]
    assert detected.detections == {
        Equipment.BATTERY: Detection(
            equipment=Equipment.BATTERY,
            fitted=True,
            answered=True,
            values={"battery_protocol": 24},
        ),
        Equipment.METER_B: Detection(
            equipment=Equipment.METER_B,
            fitted=False,
            answered=True,
            values={"meter_b_status": 0},
        ),
    }


@pytest.mark.parametrize(
    "probed",
    [set(), {Equipment.METER_B}, {Equipment.EV_CHARGER}],
)
async def test_only_the_equipment_asked_for_is_probed(monkeypatch, probed):
    reader = _reader(monkeypatch, _answer(battery_protocol=24, meter_b_status=1))

    detected = await detect(
        client=object(), device=_device(BATTERY, METER), probed=probed
    )

    assert set(detected.detections) == probed & {Equipment.METER_B}
    assert reader.asked == ([("meter_b_status",)] if detected.detections else [])


@pytest.mark.parametrize(
    ("outcome", "battery", "meter"),
    [
        (
            Readout(values={}, refusals={"battery_protocol": 2, "meter_b_status": 2}),
            True,
            False,
        ),
        (_answer(battery_protocol=None, meter_b_status=None), True, False),
    ],
)
async def test_a_refused_or_undecodable_probe_takes_its_unanswered_result(
    monkeypatch, outcome, *, battery, meter
):
    _reader(monkeypatch, outcome)

    detected = await detect(
        client=object(),
        device=_device(BATTERY, METER),
        probed={Equipment.BATTERY, Equipment.METER_B},
    )

    assert detected.detections[Equipment.BATTERY].fitted is battery
    assert detected.detections[Equipment.METER_B].fitted is meter
    assert not detected.detections[Equipment.BATTERY].answered
    assert not detected.detections[Equipment.METER_B].answered


async def test_a_refused_request_leaves_only_the_probes_it_carried_unanswered(
    monkeypatch,
):
    _reader(
        monkeypatch,
        Readout(values={"battery_protocol": 24}, refusals={"meter_b_status": 2}),
    )

    detected = await detect(
        client=object(),
        device=_device(BATTERY, METER),
        probed={Equipment.BATTERY, Equipment.METER_B},
    )

    assert detected.detections[Equipment.BATTERY].answered
    assert not detected.detections[Equipment.METER_B].answered


@pytest.mark.parametrize(
    "message",
    [ModbusErrorMessage.REQUEST_TIMEOUT, ModbusErrorMessage.CONNECTION_CLOSED],
)
async def test_a_lost_connection_fails_detection(monkeypatch, message):
    _reader(monkeypatch, ModbusError(message))

    with pytest.raises(ModbusError):
        await detect(
            client=object(),
            device=_device(BATTERY),
            probed={Equipment.BATTERY},
        )


@pytest.mark.parametrize(
    ("shipped", "also", "requests"),
    [
        (HS3, (), 4),
        (H2, (), 3),
        (H2, ("battery_pack_count",), 4),
    ],
)
async def test_the_shipped_probes_share_requests_and_stay_within_four(
    shipped, also, requests
):
    client = MemoryClient()
    device = Device(
        serial="S",
        device_type=next(iter(shipped.device_types)),
        rated_power=6000,
        profile=shipped,
        detected=True,
    )

    detected = await detect(
        client=client, device=device, probed=shipped.equipment, also=also
    )

    assert len(client.reads) == requests
    assert set(detected.detections) == shipped.equipment
    assert set(detected.readings) == set(also)


async def test_extra_keys_are_read_in_the_same_request_as_the_probes(monkeypatch):
    reader = _reader(monkeypatch, _answer(battery_protocol=24, battery_pack_count=3))

    detected = await detect(
        client=object(),
        device=_device(BATTERY),
        probed={Equipment.BATTERY},
        also=("battery_pack_count",),
    )

    assert reader.asked == [("battery_protocol", "battery_pack_count")]
    assert detected.readings == {"battery_pack_count": 3}
    assert detected.detections[Equipment.BATTERY].values == {"battery_protocol": 24}


async def test_extra_keys_are_read_even_when_nothing_is_probed(monkeypatch):
    reader = _reader(monkeypatch, _answer(battery_pack_count=2))

    detected = await detect(
        client=object(),
        device=_device(BATTERY),
        probed=set(),
        also=("battery_pack_count",),
    )

    assert reader.asked == [("battery_pack_count",)]
    assert detected == Detected(detections={}, readings={"battery_pack_count": 2})


async def test_an_extra_key_the_request_did_not_return_is_missing_from_the_readings(
    monkeypatch,
):
    _reader(
        monkeypatch,
        Readout(values={"battery_protocol": 24}, refusals={"battery_pack_count": 2}),
    )

    detected = await detect(
        client=object(),
        device=_device(BATTERY),
        probed={Equipment.BATTERY},
        also=("battery_pack_count",),
    )

    assert detected.readings == {}
    assert detected.detections[Equipment.BATTERY].answered


async def test_nothing_is_read_when_there_is_nothing_to_probe_or_ask(monkeypatch):
    reader = _reader(monkeypatch, _answer())

    detected = await detect(client=object(), device=_device(BATTERY), probed=set())

    assert reader.asked == []
    assert detected == Detected(detections={}, readings={})


def _shipped_h2() -> Device:
    return Device(
        serial="S",
        device_type=0x005A,
        rated_power=6000,
        profile=H2,
        detected=True,
    )


async def test_an_h2_that_refuses_the_parallel_block_has_no_parallel_equipment():
    client = MemoryClient(bad_addresses=frozenset(range(0x4200, 0x4204)))

    detected = await detect(
        client=client, device=_shipped_h2(), probed={Equipment.PARALLEL}
    )

    parallel = detected.detections[Equipment.PARALLEL]
    assert parallel.fitted is False
    assert parallel.answered is False


@pytest.mark.parametrize(
    ("memory", "fitted"),
    [
        ({0x4200: 1}, True),
        ({0x4203: 2}, True),
        ({0x4203: 1}, False),
        ({}, False),
    ],
)
async def test_an_h2_that_answers_the_parallel_block_is_judged_by_mode_and_machines(
    memory, *, fitted
):
    detected = await detect(
        client=MemoryClient(memory),
        device=_shipped_h2(),
        probed={Equipment.PARALLEL},
    )

    assert detected.detections[Equipment.PARALLEL].fitted is fitted
    assert detected.detections[Equipment.PARALLEL].answered
