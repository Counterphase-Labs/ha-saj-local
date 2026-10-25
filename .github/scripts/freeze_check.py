from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

SURFACE_SCRIPT = "freeze_surface.py"
SURFACE_SCRIPT_IN_TREE = Path(".github/scripts") / SURFACE_SCRIPT
ARCHIVE_NAME = "release.tar"
NO_TAG_MESSAGE = "no stable release tag"
STABLE_TAG_PATTERN = "[0-9]*.[0-9]*.[0-9]*"
BETA_TAG_PATTERN = "*b*"
COMMAND_TIMEOUT_SECONDS = 300
NO_OUTPUT = "no output"
RISING_VERSIONS = frozenset(
    {
        ("stored", "config_flow", "VERSION"),
        ("stored", "config_flow", "MINOR_VERSION"),
        ("stored", "power_control_store", "version"),
    }
)
Run = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]
Unpack = Callable[[str, str], None]


class SurfaceUnavailableError(Exception):
    pass


def run_command(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=False,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )


def newest_tag(*, run: Run) -> str | None:
    described = run(
        (
            "git",
            "describe",
            "--tags",
            "--abbrev=0",
            "--match",
            STABLE_TAG_PATTERN,
            "--exclude",
            BETA_TAG_PATTERN,
        )
    )
    return described.stdout.strip() if described.returncode == 0 else None


def extract_tag(*, tag: str, destination: Path, run: Run, unpack: Unpack) -> None:
    archive = destination / ARCHIVE_NAME
    archived = run(("git", "archive", "--format=tar", f"--output={archive}", tag))
    if archived.returncode != 0:
        message = f"git archive of {tag} failed: {_last_line(archived.stderr)}"
        raise SurfaceUnavailableError(message)
    unpack(str(archive), str(destination / "tree"))


def surface_of(*, script: Path, tree: Path, run: Run) -> dict[str, Any]:
    printed = run((sys.executable, str(script), str(tree)))
    if printed.returncode != 0:
        message = f"surface of {tree} failed: {_last_line(printed.stderr)}"
        raise SurfaceUnavailableError(message)
    surface: dict[str, Any] = json.loads(printed.stdout)
    return surface


def _last_line(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else NO_OUTPUT


def _shown(value: object) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def breaks(*, frozen: object, current: object, path: tuple[str, ...] = ()) -> list[str]:
    if isinstance(frozen, dict) and isinstance(current, dict):
        found: list[str] = []
        for key, old in frozen.items():
            if key not in current:
                found.append(f"{' '.join((*path, key))}: missing")
            else:
                found.extend(
                    breaks(frozen=old, current=current[key], path=(*path, key))
                )
        return found
    if isinstance(frozen, list) and isinstance(current, list):
        return [
            f"{' '.join(path)}: missing {_shown(item)}"
            for item in frozen
            if item not in current
        ]
    if frozen == current:
        return []
    if (
        path in RISING_VERSIONS
        and isinstance(frozen, int)
        and isinstance(current, int)
        and current > frozen
    ):
        return []
    *parents, name = path
    return [f"{' '.join(parents)}: {name} {_shown(frozen)} -> {_shown(current)}"]


def main(
    *,
    run: Run = run_command,
    unpack: Unpack = shutil.unpack_archive,
    root: Path | None = None,
) -> int:
    tag = newest_tag(run=run)
    if tag is None:
        sys.stdout.write(f"{NO_TAG_MESSAGE}\n")
        return 0
    tree = Path.cwd() if root is None else root
    with tempfile.TemporaryDirectory() as scratch:
        try:
            extract_tag(tag=tag, destination=Path(scratch), run=run, unpack=unpack)
            frozen_tree = Path(scratch) / "tree"
            frozen = surface_of(
                script=frozen_tree / SURFACE_SCRIPT_IN_TREE, tree=frozen_tree, run=run
            )
            current = surface_of(
                script=Path(__file__).with_name(SURFACE_SCRIPT), tree=tree, run=run
            )
        except SurfaceUnavailableError as error:
            sys.stdout.write(f"error {error}\n")
            return 1
    found = breaks(frozen=frozen, current=current)
    for line in found:
        sys.stdout.write(f"{line}\n")
    if not found:
        sys.stdout.write(f"surface kept since {tag}\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
