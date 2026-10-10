import asyncio
import logging

import pytest

from saj.catalogue import Row
from saj.client import ModbusError, ModbusErrorMessage
from saj.device import Device
from saj.errors import UnsupportedDeviceError
from saj.health import REFUSAL_THRESHOLD, Break, ReadHealth, Refusal, Region
from saj.models.hs3 import PROFILE as HS3
from saj.poller import (
    RECONNECT_REQUESTS,
    CadencePlan,
    CycleFailedError,
    IdentityChangedError,
    Poller,
    Services,
    Target,
    Tracking,
)
from saj.schedule import Cadence
from saj.telemetry import Readout, ReadRange, RequestOutcome
from tests.profiles import profile
from tests.saj.fakes import MemoryClient

PROFILE = profile(base=HS3, key="alpha", device_types={1}, keys=(), hand_verified=True)
DEVICE = Device("SERIAL-1", 1, 6000, PROFILE, detected=True)
OTHER_DEVICE = Device("SERIAL-2", 1, 6000, PROFILE, detected=True)
ROW_AB = (Row(address=0x4000, words=1), Row(address=0x4001, words=1))
ROW_C = (Row(address=0x4002, words=1),)
NOW = 1000.0
PER_REQUEST = 10.0


class FakeClient:
    def __init__(self, *, connected: bool = True) -> None:
        self.connected = connected
        self.events: list[str] = []

    def is_connected(self) -> bool:
        return self.connected

    async def close(self) -> None:
        self.connected = False
        self.events.append("close")

    async def connect(self) -> None:
        self.connected = True
        self.events.append("connect")

    def worst_case_duration(self, *, requests: int) -> float:
        return requests * PER_REQUEST

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self.events.append("read")
        return (address,) * count


class FakeSchedule:
    def __init__(self, cadences=()) -> None:
        self.cadences = tuple(cadences)
        self.due_keys: frozenset[str] = frozenset()
        self.next_wakeup: float | None = NOW + 10
        self.shortest_interval = 10
        self.calls: list[tuple] = []

    def due(self, *, now):
        self.calls.append(("due", now))
        return self.due_keys

    def mark_read(self, *, now):
        self.calls.append(("mark_read", now))

    def next_due(self, *, now, enabled):
        self.calls.append(("next_due", now, frozenset(enabled)))
        return self.next_wakeup

    def require_full_read(self):
        self.calls.append(("require_full_read",))


class FakeGuard:
    def __init__(self) -> None:
        self.delay = 20.0
        self.consecutive_failures = 0
        self.backoff_delay = 0.0
        self.calls: list[tuple] = []

    def failed(self, *, now, base_delay):
        self.calls.append(("failed", now, base_delay))
        return self.delay

    def succeeded(self):
        self.calls.append(("succeeded",))


class FakeHealth:
    def __init__(self) -> None:
        self.suspended_keys: frozenset[str] = frozenset()
        self.refused_keys: frozenset[str] = frozenset()
        self.retest_keys: frozenset[str] = frozenset()
        self.lifted: frozenset[str] = frozenset()
        self.newly_suspended: frozenset[str] = frozenset()
        self.refusals = {}
        self.narrowing: tuple[Region, ...] = ()
        self.breaks: frozenset[Break] = frozenset()
        self.calls: list[tuple] = []

    def suspended(self):
        return self.suspended_keys

    def refused(self):
        return self.refused_keys

    def retests_due(self, *, now):
        self.calls.append(("retests_due", now))
        return self.retest_keys

    def record_success(self, *, key):
        self.calls.append(("success", key))
        return key in self.lifted

    def record_request_read(self, *, rows):
        self.calls.append(("read", tuple(rows)))

    def record_request_refused(self, *, rows, keys, code, now):
        self.calls.append(("refused", tuple(rows), frozenset(keys), code, now))
        return self.newly_suspended


