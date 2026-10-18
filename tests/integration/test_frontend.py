from __future__ import annotations

import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.saj_local import frontend
from custom_components.saj_local.const import DOMAIN

BUNDLE = "bundle-abc123.js"
MANIFEST = {
    "src/helper.ts": {"file": "helper-1.js", "src": "src/helper.ts"},
    "src/entry.ts": {"file": BUNDLE, "src": "src/entry.ts", "isEntry": True},
}


class FakeHass:
    def __init__(self) -> None:
        self.http = SimpleNamespace(async_register_static_paths=AsyncMock())

    async def async_add_executor_job(self, target, *args):
        return target(*args)


@pytest.fixture
def added_urls(monkeypatch) -> list[str]:
    urls: list[str] = []

    def add(hass, url):
        del hass
        urls.append(url)

    monkeypatch.setattr(frontend, "add_extra_js_url", add)
    return urls


def _write_manifest(directory, content) -> None:
    (directory / frontend.MANIFEST_NAME).write_text(content, encoding="utf-8")


async def test_the_entry_bundle_is_served_with_cache_headers_and_registered(
    tmp_path, added_urls
):
    _write_manifest(tmp_path, json.dumps(MANIFEST))
    hass = FakeHass()

    await frontend.async_register_frontend(hass=hass, directory=tmp_path)

    url = f"/{DOMAIN}/{BUNDLE}"
    (paths,) = hass.http.async_register_static_paths.await_args.args
    assert [(path.url_path, path.path, path.cache_headers) for path in paths] == [
        (url, str(tmp_path / BUNDLE), True)
    ]
    assert added_urls == [url]


@pytest.mark.parametrize(
    "content",
    [
        None,
        "not json",
        "[]",
        json.dumps({"src/entry.ts": {"file": BUNDLE}}),
        json.dumps({"src/entry.ts": {"isEntry": True}}),
        json.dumps({"src/entry.ts": "text"}),
    ],
    ids=[
        "missing-file",
        "not-json",
        "not-an-object",
        "no-entry",
        "entry-without-file",
        "entry-not-an-object",
    ],
)
async def test_an_unreadable_manifest_logs_one_error_and_registers_nothing(
    tmp_path, added_urls, caplog, content
):
    if content is not None:
        _write_manifest(tmp_path, content)
    hass = FakeHass()

    with caplog.at_level(logging.ERROR, logger=frontend.__name__):
        await frontend.async_register_frontend(hass=hass, directory=tmp_path)

    assert [record.levelno for record in caplog.records] == [logging.ERROR]
    assert str(tmp_path / frontend.MANIFEST_NAME) in caplog.text
    hass.http.async_register_static_paths.assert_not_awaited()
    assert added_urls == []
