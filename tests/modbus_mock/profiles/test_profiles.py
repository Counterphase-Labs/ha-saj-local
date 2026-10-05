from types import SimpleNamespace

import pytest

from saj_modbus_mock import profiles
from tests.modbus_mock.builders import make_scenario


@pytest.fixture(autouse=True)
def stubbed_models(monkeypatch):
    for name in ("hs3", "h2"):
        monkeypatch.setattr(
            profiles,
            name,
            SimpleNamespace(
                build_blocks=lambda *, scenario, name=name: (name, scenario),
                OVERRUN_CODE=f"{name}-overrun",
            ),
        )


@pytest.mark.parametrize("model", ["hs3", "h2"])
def test_blocks_are_built_by_the_profile_of_the_scenarios_model(model):
    scenario = make_scenario(model=model)

    assert profiles.build_blocks(scenario=scenario) == (model, scenario)


@pytest.mark.parametrize("model", ["hs3", "h2"])
def test_the_overrun_exception_belongs_to_the_model(model):
    assert (
        profiles.overrun_code(scenario=make_scenario(model=model)) == f"{model}-overrun"
    )