class Harness:
    def __init__(self, *, connected: bool = True) -> None:
        self.client = FakeClient(connected=connected)
        self.schedule = FakeSchedule()
        self.health = FakeHealth()
        self.guard = FakeGuard()
        self.time = NOW
        self.plans: list[dict] = []
        self.plan_length = 1
        self.reads: list[dict] = []
        self.outcomes: list[Readout | BaseException] = [Readout(values={}, refusals={})]
        self.identified: list[tuple] = []
        self.identity = DEVICE
        self.timeouts: list[float] = []
        self.deadline_expires = False

    def plan(self, *, device, enabled, narrowing, breaks):
        self.plans.append(
            {
                "device": device,
                "enabled": frozenset(enabled),
                "narrowing": narrowing,
                "breaks": breaks,
            }
        )
        return [
            ReadRange(address=0x4000 + index, count=1, keys=("k",))
            for index in range(self.plan_length)
        ]

    async def read(self, *, client, device, enabled, narrowing, breaks):
        self.reads.append(
            {
                "client": client,
                "device": device,
                "enabled": frozenset(enabled),
                "narrowing": narrowing,
                "breaks": breaks,
            }
        )
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    async def find_identity(self, *, client, selection):
        self.identified.append((client, selection))
        return self.identity

    enabled: frozenset[str] = frozenset({"a", "b", "c"})

    async def bound(self, awaitable, seconds):
        self.timeouts.append(seconds)
        if self.deadline_expires:
            awaitable.close()
            raise TimeoutError
        return await awaitable

    def clock(self) -> float:
        return self.time

    def poller(self) -> Poller:
        return Poller(
            target=Target(client=self.client, device=DEVICE, selection="automatic"),
            tracking=Tracking(
                schedule=self.schedule, health=self.health, guard=self.guard
            ),
            services=Services(
                clock=self.clock,
                bound=self.bound,
                plan=self.plan,
                read=self.read,
                identity=self.find_identity,
            ),
            enabled=self.enabled,
        )


def _readout(**values) -> Readout:
    return Readout(values=values, refusals={})


@pytest.mark.parametrize(
    ("due", "enabled", "suspended", "retests", "expected"),
    [
        ({"a", "b", "c"}, {"a", "b", "c"}, set(), set(), {"a", "b", "c"}),
        ({"a", "b", "c"}, {"a", "b"}, set(), set(), {"a", "b"}),
        ({"a", "b", "c"}, {"a", "b", "c"}, {"b"}, set(), {"a", "c"}),
        ({"a"}, {"a", "s"}, {"s"}, {"s"}, {"a", "s"}),
        ({"a"}, {"a"}, {"s"}, {"s"}, {"a"}),
        (set(), {"a", "s"}, {"s"}, {"s"}, {"s"}),
    ],
)
async def test_a_cycle_reads_due_enabled_unsuspended_keys_and_due_retests(
    due: set[str],
    enabled: set[str],
    suspended: set[str],
    retests: set[str],
    expected: set[str],
):
    harness = Harness()
    harness.schedule.due_keys = frozenset(due)
    harness.health.suspended_keys = frozenset(suspended)
    harness.health.retest_keys = frozenset(retests)

    await harness.poller().run(enabled=enabled)

    assert harness.reads[0]["enabled"] == expected
    assert harness.plans[0]["enabled"] == expected


async def test_pending_narrowing_and_breaks_are_passed_into_planning_and_reading():
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a", "b"})
    harness.health.narrowing = (Region(rows=(Row(address=0x4000, words=1),)),)
    harness.health.breaks = frozenset({Break(before=0x4001, after=0x4003)})

    poller = harness.poller()
    await poller.run(enabled={"a", "b"})

    assert harness.reads[0]["narrowing"] == harness.health.narrowing
    assert harness.reads[0]["breaks"] == harness.health.breaks
    assert harness.plans[0]["narrowing"] == harness.health.narrowing
    assert harness.plans[0]["breaks"] == harness.health.breaks
    assert poller.narrowing == harness.health.narrowing
    assert poller.breaks == harness.health.breaks


