import pytest

from saj.device_type import format_device_type


@pytest.mark.parametrize(
    ("device_type", "text"), [(0x1610, "0x1610"), (0x5A, "0x005a"), (0, "0x0000")]
)
def test_device_type_is_formatted_as_four_digit_hexadecimal(
    device_type: int, text: str
):
    assert format_device_type(device_type) == text
