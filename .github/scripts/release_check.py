from __future__ import annotations

import re
import sys
import tempfile
import zipfile
from pathlib import Path

ASSET_MANIFEST_ENTRY = "saj_local/frontend/asset-manifest.json"
BUNDLE_ENTRY = "saj_local/frontend/saj-local-<hash>.js"
REQUIRED_ENTRIES = (
    (ASSET_MANIFEST_ENTRY, re.compile(r"^saj_local/frontend/asset-manifest\.json$")),
    (BUNDLE_ENTRY, re.compile(r"^saj_local/frontend/saj-local-[A-Za-z0-9_-]+\.js$")),
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


def main() -> int:
    missing = missing_entries(archive_entries(Path("custom_components")))
    for label in missing:
        sys.stdout.write(f"missing {label}\n")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