async def test_nothing_to_read_sends_no_request_and_still_serves_the_schedule():
    harness = Harness(connected=True)
    harness.schedule.due_keys = frozenset({"a"})
    harness.schedule.next_wakeup = NOW + 30

    result = await harness.poller().run(enabled=set())

    assert harness.reads == []
    assert harness.timeouts == []
    assert harness.client.events == []
    assert ("mark_read", NOW) in harness.schedule.calls
    assert result.values == {}
    assert result.read == frozenset()
    assert result.next_wakeup == NOW + 30


async def test_with_nothing_enabled_there_is_no_wakeup():
    harness = Harness()
    harness.schedule.next_wakeup = None

    result = await harness.poller().run(enabled=set())

    assert result.next_wakeup is None


@pytest.mark.parametrize("plan_length", [1, 3])
async def test_the_cycle_deadline_follows_the_read_plan(plan_length: int):
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a"})
    harness.plan_length = plan_length
    other = Harness()
    other.schedule.due_keys = frozenset({"a"})
    other.plan_length = plan_length + 2

    await harness.poller().run(enabled={"a"})
    await other.poller().run(enabled={"a"})

    assert other.timeouts[0] - harness.timeouts[0] == 2 * PER_REQUEST
    assert harness.timeouts[0] > plan_length * PER_REQUEST


async def test_a_successful_cycle_returns_values_and_updates_trackers():
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a", "b", "c"})
    harness.health.suspended_keys = frozenset({"s"})
    harness.health.refused_keys = frozenset({"c", "s"})
    harness.schedule.next_wakeup = NOW + 5
    harness.outcomes = [
        Readout(
            values={"a": 1, "b": None},
            refusals={"c": 2},
            outcomes=(
                RequestOutcome(rows=ROW_AB, keys=frozenset({"a", "b"}), code=None),
                RequestOutcome(rows=ROW_C, keys=frozenset({"c"}), code=2),
            ),
        )
    ]

    result = await harness.poller().run(enabled={"a", "b", "c"})

    assert result.values == {"a": 1, "b": None}
    assert result.read == {"a", "b"}
    assert result.refused == {"c": 2}
    assert result.suspended == {"s"}
    assert result.unavailable == {"c", "s"}
    assert result.next_wakeup == NOW + 5
    assert [call for call in harness.health.calls if call[0] != "retests_due"] == [
        ("success", "a"),
        ("success", "b"),
        ("read", ROW_AB),
        ("refused", ROW_C, frozenset({"c"}), 2, NOW),
    ]
    assert ("mark_read", NOW) in harness.schedule.calls
    assert ("succeeded",) in harness.guard.calls


async def test_the_next_wakeup_depends_on_the_schedule_alone_never_on_retests():
    harness = Harness()
    harness.health.retest_keys = frozenset({"s"})
    harness.schedule.next_wakeup = NOW + 25
    harness.time = NOW

    result = await harness.poller().run(enabled={"a", "s"})

    assert result.next_wakeup == NOW + 25
    assert ("next_due", NOW, frozenset({"a", "s"})) in harness.schedule.calls


async def test_the_next_wakeup_is_computed_after_the_cycle_has_finished():
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a"})

    async def slow_read(**_kwargs):
        harness.time = NOW + 40
        return _readout(a=1)

    harness.read = slow_read
    await harness.poller().run(enabled={"a"})

    assert ("mark_read", NOW) in harness.schedule.calls
    assert ("next_due", NOW + 40, frozenset({"a"})) in harness.schedule.calls


async def test_a_suspension_is_warned_once_and_a_lifted_suspension_is_informed(caplog):
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a", "b"})
    harness.health.newly_suspended = frozenset({"b"})
    harness.health.lifted = frozenset({"a"})
    harness.outcomes = [
        Readout(
            values={"a": 1},
            refusals={"b": 5},
            outcomes=(RequestOutcome(rows=ROW_C, keys=frozenset({"b"}), code=5),),
        )
    ]

    with caplog.at_level(logging.INFO):
        await harness.poller().run(enabled={"a", "b"})

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    infos = [r for r in caplog.records if r.levelno == logging.INFO]
    assert len(warnings) == 1
    assert "b" in warnings[0].getMessage()
    assert "5" in warnings[0].getMessage()
    assert len(infos) == 1
    assert "a" in infos[0].getMessage()


