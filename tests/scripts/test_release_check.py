from __future__ import annotations

import json
import runpy
import subprocess

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
        "saj_local/frontend/THIRD_PARTY_LICENSES.md",
    ]

    assert release_check.missing_entries(entries) == []


def test_each_absent_required_entry_is_reported_by_name():
    assert release_check.missing_entries(["saj_local/__init__.py"]) == [
        "saj_local/frontend/asset-manifest.json",
        "saj_local/frontend/saj-local-<hash>.js",
        "saj_local/frontend/THIRD_PARTY_LICENSES.md",
    ]


def test_a_bundle_with_an_unexpected_name_does_not_count():
    entries = [
        "saj_local/frontend/asset-manifest.json",
        "saj_local/frontend/saj-local-.js",
        "saj_local/frontend/THIRD_PARTY_LICENSES.md",
    ]

    assert release_check.missing_entries(entries) == [
        "saj_local/frontend/saj-local-<hash>.js"
    ]


COMPLETE_ARCHIVE = [
    "frontend/asset-manifest.json",
    "frontend/saj-local-abc.js",
    "frontend/THIRD_PARTY_LICENSES.md",
]


def completed(*, stdout="", returncode=0):
    return subprocess.CompletedProcess(
        args=(), returncode=returncode, stdout=stdout, stderr=""
    )


def untagged(argv):
    del argv
    return completed(returncode=128)


def tagged(tag):
    def describe(argv):
        assert argv == ("git", "describe", "--tags", "--exact-match", "HEAD")
        return completed(stdout=f"{tag}\n")

    return describe


def write_versions(root, *, manifest="1.0.0", pyproject="1.0.0", package="1.0.0"):
    manifest_path = root / "custom_components" / "saj_local" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({"version": manifest}), encoding="utf-8")
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "x"\nversion = "{pyproject}"\n', encoding="utf-8"
    )
    (root / "frontend").mkdir(exist_ok=True)
    (root / "frontend" / "package.json").write_text(
        json.dumps({"version": package}), encoding="utf-8"
    )


def release(root, *, run=untagged, **versions):
    populate(root, COMPLETE_ARCHIVE)
    write_versions(root, **versions)
    return release_check.main(run=run, root=root)


def test_main_reports_missing_entries_and_fails(tmp_path, capsys):
    populate(tmp_path, ["__init__.py"])
    write_versions(tmp_path)

    assert release_check.main(run=untagged, root=tmp_path) == 1
    assert capsys.readouterr().out == (
        "missing saj_local/frontend/asset-manifest.json\n"
        "missing saj_local/frontend/saj-local-<hash>.js\n"
        "missing saj_local/frontend/THIRD_PARTY_LICENSES.md\n"
    )


@pytest.mark.parametrize("version", ["1.0.0", "1.0.0b1", "0.1.0"])
def test_three_equal_versions_pass(tmp_path, capsys, version):
    status = release(tmp_path, manifest=version, pyproject=version, package=version)

    assert status == 0
    assert capsys.readouterr().out == ""


def test_one_differing_file_is_reported_with_all_three_values(tmp_path, capsys):
    status = release(tmp_path, package="1.0.1")

    assert status == 1
    assert capsys.readouterr().out == (
        "version mismatch: manifest.json 1.0.0, pyproject.toml 1.0.0, "
        "frontend/package.json 1.0.1\n"
    )


def test_a_version_in_another_form_is_reported_per_file(tmp_path, capsys):
    status = release(tmp_path, manifest="v1.0", pyproject="1.0", package="1.0.0")

    assert status == 1
    assert capsys.readouterr().out.splitlines() == [
        "version manifest.json: v1.0 is not X.Y.Z or X.Y.ZbN",
        "version pyproject.toml: 1.0 is not X.Y.Z or X.Y.ZbN",
        (
            "version mismatch: manifest.json v1.0, pyproject.toml 1.0, "
            "frontend/package.json 1.0.0"
        ),
    ]


def test_a_tag_equal_to_the_version_passes(tmp_path, capsys):
    assert release(tmp_path, run=tagged("1.0.0")) == 0
    assert capsys.readouterr().out == ""


def test_a_differing_tag_is_reported(tmp_path, capsys):
    status = release(tmp_path, run=tagged("0.1.0b1"))

    assert status == 1
    assert capsys.readouterr().out == "tag 0.1.0b1 differs from version 1.0.0\n"


def test_no_tag_at_head_skips_the_comparison(tmp_path, capsys):
    assert release(tmp_path, run=untagged) == 0
    assert capsys.readouterr().out == ""


def test_the_default_root_is_the_working_directory(tmp_path, monkeypatch, capsys):
    populate(tmp_path, COMPLETE_ARCHIVE)
    write_versions(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert release_check.main(run=untagged) == 0
    capsys.readouterr()


def test_running_the_check_as_a_script_exits_with_the_status_of_main(
    tmp_path, monkeypatch
):
    populate(tmp_path, ["__init__.py"])
    write_versions(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(subprocess, "run", lambda argv, **_: untagged(argv))

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("release_check", run_name="__main__")

    assert stopped.value.code == 1
