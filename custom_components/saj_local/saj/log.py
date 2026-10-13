from __future__ import annotations

import logging
import re
from typing import Any

SERIAL_MASK = "xxxxx"
SERIAL_VISIBLE_CHARACTERS = 3
LOG_CALLER_STACKLEVEL = 2


def mask_serial(*, serial: str) -> str:
    if len(serial) <= SERIAL_VISIBLE_CHARACTERS:
        return SERIAL_MASK
    return SERIAL_MASK + serial[-SERIAL_VISIBLE_CHARACTERS:]


def system_label(*, title: str, serial: str | None) -> str:
    if not serial:
        return title
    masked = mask_serial(serial=serial)
    in_title = re.compile(re.escape(serial), re.IGNORECASE)
    if in_title.search(title):
        return in_title.sub(masked, title)
    return f"{title} ({masked})" if title else masked


class LabelledLogger(logging.LoggerAdapter[logging.Logger]):
    def __init__(self, *, logger: logging.Logger, label: str) -> None:
        super().__init__(logger, {})
        self.prefix = f"{label}: "
        self._escaped_prefix = self.prefix.replace("%", "%%")

    def log(self, level: int, msg: object, *args: object, **kwargs: Any) -> None:
        if not self.isEnabledFor(level):
            return
        prefix = self._escaped_prefix if args else self.prefix
        kwargs.setdefault("stacklevel", LOG_CALLER_STACKLEVEL)
        labelled = prefix + str(msg)
        self.logger.log(level, labelled, *args, **kwargs)