async def test_refusals_that_do_not_change_suspension_are_silent(caplog):
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a"})
    harness.outcomes = [
        Readout(
            values={},
            refusals={"a": 2},
            outcomes=(RequestOutcome(rows=ROW_C, keys=frozenset({"a"}), code=2),),
        )
    ]

    with caplog.at_level(logging.DEBUG):
        await harness.poller().run(enabled={"a"})

    assert [r for r in caplog.records if r.levelno >= logging.INFO] == []


LINK_FAILURES = [
    ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT),
    ModbusError(ModbusErrorMessage.MISMATCHED_HEADER),
    ModbusError(ModbusErrorMessage.CONNECTION_FAILED),
    TimeoutError(),
    OSError("socket"),
    ValueError("bad serial"),
    UnsupportedDeviceError(0x7777),
    IdentityChangedError(),
]
BUSY_FAILURES = [
    ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=4),
    ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=6),
]


@pytest.mark.parametrize("failure", [*LINK_FAILURES, *BUSY_FAILURES])
async def test_a_failed_cycle_raises_one_error_with_its_cause_and_the_backoff_wakeup(
    failure: Exception,
):
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a"})
    harness.guard.delay = 40
    harness.schedule.shortest_interval = 15
    harness.outcomes = [failure]

    with pytest.raises(CycleFailedError) as caught:
        await harness.poller().run(enabled={"a"})

    assert caught.value.cause is failure
    assert caught.value.__cause__ is failure
    assert caught.value.next_wakeup == NOW + 40
    assert harness.guard.calls == [("failed", NOW, 15)]
    assert ("require_full_read",) in harness.schedule.calls
    assert not [call for call in harness.schedule.calls if call[0] == "mark_read"]
    assert not [call for call in harness.health.calls if call[0] != "retests_due"]


@pytest.mark.parametrize(
    ("failure", "closes"),
    [(failure, True) for failure in LINK_FAILURES]
    + [(failure, False) for failure in BUSY_FAILURES],
)
async def test_only_link_failures_close_the_connection(
    failure: Exception, *, closes: bool
):
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a"})
    harness.outcomes = [failure]

    with pytest.raises(CycleFailedError):
        await harness.poller().run(enabled={"a"})

    assert ("close" in harness.client.events) is closes
    assert len(harness.reads) == 1


async def test_a_cycle_past_its_deadline_is_a_failed_cycle_and_closes():
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a"})
    harness.deadline_expires = True

    with pytest.raises(CycleFailedError) as caught:
        await harness.poller().run(enabled={"a"})

    assert isinstance(caught.value.cause, TimeoutError)
    assert "close" in harness.client.events


async def test_cancellation_closes_the_connection_and_propagates_without_a_failure():
    harness = Harness()
    harness.schedule.due_keys = frozenset({"a"})
    harness.outcomes = [asyncio.CancelledError()]

    with pytest.raises(asyncio.CancelledError):
        await harness.poller().run(enabled={"a"})

    assert harness.client.events == ["close"]
    assert harness.guard.calls == []


async def test_a_dropped_connection_is_reopened_with_identity_verified_before_reading():
    harness = Harness(connected=False)
    harness.schedule.due_keys = frozenset({"a"})

    await harness.poller().run(enabled={"a"})

    assert harness.client.events == ["close", "connect"]
    assert harness.identified == [(harness.client, "automatic")]
    assert ("require_full_read",) in harness.schedule.calls
    assert harness.schedule.calls.index(("require_full_read",)) < (
        harness.schedule.calls.index(("due", NOW))
    )


async def test_a_connected_client_is_not_reopened_or_forced_to_a_full_read():
    harness = Harness(connected=True)
    harness.schedule.due_keys = frozenset({"a"})

    await harness.poller().run(enabled={"a"})

    assert harness.client.events == []
    assert harness.identified == []
    assert ("require_full_read",) not in harness.schedule.calls


