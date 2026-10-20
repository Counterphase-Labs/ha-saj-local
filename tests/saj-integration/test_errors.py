import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.errors import (
    Translation,
    WriteOutcome,
    has_safe_message,
    read_back_values,
    rejection_code,
    translate_error,
    write_failure,
    write_outcome,
)
from custom_components.saj_local.saj import errors as saj_errors
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.errors import (
    AnotherFunctionRunningError,
    ControlDisabledError,
    EmsTimeoutError,
    InvalidValueError,
    LinkUnavailableError,
    ModelError,
    ModelMismatchError,
    ModelUnverifiedError,
    NoPowerTargetError,
    ProtectedSettingError,
    SeparateRegistersError,
    UnknownModelError,
    UnknownSettingError,
    UnsupportedDeviceError,
    UnusablePowerError,
    ValueProblem,
    WriteAllowanceError,
    WriteMismatchError,
    WriteRejectedError,
    WriteUnconfirmedError,
)
from custom_components.saj_local.saj.models import PowerFunction
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


WRITE_FAILURES = [
    (ControlDisabledError(), "control_not_enabled", {}, True),
    (ModelUnverifiedError(), "model_unverified", {}, True),
    (
        ProtectedSettingError("rs485_address"),
        "protected_setting",
        {"setting": "rs485_address"},
        True,
    ),
    (
        UnknownSettingError("nothing"),
        "unknown_setting",
        {"setting": "nothing"},
        True,
    ),
    (SeparateRegistersError(), "separate_registers", {}, True),
    *(
        (InvalidValueError(problem), f"invalid_value_{problem.value}", {}, True)
        for problem in ValueProblem
    ),
    (LinkUnavailableError(), "link_unavailable", {}, True),
    (
        WriteAllowanceError(limit=10, window=60.0),
        "write_allowance",
        {"limit": "10", "window": "60"},
        True,
    ),
    (
        EmsTimeoutError(timeout=30, interval=60),
        "ems_timeout_too_short",
        {"timeout": "30", "interval": "60"},
        True,
    ),
    (
        NoPowerTargetError(function=PowerFunction.BATTERY),
        "no_power_target",
        {"function": "battery"},
        True,
    ),
    (
        AnotherFunctionRunningError(running=PowerFunction.GRID),
        "another_function_running",
        {"running": "grid"},
        True,
    ),
    (
        UnusablePowerError(minimum=-8800, maximum=8800),
        "unusable_power",
        {"minimum": "-8800", "maximum": "8800"},
        True,
    ),
    (
        WriteRejectedError(exception_code=3),
        "write_rejected",
        {"exception_code": "3"},
        False,
    ),
    (
        WriteRejectedError(exception_code=None),
        "write_rejected",
        {"exception_code": "unknown"},
        False,
    ),
    (
        WriteUnconfirmedError(cause=TimeoutError(), acknowledged=True),
        "write_unconfirmed",
        {},
        False,
    ),
    (WriteMismatchError(read_back={}), "write_mismatch", {}, False),
]


@pytest.mark.parametrize(("error", "key", "placeholders", "refusal"), WRITE_FAILURES)
def test_each_write_error_has_its_own_message_and_a_kind_that_says_who_failed(
    error, key, placeholders, *, refusal
):
    failure = write_failure(error=error)

    assert failure.translation_domain == DOMAIN
    assert failure.translation_key == key
    assert (failure.translation_placeholders or {}) == placeholders
    assert isinstance(failure, ServiceValidationError) is refusal
    assert isinstance(failure, HomeAssistantError)


def test_every_write_error_the_library_defines_is_translated():
    defined = {
        error
        for error in vars(saj_errors).values()
        if isinstance(error, type)
        and issubclass(error, saj_errors.WriteError)
        and error is not saj_errors.WriteError
    }
    translated = {type(error) for error, *_ in WRITE_FAILURES}

    assert defined == translated


class UntranslatedWriteError(saj_errors.WriteError):
    pass


def test_a_write_error_without_a_translation_fails_loudly():
    with pytest.raises(NotImplementedError, match="UntranslatedWriteError"):
        write_failure(error=UntranslatedWriteError())


@pytest.mark.parametrize(
    ("error", "outcome", "code", "read_back"),
    [
        (WriteRejectedError(exception_code=2), WriteOutcome.REJECTED, 2, {}),
        (
            WriteUnconfirmedError(cause=TimeoutError(), acknowledged=False),
            WriteOutcome.UNCONFIRMED,
            None,
            {},
        ),
        (
            WriteMismatchError(read_back={"a": 1}),
            WriteOutcome.MISMATCHED,
            None,
            {"a": 1},
        ),
        (ControlDisabledError(), None, None, {}),
    ],
)
def test_a_device_outcome_is_classified_with_its_code_and_read_back(
    error, outcome, code, read_back
):
    assert write_outcome(error=error) is outcome
    assert rejection_code(error=error) == code
    assert read_back_values(error=error) == read_back


@pytest.mark.parametrize(
    ("error", "placeholders"),
    [
        (NoPowerTargetError(function=PowerFunction.BATTERY), {"function": "Batterie"}),
        (
            AnotherFunctionRunningError(running=PowerFunction.GRID),
            {"running": "Netz"},
        ),
        (
            WriteAllowanceError(limit=10, window=60.0),
            {"limit": "10", "window": "60"},
        ),
    ],
)
def test_a_message_names_a_function_by_its_translated_name_only(error, placeholders):
    failure = write_failure(
        error=error, function_names={"battery": "Batterie", "grid": "Netz"}
    )

    assert failure.translation_placeholders == placeholders
