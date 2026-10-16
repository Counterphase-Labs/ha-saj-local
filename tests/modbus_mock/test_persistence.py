import asyncio
import itertools
import json
import logging

import pytest

from saj_modbus_mock import persistence
from saj_modbus_mock.persistence import Saver, StateStore, scenario_hash
from tests.modbus_mock.builders import make_scenario

SNAPSHOT = {"settings": {"app_mode": 6}, "soc_percent": 41.5}


def mounted(_path):
    return True


def unmounted(_path):
    return False


def store(*, path, scenario_hash="abc", is_mount=mounted):
    return StateStore(path=path, scenario_hash=scenario_hash, is_mount=is_mount)


def test_the_scenario_hash_is_stable_and_differs_when_anything_in_it_changes():
    scenario = make_scenario(model="hs3")

    assert scenario_hash(scenario=scenario) == scenario_hash(
        scenario=make_scenario(model="hs3")
    )
    assert scenario_hash(scenario=scenario) != scenario_hash(
        scenario=make_scenario(model="hs3", battery={"modules": 3})
    )
    assert scenario_hash(scenario=scenario) != scenario_hash(
        scenario=make_scenario(model="h2")
    )


def test_a_saved_state_is_loaded_back(tmp_path):
    path = tmp_path / "state.json"
    store(path=path).save(snapshot=SNAPSHOT)

    assert store(path=path).load() == SNAPSHOT


def test_nothing_is_loaded_when_nothing_was_saved(tmp_path):
    assert store(path=tmp_path / "state.json").load() is None


