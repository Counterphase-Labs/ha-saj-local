import pytest

from saj_modbus_mock.exceptions import ExceptionCode, ModbusError


@pytest.mark.parametrize("code", list(ExceptionCode))
def test_a_modbus_error_carries_its_exception_code(code):
    error = ModbusError(code=code)

    assert error.code is code
    assert code.name in str(error)


def test_vendor_codes_have_their_wire_values():
    assert ExceptionCode.BLOCK_OVERRUN == 0x36
    assert ExceptionCode.CHARGER_UNAVAILABLE == 0x30
