import pytest

from custom_components.saj_local.errors import (
    Translation,
    has_safe_message,
    translate_error,
)
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.errors import (
    ModelError,
    ModelMismatchError,
    UnknownModelError,
    UnsupportedDeviceError,
)
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from tests.profiles import profile

ALPHA = profile(base=HS3, key="alpha", device_types={1}, keys=(), hand_verified=True)
BETA = profile(base=HS3, key="beta", device_types={2}, keys=(), hand_verified=False)


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            UnsupportedDeviceError(0x1234),
            Translation(
                key="unsupported_device",
                concerns_model=True,
                placeholders={"device_type": "0x1234"},
            ),
        ),
        (
            ModelMismatchError(selected=ALPHA, detected=BETA),
            Translation(
                key="model_mismatch",
                concerns_model=True,
                placeholders={"selected_model": "Alpha", "detected_model": "Beta"},
            ),
        ),
        (
            UnknownModelError("gamma"),
            Translation(
                key="unknown_model",
                concerns_model=True,
                placeholders={"selection": "gamma"},
            ),
        ),
        (ValueError("malformed"), Translation(key="invalid_device_data")),
        (TimeoutError("private"), Translation(key="timeout")),
        (
            ModbusError(ModbusErrorMessage.CONNECTION_TIMEOUT),
            Translation(key="timeout"),
        ),
        (ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT), Translation(key="timeout")),
        (
            ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2),
            Translation(key="read_rejected"),
        ),
        (
            ModbusError(ModbusErrorMessage.MISMATCHED_HEADER),
            Translation(key="cannot_connect"),
        ),
        (OSError("private"), Translation(key="cannot_connect")),
    ],
)
def test_translate_error_maps_each_failure_to_key_and_placeholders(error, expected):
    assert translate_error(error=error) == expected


class UntranslatedModelError(ModelError):
    pass


def test_translate_error_fails_loudly_for_a_model_error_without_translator():
    with pytest.raises(NotImplementedError, match="UntranslatedModelError"):
        translate_error(error=UntranslatedModelError())


@pytest.mark.parametrize(
    ("error", "safe"),
    [
        (UnknownModelError("gamma"), True),
        (ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT), True),
        (OSError("private host"), False),
        (ValueError("private serial"), False),
    ],
)
def test_has_safe_message_admits_only_library_authored_errors(error, safe):
    assert has_safe_message(error=error) is safe