async def test_a_different_device_at_the_endpoint_fails_the_cycle_before_reading():
    harness = Harness(connected=False)
    harness.schedule.due_keys = frozenset({"a"})
    harness.identity = OTHER_DEVICE

    with pytest.raises(CycleFailedError) as caught:
        await harness.poller().run(enabled={"a"})

    assert isinstance(caught.value.cause, IdentityChangedError)
    assert harness.reads == []
    assert harness.client.events[-1] == "close"


def _stale(harness: Harness, *, requests: int = 1, peer_closed: bool = True):
    async def read(*, client, device, enabled, narrowing, breaks):
        harness.reads.append({"client": client, "enabled": frozenset(enabled)})
        if len(harness.reads) == 1:
            for _ in range(requests):
                await client.read_holding_registers(0, 1)
            raise ModbusError(
                ModbusErrorMessage.INCOMPLETE_RESPONSE, peer_closed=peer_closed
            )
        return _readout(a=1)

    harness.read = read


async def test_a_stale_connection_is_reopened_once_and_the_read_sent_again():
    harness = Harness(connected=True)
    harness.schedule.due_keys = frozenset({"a"})
    _stale(harness)
    poller = harness.poller()

    result = await poller.run(enabled={"a"})

    assert result.values == {"a": 1}
    assert len(harness.reads) == 2
    assert harness.reads[1]["client"] is harness.client
    assert harness.client.events == ["read", "close", "connect"]
    assert harness.identified == [(harness.client, "automatic")]
    assert poller.stale_reconnects == 1
    assert ("succeeded",) in harness.guard.calls


async def test_a_stale_reopen_is_followed_by_a_full_read_of_every_unsuspended_key():
    harness = Harness(connected=True)
    harness.schedule.due_keys = frozenset({"a"})
    harness.health.suspended_keys = frozenset({"s", "r"})
    harness.health.retest_keys = frozenset({"r"})
    _stale(harness)
    sizes = []

    def plan(*, device, enabled, narrowing, breaks):
        del device, narrowing, breaks
        sizes.append(len(enabled))
        return [
            ReadRange(address=index, count=1, keys=("k",))
            for index in range(len(enabled))
        ]

    harness.plan = plan

    await harness.poller().run(enabled={"a", "b", "s", "r", "gone"})

    assert harness.reads[0]["enabled"] == {"a", "r"}
    assert harness.reads[1]["enabled"] == {"a", "b", "r", "gone"}
    assert harness.timeouts == [(max(sizes) + RECONNECT_REQUESTS) * PER_REQUEST]
    assert max(sizes) == 4


async def test_a_second_failure_after_the_stale_reopen_is_not_retried_again():
    harness = Harness(connected=True)
    harness.schedule.due_keys = frozenset({"a"})
    _stale(harness)

    async def always_failing(*, client, device, enabled, narrowing, breaks):
        harness.reads.append({"client": client})
        await client.read_holding_registers(0, 1)
        raise ModbusError(ModbusErrorMessage.INCOMPLETE_RESPONSE, peer_closed=True)

    harness.read = always_failing
    poller = harness.poller()

    with pytest.raises(CycleFailedError):
        await poller.run(enabled={"a"})

    assert len(harness.reads) == 2
    assert poller.stale_reconnects == 1


async def test_a_stale_reopen_that_finds_another_device_fails_the_cycle():
    harness = Harness(connected=True)
    harness.schedule.due_keys = frozenset({"a"})
    harness.identity = OTHER_DEVICE
    _stale(harness)

    with pytest.raises(CycleFailedError) as caught:
        await harness.poller().run(enabled={"a"})

    assert isinstance(caught.value.cause, IdentityChangedError)
    assert len(harness.reads) == 1


