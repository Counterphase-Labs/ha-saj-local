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
    return recorded
