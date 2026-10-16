import pytest

from saj_modbus_mock.exceptions import ControlError, ExceptionCode, ModbusError


@pytest.mark.parametrize("code", list(ExceptionCode))
def test_a_modbus_error_carries_its_exception_code(code):
    error = ModbusError(code=code)

    assert error.code is code
    assert code.name in str(error)


@pytest.mark.parametrize(
    ("code", "text"), [(0x00, "0x00"), (0x7F, "0x7F"), (0x81, "0x81"), (0xFF, "0xFF")]
)
def test_a_modbus_error_carries_any_byte_as_its_code(code, text):
    error = ModbusError(code=code)

    assert error.code == code
    assert text in str(error)


def test_busy_and_device_failure_have_their_wire_values():
    assert ExceptionCode.BUSY == 0x06
    assert ExceptionCode.DEVICE_FAILURE == 0x04


def test_vendor_codes_have_their_wire_values():
    assert ExceptionCode.BLOCK_OVERRUN == 0x36
    assert ExceptionCode.CHARGER_UNAVAILABLE == 0x30


def test_a_refused_change_says_which_key_and_why_in_the_scenario_parsers_words():
    error = ControlError(key="app_mode", reason="value outside enumeration")

    assert str(error) == "app_mode: value outside enumeration"
    assert (error.key, error.reason) == ("app_mode", "value outside enumeration")