@pytest.mark.parametrize(
    ("connected", "requests", "peer_closed"),
    [
        (True, 2, True),
        (True, 1, False),
        (False, 1, True),
    ],
)
async def test_only_a_peer_close_on_the_first_request_of_a_kept_connection_is_stale(
    *, connected: bool, requests: int, peer_closed: bool
):
    harness = Harness(connected=connected)
    harness.schedule.due_keys = frozenset({"a"})
    _stale(harness, requests=requests, peer_closed=peer_closed)
    poller = harness.poller()

    with pytest.raises(CycleFailedError):
        await poller.run(enabled={"a"})

    assert len(harness.reads) == 1
    assert poller.stale_reconnects == 0


async def test_cadence_plans_describe_each_cadence_and_its_request_count():
    harness = Harness()
    harness.schedule = FakeSchedule(
        [
            Cadence(interval=60, keys=frozenset({"a", "b"}), default=True),
            Cadence(interval=10, keys=frozenset({"c"})),
        ]
    )
    harness.plan_length = 2

    poller = harness.poller()

    assert poller.cadence_plans() == (
        CadencePlan(
            interval=60,
            keys=frozenset({"a", "b"}),
            ranges=((0x4000, 1), (0x4001, 1)),
            default=True,
        ),
        CadencePlan(
            interval=10,
            keys=frozenset({"c"}),
            ranges=((0x4000, 1), (0x4001, 1)),
            default=False,
        ),
    )
    assert harness.plans[0]["narrowing"] == ()
    assert harness.plans[0]["breaks"] == frozenset()


async def test_poller_exposes_failure_and_refusal_state_for_diagnostics():
    harness = Harness()
    harness.guard.consecutive_failures = 3
    harness.guard.backoff_delay = 40.0
    harness.health.refusals = {"a": Refusal(count=1, code=2, retest_at=None)}
    poller = harness.poller()

    assert poller.consecutive_failures == 3
    assert poller.backoff_seconds == 40.0
    assert poller.refusals == {"a": Refusal(count=1, code=2, retest_at=None)}


def test_the_identity_error_carries_a_fixed_message():
    assert "identity" in str(IdentityChangedError())


def test_a_failed_cycle_error_reads_like_its_cause():
    error = CycleFailedError(cause=ValueError("bad"), next_wakeup=1)

    assert str(error) == "bad"


LOAD_DEVICE = Device(
    "SERIAL-1",
    1,
    6000,
    profile(
        base=HS3,
        key="gamma",
        device_types={1},
        keys=(
            "operating_mode",
            "battery_soc",
            "pv_power",
            "battery_power",
            "grid_power",
        ),
        hand_verified=True,
    ),
    detected=True,
)
FAST_POWERS = frozenset({"pv_power", "battery_power", "grid_power"})
SLOW_STATUS = frozenset({"operating_mode", "battery_soc"})


@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        (SLOW_STATUS | FAST_POWERS, 2 * 60 / 60 + 1 * 60 / 10),
        (SLOW_STATUS | {"pv_power"}, 2 * 60 / 60 + 1 * 60 / 10),
        (SLOW_STATUS, 2 * 60 / 60),
        (frozenset(), 0),
    ],
)
async def test_the_planned_load_counts_enabled_keys_of_each_cadence_planned_alone(
    enabled: frozenset[str], expected: float
):
    harness = Harness()
    harness.schedule = FakeSchedule(
        [
            Cadence(interval=60, keys=SLOW_STATUS, default=True),
            Cadence(interval=10, keys=FAST_POWERS),
        ]
    )
    poller = Poller(
        target=Target(client=harness.client, device=LOAD_DEVICE, selection="automatic"),
        tracking=Tracking(
            schedule=harness.schedule, health=harness.health, guard=harness.guard
        ),
        services=Services(clock=harness.clock, bound=harness.bound, read=harness.read),
        enabled=enabled,
    )

    assert poller.planned_load() == expected
    assert [plan.keys for plan in poller.cadence_plans()] == [
        SLOW_STATUS & enabled,
        FAST_POWERS & enabled,
    ]


class MemoryPollerClient(FakeClient):
    def __init__(self, memory: MemoryClient) -> None:
        super().__init__()
        self.memory = memory

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        return await self.memory.read_holding_registers(address=address, count=count)


