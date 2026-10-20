from dataclasses import replace

import pytest

from saj.errors import (
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
    WriteError,
    WriteMismatchError,
    WriteRejectedError,
    WriteUnconfirmedError,
)
from saj.models import PowerFunction
from saj.models.hs3 import PROFILE as HS3

DEVICE_TYPE = 0x0123
LIMIT = 5
WINDOW = 2.5


def test_an_unsupported_device_error_names_the_device_type_and_keeps_it():
    error = UnsupportedDeviceError(DEVICE_TYPE)

    assert error.device_type == DEVICE_TYPE
    assert f"{DEVICE_TYPE:04x}" in str(error).lower()


def test_a_model_mismatch_error_names_both_models_and_keeps_them():
    selected = replace(HS3, key="selected")
    detected = replace(HS3, key="detected")

    error = ModelMismatchError(selected=selected, detected=detected)

    assert error.selected is selected
    assert error.detected is detected
    assert "selected" in str(error)
    assert "detected" in str(error)


@pytest.mark.parametrize("problem", list(ValueProblem))
def test_an_invalid_value_error_reports_the_problem(problem: ValueProblem):
    error = InvalidValueError(problem)

    assert error.problem is problem
    assert str(problem) in str(error)


def test_a_link_unavailable_error_without_a_cause_is_not_a_link_failure():
    error = LinkUnavailableError()

    assert error.cause is None
    assert error.link_failed is False


def test_a_link_unavailable_error_with_a_cause_is_a_link_failure():
    cause = OSError("refused")

    error = LinkUnavailableError(cause=cause)

    assert error.cause is cause
    assert error.link_failed is True


def test_a_write_allowance_error_names_the_limit_and_the_window():
    error = WriteAllowanceError(limit=LIMIT, window=WINDOW)

    assert (error.limit, error.window) == (LIMIT, WINDOW)
    assert str(LIMIT) in str(error)
    assert f"{WINDOW:g}" in str(error)


@pytest.mark.parametrize("acknowledged", [True, False])
def test_an_unconfirmed_write_is_a_link_failure_that_keeps_its_cause(
    *, acknowledged: bool
):
    cause = TimeoutError("late")

    error = WriteUnconfirmedError(cause=cause, acknowledged=acknowledged)

    assert error.link_failed is True
    assert error.cause is cause
    assert error.acknowledged is acknowledged
    assert str(cause) in str(error)


def test_a_write_error_is_not_a_link_failure_unless_it_says_so():
    assert WriteError.link_failed is False


def test_the_power_function_is_named_in_its_error_messages():
    function = PowerFunction.GRID

    assert str(function) in str(NoPowerTargetError(function=function))
    assert str(function) in str(AnotherFunctionRunningError(running=function))


@pytest.mark.parametrize(
    ("error", "detail"),
    [
        (UnknownModelError("mystery"), "mystery"),
        (ProtectedSettingError("grid_code"), "grid_code"),
        (UnknownSettingError("odd_setting"), "odd_setting"),
        (UnusablePowerError(minimum=-40, maximum=90), "-40"),
        (UnusablePowerError(minimum=-40, maximum=90), "90"),
        (EmsTimeoutError(timeout=17, interval=23), "17"),
        (EmsTimeoutError(timeout=17, interval=23), "23"),
        (WriteRejectedError(exception_code=11), "11"),
    ],
)
def test_an_error_message_carries_the_detail_it_was_raised_with(
    error: Exception, detail: str
):
    assert detail in str(error)


@pytest.mark.parametrize(
    "error",
    [
        ControlDisabledError(),
        ModelUnverifiedError(),
        SeparateRegistersError(),
        ProtectedSettingError("key"),
        UnknownSettingError("key"),
        UnusablePowerError(minimum=1, maximum=2),
        WriteRejectedError(exception_code=None),
        WriteMismatchError(read_back={}),
    ],
)
def test_a_refused_write_is_a_write_error_that_is_not_a_link_failure(
    error: WriteError,
):
    assert isinstance(error, WriteError)
    assert error.link_failed is False
    assert str(error)


@pytest.mark.parametrize("error", [UnsupportedDeviceError(1), UnknownModelError("x")])
def test_a_model_problem_is_a_model_error(error: Exception):
    assert isinstance(error, ModelError)


def test_the_stored_attributes_of_each_error_match_what_it_was_raised_with():
    read_back = {"register": 3}

    assert UnknownModelError("x").selection == "x"
    assert ProtectedSettingError("p").key == "p"
    assert UnknownSettingError("u").key == "u"
    assert WriteRejectedError(exception_code=4).exception_code == 4
    assert WriteMismatchError(read_back=read_back).read_back is read_back
    assert UnusablePowerError(minimum=1, maximum=2).minimum == 1
    assert EmsTimeoutError(timeout=1, interval=2).interval == 2
    assert NoPowerTargetError(function=PowerFunction.GRID).function is (
        PowerFunction.GRID
    )
    assert (
        AnotherFunctionRunningError(running=PowerFunction.BATTERY).running
        is PowerFunction.BATTERY
    )
