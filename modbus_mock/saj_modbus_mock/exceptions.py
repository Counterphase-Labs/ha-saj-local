import enum


class ExceptionCode(enum.IntEnum):
    ILLEGAL_FUNCTION = 0x01
    ILLEGAL_DATA_ADDRESS = 0x02
    ILLEGAL_DATA_VALUE = 0x03
    BLOCK_OVERRUN = 0x36
    CHARGER_UNAVAILABLE = 0x30


class ModbusError(Exception):
    def __init__(self, *, code: ExceptionCode) -> None:
        super().__init__(code.name)
        self.code = code