POWER_DEVICE = Device(
    "SERIAL-1",
    1,
    6000,
    profile(
        base=HS3,
        key="delta",
        device_types={1},
        keys=("load_power", "pv_power", "battery_power", "grid_power"),
        hand_verified=True,
    ),
    detected=True,
)
POWER_KEYS = frozenset({"load_power", "pv_power", "battery_power", "grid_power"})
LOAD_ADDRESS = 0x40A0
PV_ADDRESS = 0x40A5
BATTERY_ADDRESS = 0x40A6
GRID_ADDRESS = 0x40A7


def _narrowing_poller(*, bad_address: int) -> tuple[Poller, MemoryClient]:
    harness = Harness()
    harness.schedule.due_keys = POWER_KEYS
    memory = MemoryClient(bad_addresses=frozenset({bad_address}))
    client = MemoryPollerClient(memory)
    return (
        Poller(
            target=Target(client=client, device=POWER_DEVICE, selection="automatic"),
            tracking=Tracking(
                schedule=harness.schedule, health=ReadHealth(), guard=harness.guard
            ),
            services=Services(clock=harness.clock, bound=harness.bound),
            enabled=POWER_KEYS,
        ),
        memory,
    )


async def test_a_refused_request_is_narrowed_until_the_refused_row_is_alone():
    poller, memory = _narrowing_poller(bad_address=BATTERY_ADDRESS)

    results = [await poller.run(enabled=POWER_KEYS) for _ in range(4)]

    assert memory.reads == [
        (LOAD_ADDRESS, 8),
        (LOAD_ADDRESS, 1),
        (PV_ADDRESS, 3),
        (LOAD_ADDRESS, 1),
        (PV_ADDRESS, 1),
        (BATTERY_ADDRESS, 2),
        (LOAD_ADDRESS, BATTERY_ADDRESS - LOAD_ADDRESS),
        (BATTERY_ADDRESS, 1),
        (GRID_ADDRESS, 1),
    ]
    assert [result.read for result in results] == [
        frozenset(),
        {"load_power"},
        {"load_power", "pv_power"},
        {"load_power", "pv_power", "grid_power"},
    ]
    assert poller.narrowing == (Region(rows=(Row(address=BATTERY_ADDRESS, words=1),)),)
    assert poller.breaks == frozenset()
    assert set(poller.refusals) == {"battery_power"}
    assert poller.refusals["battery_power"].count == 1


async def test_a_single_row_refused_three_times_in_a_row_is_suspended():
    poller, _ = _narrowing_poller(bad_address=BATTERY_ADDRESS)

    results = [await poller.run(enabled=POWER_KEYS) for _ in range(6)]

    assert results[-2].suspended == frozenset()
    assert results[-1].suspended == {"battery_power"}
    assert poller.refusals["battery_power"].count == REFUSAL_THRESHOLD


async def test_a_fault_in_a_gap_word_is_found_as_a_break_that_later_cycles_keep():
    harness = Harness()
    keys = frozenset({"load_power", "grid_power"})
    harness.schedule.due_keys = keys
    memory = MemoryClient(bad_addresses=frozenset({LOAD_ADDRESS + 3}))
    poller = Poller(
        target=Target(
            client=MemoryPollerClient(memory),
            device=POWER_DEVICE,
            selection="automatic",
        ),
        tracking=Tracking(
            schedule=harness.schedule, health=ReadHealth(), guard=harness.guard
        ),
        services=Services(clock=harness.clock, bound=harness.bound),
        enabled=keys,
    )

    for _ in range(4):
        await poller.run(enabled=keys)

    assert memory.reads == [
        (LOAD_ADDRESS, 8),
        (LOAD_ADDRESS, 1),
        (GRID_ADDRESS, 1),
        (LOAD_ADDRESS, 1),
        (GRID_ADDRESS, 1),
        (LOAD_ADDRESS, 1),
        (GRID_ADDRESS, 1),
    ]
    assert poller.breaks == {Break(before=LOAD_ADDRESS + 1, after=GRID_ADDRESS)}
    assert poller.narrowing == ()
