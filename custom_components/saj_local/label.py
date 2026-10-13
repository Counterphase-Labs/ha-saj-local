from typing import TYPE_CHECKING

from .saj.log import LabelledLogger, system_label

if TYPE_CHECKING:
    import logging

    from homeassistant.config_entries import ConfigEntry


def entry_label(*, entry: ConfigEntry) -> str:
    return system_label(title=entry.title, serial=entry.unique_id)


def entry_logger(*, logger: logging.Logger, entry: ConfigEntry) -> LabelledLogger:
    return LabelledLogger(logger=logger, label=entry_label(entry=entry))
