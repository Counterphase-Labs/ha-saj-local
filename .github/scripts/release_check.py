from __future__ import annotations

import json
import re
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

from freeze_check import Run, run_command

MANIFEST = "manifest.json"
PYPROJECT = "pyproject.toml"
PACKAGE = "frontend/package.json"
MANIFEST_PATH = "custom_components/saj_local/manifest.json"
VERSION_FORM = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+)?$")
ASSET_MANIFEST_ENTRY = "saj_local/frontend/asset-manifest.json"
BUNDLE_ENTRY = "saj_local/frontend/saj-local-<hash>.js"
LICENCES_ENTRY = "saj_local/frontend/THIRD_PARTY_LICENSES.md"
REQUIRED_ENTRIES = (
    (ASSET_MANIFEST_ENTRY, re.compile(r"^saj_local/frontend/asset-manifest\.json$")),
    (BUNDLE_ENTRY, re.compile(r"^saj_local/frontend/saj-local-[A-Za-z0-9_-]+\.js$")),
    (LICENCES_ENTRY, re.compile(r"^saj_local/frontend/THIRD_PARTY_LICENSES\.md$")),
)


def archive_entries(components_directory: Path) -> list[str]:
    with tempfile.TemporaryDirectory() as scratch:
        archive_path = Path(scratch) / "saj_local.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            for path in sorted((components_directory / "saj_local").rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(components_directory))
        with zipfile.ZipFile(archive_path) as archive:
            return archive.namelist()


def missing_entries(entries: list[str]) -> list[str]:
    return [
        label
        for label, pattern in REQUIRED_ENTRIES
        if not any(pattern.match(entry) for entry in entries)
    ]


def read_versions(root: Path) -> dict[str, str]:
    pyproject = tomllib.loads((root / PYPROJECT).read_text(encoding="utf-8"))
    return {
        MANIFEST: json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))[
            "version"
        ],
        PYPROJECT: pyproject["project"]["version"],
        PACKAGE: json.loads((root / PACKAGE).read_text(encoding="utf-8"))["version"],
    }


def version_findings(versions: dict[str, str]) -> list[str]:
    findings = [
        f"version {name}: {value} is not X.Y.Z or X.Y.ZbN"
        for name, value in versions.items()
        if not VERSION_FORM.match(value)
    ]
    if len(set(versions.values())) > 1:
        shown = ", ".join(f"{name} {value}" for name, value in versions.items())
        findings.append(f"version mismatch: {shown}")
    return findings


def tag_findings(*, version: str, run: Run) -> list[str]:
    described = run(("git", "describe", "--tags", "--exact-match", "HEAD"))
    tag = described.stdout.strip()
    if described.returncode != 0 or tag == version:
        return []
    return [f"tag {tag} differs from version {version}"]


def main(*, run: Run = run_command, root: Path = Path()) -> int:
    findings = [
        f"missing {label}"
        for label in missing_entries(archive_entries(root / "custom_components"))
    ]
    versions = read_versions(root)
    findings += version_findings(versions)
    findings += tag_findings(version=versions[MANIFEST], run=run)
    for finding in findings:
        sys.stdout.write(f"{finding}\n")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
