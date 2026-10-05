import pytest

from saj_modbus_mock.models import H2, HS3, MODELS


@pytest.mark.parametrize("name", [HS3, H2])
def test_each_model_exists_under_its_own_name_with_a_rating_it_supports(name):
    spec = MODELS[name]

    assert spec.name == name
    assert spec.default_rated_power_w in spec.rated_powers_w
    assert spec.phases in {1, 3}


def test_only_the_three_phase_model_supports_the_optional_equipment():
    assert MODELS[HS3].supports_ev_charger
    assert MODELS[HS3].supports_parallel
    assert MODELS[HS3].supports_meter_b
    assert not MODELS[H2].supports_ev_charger
    assert not MODELS[H2].supports_parallel
    assert not MODELS[H2].supports_meter_b


def test_the_models_have_distinct_device_types_and_serials():
    assert MODELS[HS3].device_type != MODELS[H2].device_type
    assert MODELS[HS3].default_serial_number != MODELS[H2].default_serial_number
