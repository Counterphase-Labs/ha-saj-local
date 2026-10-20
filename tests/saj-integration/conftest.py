import pytest

from custom_components.saj_local import coordinator as coordinator_module
from tests.coordinators import Recorder


@pytest.fixture
def recorder(monkeypatch) -> Recorder:
    recorded = Recorder()
    monkeypatch.setattr(coordinator_module, "async_track_time_interval", recorded.track)
    monkeypatch.setattr(
        coordinator_module, "async_track_state_change_event", recorded.listen
    )
    monkeypatch.setattr(coordinator_module, "device_registers", lambda **_: ())
    monkeypatch.setattr(coordinator_module, "hidden_sources", lambda **_: frozenset())
    for name in (
        "check_unreachable",
        "clear_model_issues",
        "clear_unreachable",
        "raise_model_issue",
        "sync_refusals",
    ):
        monkeypatch.setattr(coordinator_module, name, lambda **_: None)
    monkeypatch.setattr(coordinator_module, "model_finding", lambda **_: None)
    monkeypatch.setattr(coordinator_module, "open_refusals", lambda **_: frozenset())
    return recorded
