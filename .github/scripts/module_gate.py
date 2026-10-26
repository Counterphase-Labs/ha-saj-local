from __future__ import annotations

import contextlib
import io
import json
import re
import sys
from pathlib import Path

import coverage
from pytest_scope import module_tests

STANDARD_OUTPUT = "-"
EMPTY_CONTEXT = "^$"
EXIT_ARC = "exit"


def contexts_of(test_files: tuple[Path, ...]) -> list[str]:
    names = "|".join(re.escape(test_file.as_posix()) for test_file in test_files)
    return [EMPTY_CONTEXT, f"^(?:{names})::"]


def _arc(arc: list[int]) -> str:
    start, end = arc
    return f"{start}->{end if end > 0 else EXIT_ARC}"


def module_gap(
    measured: coverage.Coverage, *, module: Path, test_files: tuple[Path, ...]
) -> str | None:
    if not test_files:
        return f"{module.as_posix()}: no unit test file"
    report = io.StringIO()
    with contextlib.redirect_stdout(report):
        measured.json_report(
            morfs=[module.as_posix()],
            outfile=STANDARD_OUTPUT,
            contexts=contexts_of(test_files),
        )
    (entry,) = json.loads(report.getvalue())["files"].values()
    missing = [
        *(str(line) for line in entry["missing_lines"]),
        *(_arc(arc) for arc in entry["missing_branches"]),
    ]
    if not missing:
        return None
    percent = entry["summary"]["percent_covered"]
    return f"{module.as_posix()}: {percent:.1f}% missing {', '.join(missing)}"


def main(argv: list[str]) -> int:
    data_file, *names = argv
    mapping = module_tests(Path.cwd())
    measured = coverage.Coverage(data_file=data_file, config_file=False)
    measured.load()
    gaps = [
        gap
        for name in names
        if (
            gap := module_gap(
                measured,
                module=Path(name),
                test_files=mapping.get(Path(name), ()),
            )
        )
    ]
    for gap in gaps:
        sys.stdout.write(f"finding {gap}\n")
    sys.stdout.write(f"{len(names) - len(gaps)} of {len(names)} modules covered\n")
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
