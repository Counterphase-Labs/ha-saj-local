from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

BUNDLE_DIRECTORY = Path(__file__).parent / "frontend"
MANIFEST_NAME = "asset-manifest.json"
READ_FAILURES = (OSError, ValueError, KeyError, AttributeError)


class BundleNotFoundError(Exception):
    pass


def bundle_file_name(*, directory: Path) -> str:
    entries = json.loads((directory / MANIFEST_NAME).read_text(encoding="utf-8"))
    name = next(
        (entry["file"] for entry in entries.values() if entry.get("isEntry")), None
    )
    if name is None:
        raise BundleNotFoundError
    return str(name)


async def async_register_frontend(
    *, hass: HomeAssistant, directory: Path = BUNDLE_DIRECTORY
) -> None:
    try:
        name = await hass.async_add_executor_job(
            lambda: bundle_file_name(directory=directory)
        )
    except (BundleNotFoundError, *READ_FAILURES):
        _LOGGER.exception(
            "Cannot read the cards bundle from %s, so the SAJ Local cards are not "
            "available",
            directory / MANIFEST_NAME,
        )
        return
    url = f"/{DOMAIN}/{name}"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(url_path=url, path=str(directory / name), cache_headers=True)]
    )
    add_extra_js_url(hass, url)
