from __future__ import annotations

import runpy

import pytest
import release_check


def populate(root, names):
    for name in names:
        path = root / "custom_components" / "saj_local" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x", encoding="utf-8")


def test_the_archive_contains_the_integration_files_under_their_directory(tmp_path):
    populate(tmp_path, ["__init__.py", "frontend/asset-manifest.json"])

    entries = release_check.archive_entries(tmp_path / "custom_components")

    assert sorted(entries) == [
        "saj_local/__init__.py",
        "saj_local/frontend/asset-manifest.json",
    ]


def test_a_complete_archive_has_nothing_missing():
    entries = [
        "saj_local/frontend/asset-manifest.json",
        "saj_local/frontend/saj-local-aB3_-x.js",
    ]

    assert release_check.missing_entries(entries) == []


def test_each_absent_required_entry_is_reported_by_name():
    assert release_check.missing_entries(["saj_local/__init__.py"]) == [
        "saj_local/frontend/asset-manifest.json",
        "saj_local/frontend/saj-local-<hash>.js",
    ]


def test_a_bundle_with_an_unexpected_name_does_not_count():
    entries = [
        "saj_local/frontend/asset-manifest.json",
        "saj_local/frontend/saj-local-.js",
    ]

    assert release_check.missing_entries(entries) == [
        "saj_local/frontend/saj-local-<hash>.js"
    ]


def test_main_reports_missing_entries_and_fails(tmp_path, monkeypatch, capsys):
    populate(tmp_path, ["__init__.py"])
    monkeypatch.chdir(tmp_path)

    assert release_check.main() == 1
    assert capsys.readouterr().out == (
        "missing saj_local/frontend/asset-manifest.json\n"
        "missing saj_local/frontend/saj-local-<hash>.js\n"
    )


def test_main_succeeds_for_a_complete_archive(tmp_path, monkeypatch, capsys):
    populate(tmp_path, ["frontend/asset-manifest.json", "frontend/saj-local-abc.js"])
    monkeypatch.chdir(tmp_path)

    assert release_check.main() == 0
    assert capsys.readouterr().out == ""


def test_running_the_check_as_a_script_exits_with_the_status_of_main(
    tmp_path, monkeypatch
):
    populate(tmp_path, ["__init__.py"])
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("release_check", run_name="__main__")

    assert stopped.value.code == 1
