import enum


class ExceptionCode(enum.IntEnum):
    ILLEGAL_FUNCTION = 0x01
    ILLEGAL_DATA_ADDRESS = 0x02
    ILLEGAL_DATA_VALUE = 0x03
    DEVICE_FAILURE = 0x04
    BUSY = 0x06
    BLOCK_OVERRUN = 0x36
    CHARGER_UNAVAILABLE = 0x30


class ControlError(Exception):
    """A change from the control panel that was refused, and why."""

    def __init__(self, *, key: str, reason: str) -> None:
        super().__init__(f"{key}: {reason}")
        self.key = key
        self.reason = reason


class ModbusError(Exception):
    def __init__(self, *, code: int) -> None:
        name = ExceptionCode(code).name if code in ExceptionCode else f"0x{code:02X}"
        super().__init__(name)
        self.code = code