def test_a_state_saved_for_another_scenario_is_ignored_with_one_log_line(
    tmp_path, caplog
):
    path = tmp_path / "state.json"
    store(path=path, scenario_hash="old").save(snapshot=SNAPSHOT)

    with caplog.at_level(logging.WARNING):
        loaded = store(path=path, scenario_hash="new").load()

    assert loaded is None
    assert [record.getMessage() for record in caplog.records] == [
        "the scenario changed since the state was saved; starting from the scenario"
    ]


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        "[1, 2]",
        json.dumps({"version": 99, "scenario_hash": "abc", "state": {}}),
        json.dumps({"scenario_hash": "abc", "state": {}}),
    ],
)
def test_a_file_that_cannot_be_read_is_ignored_with_one_log_line(
    tmp_path, caplog, content
):
    path = tmp_path / "state.json"
    path.write_text(content, encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        loaded = store(path=path).load()

    assert loaded is None
    assert len(caplog.records) == 1
    assert "starting from the scenario" in caplog.records[0].getMessage()


def test_a_file_whose_state_is_not_a_mapping_loads_as_nothing(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(
        json.dumps(
            {"version": persistence.STATE_VERSION, "scenario_hash": "abc", "state": 5}
        ),
        encoding="utf-8",
    )

    assert store(path=path).load() is None


def test_a_directory_in_place_of_the_file_is_unreadable_not_fatal(tmp_path, caplog):
    path = tmp_path / "state.json"
    path.mkdir()

    with caplog.at_level(logging.WARNING):
        assert store(path=path).load() is None

    assert len(caplog.records) == 1


def test_saving_writes_a_temporary_file_and_renames_it_so_a_crash_leaves_the_old_state(
    tmp_path, monkeypatch
):
    path = tmp_path / "state.json"
    state = store(path=path)
    state.save(snapshot=SNAPSHOT)
    seen = []

    def crash(self, target):
        seen.append(sorted(entry.name for entry in tmp_path.iterdir()))
        raise OSError

    monkeypatch.setattr(type(path), "replace", crash)

    state.save(snapshot={"settings": {"app_mode": 0}})

    assert seen == [["state.json", "state.json.tmp"]]
    assert json.loads(path.read_text(encoding="utf-8"))["state"] == SNAPSHOT


def test_a_save_leaves_no_temporary_file_behind(tmp_path):
    path = tmp_path / "state.json"

    store(path=path).save(snapshot=SNAPSHOT)

    assert [entry.name for entry in tmp_path.iterdir()] == ["state.json"]


def test_a_failing_save_logs_once_until_it_works_again(tmp_path, caplog, monkeypatch):
    path = tmp_path / "state.json"
    state = store(path=path)
    original = type(path).write_text

    def failing(self, *args, **kwargs):
        raise OSError

    monkeypatch.setattr(type(path), "write_text", failing)
    with caplog.at_level(logging.WARNING):
        state.save(snapshot=SNAPSHOT)
        state.save(snapshot=SNAPSHOT)
    assert len(caplog.records) == 1

    monkeypatch.setattr(type(path), "write_text", original)
    state.save(snapshot=SNAPSHOT)
    monkeypatch.setattr(type(path), "write_text", failing)
    with caplog.at_level(logging.WARNING):
        state.save(snapshot=SNAPSHOT)

    assert len(caplog.records) == 2


def test_deleting_removes_the_file_and_is_harmless_without_one(tmp_path):
    path = tmp_path / "state.json"
    state = store(path=path)
    state.save(snapshot=SNAPSHOT)

    state.delete()
    state.delete()

    assert not path.exists()


def test_without_a_volume_one_line_is_logged_and_nothing_is_kept_or_loaded(
    tmp_path, caplog
):
    path = tmp_path / "state.json"
    path.write_text("{}", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        state = store(path=path, is_mount=unmounted)
        state.save(snapshot=SNAPSHOT)
        state.delete()

    assert state.enabled is False
    assert state.load() is None
    assert path.read_text(encoding="utf-8") == "{}"
    assert [record.getMessage() for record in caplog.records] == [
        f"no volume is mounted at {tmp_path}, so changes will not be kept"
    ]


def test_a_volume_is_a_mount_over_the_directory_of_the_state_file(tmp_path):
    asked = []

    def is_mount(path):
        asked.append(path)
        return True

    state = StateStore(
        path=tmp_path / "state.json", scenario_hash="x", is_mount=is_mount
    )

    assert state.enabled is True
    assert asked == [tmp_path]


class FakeStore:
    def __init__(self):
        self.saved = []

    def save(self, *, snapshot):
        self.saved.append(snapshot)


class FakeTime:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def saver(*, time, store=None, pause=None):
    store = store or FakeStore()
    taken = []

    def snapshot():
        taken.append(time.now)
        return {"taken_at": time.now}

    kwargs = {} if pause is None else {"pause": pause}
    return Saver(store=store, snapshot=snapshot, monotonic=time, **kwargs), store, taken


@pytest.mark.parametrize(
    ("changed", "waited", "saves"),
    [
        (False, 0.5, 0),
        (False, 30, 0),
        (False, 60, 1),
        (True, 0.5, 0),
        (True, 1, 1),
        (True, 5, 1),
    ],
)
def test_a_change_is_saved_after_a_second_and_otherwise_every_minute(
    changed, waited, saves
):
    time = FakeTime()
    state, store, _ = saver(time=time)
    if changed:
        state.changed()

    time.now += waited
    state.tick()

    assert len(store.saved) == saves


def test_changes_arriving_in_a_burst_are_saved_at_most_once_a_second():
    time = FakeTime()
    state, store, _ = saver(time=time)

    for _ in range(10):
        state.changed()
        time.now += 0.3
        state.tick()

    times = [saved["taken_at"] for saved in store.saved]
    assert len(times) == 2
    assert all(later - earlier >= 1 for earlier, later in itertools.pairwise(times))


def test_a_save_clears_the_change_so_the_same_one_is_not_saved_twice():
    time = FakeTime()
    state, store, _ = saver(time=time)
    state.changed()
    time.now += 2
    state.tick()

    time.now += 2
    state.tick()

    assert len(store.saved) == 1


def test_flushing_saves_the_snapshot_now_whatever_the_timing():
    time = FakeTime()
    state, store, taken = saver(time=time)

    state.flush()

    assert store.saved == [{"taken_at": 1000.0}]
    assert taken == [1000.0]


async def test_running_ticks_every_second_until_cancelled():
    time = FakeTime()
    pauses = []

    async def pause(seconds):
        pauses.append(seconds)
        time.now += seconds
        if len(pauses) == 3:
            raise asyncio.CancelledError

    state, store, _ = saver(time=time, pause=pause)
    state.changed()

    with pytest.raises(asyncio.CancelledError):
        await state.run()

    assert pauses == [persistence.TICK_S] * 3
    assert len(store.saved) == 1
