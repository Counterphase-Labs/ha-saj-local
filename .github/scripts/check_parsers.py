from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class Finding:
    file: str | None
    line: int | None
    message: str


@dataclass(frozen=True)
class Parsed:
    summary: str
    details: tuple[str, ...] = ()
    findings: tuple[Finding, ...] = ()


type Parser = Callable[[str, int], Parsed]

UV_WARNING_PREFIX = "warning: "

_PYTEST_RESULT_LINE = re.compile(
    r"^(?:=+ )?(?P<counts>(?:\d+ \w+(?:, )?)+|no tests ran) in [\d.]+s"
    r"(?: \([\d:]+\))?(?: =+)?$"
)
_COVERAGE_COUNTS = r"\s+\d+\s+\d+(?:\s+\d+\s+\d+)?"
_PYTEST_TOTAL = re.compile(rf"^TOTAL{_COVERAGE_COUNTS}\s+(?P<percent>\d+(?:\.\d+)?)%$")
_PYTEST_ROW = re.compile(
    rf"^(?P<file>\S.*?){_COVERAGE_COUNTS}\s+(?P<percent>\d+(?:\.\d+)?)%"
    r"(?:\s+(?P<missing>\S.*))?$"
)
_FULL_COVERAGE = 100
_PYTEST_WARNING_COUNT = re.compile(r"^(?P<count>\d+) warnings?$")
_PYTEST_GATE = re.compile(
    r"Required test coverage of (?P<required>\d+(?:\.\d+)?)% not reached"
)
_PYTEST_SECTION = re.compile(r"^_{2,} (?P<name>.+?) _{2,}$")
_PYTEST_LOCATION = re.compile(r"^(?P<file>\S+\.py):(?P<line>\d+): ")
_PYTEST_HEADER = re.compile(r"^=+ (?P<title>.+?) =+$")
_RUFF_FINDING = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):\d+: (?P<code>\S+) (?P<message>.*)$"
)
_RUFF_REFORMAT = re.compile(r"^(?P<file>.+?):\d+:\d+: unformatted: .*$")
_MYPY_LINE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+): (?P<level>error|note|warning): (?P<message>.*)$"
)
_COMPLEXIPY_LINE = re.compile(r"^(?P<file>\S+) (?P<function>\S+) (?P<score>\d+)$")
_JSCPD_CLONE = re.compile(
    r"^(?:(?P<prefix>\S+/) )?"
    r"(?P<first>\S+?)(?::[a-z]+)?:(?P<first_start>\d+)-(?P<first_end>\d+) ~ "
    r"(?P<second>\S+?)(?::[a-z]+)?:(?P<second_start>\d+)-(?P<second_end>\d+)$"
)
_JSCPD_SAME_FILE_CLONE = re.compile(
    r"^(?P<file>\S+?)(?::[a-z]+)? (?P<first_start>\d+)-(?P<first_end>\d+) ~ "
    r"(?P<second_start>\d+)-(?P<second_end>\d+)$"
)
_TSC_LINE = re.compile(
    r"^(?P<file>.+?)\((?P<line>\d+),\d+\): error (?P<code>TS\d+): (?P<message>.*)$"
)
_ESLINT_LINE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):\d+ (?P<rule>\S+) (?P<message>.*)$"
)
_PRETTIER_LINE = re.compile(r"^\[(?P<level>warn|error)\] (?P<message>.*)$")
_VITEST_TESTS = re.compile(r"^\s*Tests\s+(?P<counts>.+?)(?: \(\d+\))?\s*$")
_VITEST_THRESHOLD = re.compile(r"does not meet .*threshold")
_VITEST_LOCATION = re.compile(r"^\s*\u276f (?P<file>\S+\.\w+):(?P<line>\d+):\d+$")
_VITEST_SUMMARY_START = re.compile(r"^\s*Test Files\s")
_VITEST_FAILURE_START = re.compile(r"^\s*(FAIL|Failed Tests|Error:)")
_PLAYWRIGHT_RESULT = re.compile(
    r"^\s*(?P<count>\d+) (?P<kind>passed|failed|flaky|skipped)\b"
)
_PLAYWRIGHT_FAILURE = re.compile(
    r"^\s+\d+\) (?P<file>\S+\.ts):(?P<line>\d+):\d+ \u203a (?P<name>.*?)(?: \u2500+)?$"
)
_VITE_ASSET = re.compile(r"^\S*?(?P<name>[\w.-]+\.(?:js|json|css))\s+[\d.]+ k?B")
_HASSFEST_INTEGRATION = re.compile(r"^Integration \S+ - (?P<path>\S+):$")
_HASSFEST_ERROR = re.compile(r"^\* \[ERROR\] \[(?P<check>\w+)\] (?P<message>.*)$")
_IMPORT_LINTER_SUMMARY = re.compile(
    r"^Contracts: (?P<kept>\d+) kept, (?P<broken>\d+) broken\.$"
)
_IMPORT_LINTER_RULE = re.compile(r"^-+$")
_IMPORT_LINTER_BANNER = re.compile(
    "^[\\s\u2554\u2557\u255a\u255d\u2551\u2566\u2569\u256c\u2563\u2560\u2550"
    "\u2500\u2502\u25b6\u25c0\u2514\u2510\u2518\u25b2]+$"
)
_IMPORT_LINTER_BROKEN_TITLE = "Broken contracts"
_NPM_BANNER = re.compile(r"^> \S+@\S+ \S")
_WORKSPACE_PREFIX = "/github/workspace/"
_PYTEST_SLOW_CALL = re.compile(r"^(?P<seconds>\d+(?:\.\d+)?)s call\s+(?P<test>\S.*)$")
_MODULE_GATE_FINDING = re.compile(r"^finding (?P<module>\S+): (?P<message>.*)$")
_MODULE_GATE_SUMMARY = re.compile(r"^\d+ of \d+ modules covered$")


def _lines(output: str) -> list[str]:
    return [line.rstrip() for line in output.splitlines() if line.strip()]


def strip_npm_banner(lines: list[str]) -> list[str]:
    kept: list[str] = []
    skip_command = False
    for line in lines:
        if skip_command and line.startswith("> "):
            skip_command = False
            continue
        skip_command = bool(_NPM_BANNER.match(line))
        if not skip_command:
            kept.append(line)
    return kept


def _npm_lines(output: str) -> list[str]:
    return strip_npm_banner(_lines(output))


def relative_path(path: str) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        return path
    try:
        return candidate.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path


def _plural(count: int, noun: str) -> str:
    if count == 0:
        return "failed"
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _pytest_failure_sections(lines: list[str]) -> list[list[str]]:
    sections: list[list[str]] = []
    collecting = False
    for line in lines:
        header = _PYTEST_HEADER.match(line)
        if header:
            collecting = header["title"] in {"FAILURES", "ERRORS"}
            continue
        if not collecting:
            continue
        if _PYTEST_SECTION.match(line) or not sections:
            sections.append([line])
        else:
            sections[-1].append(line)
    return sections


def _pytest_findings(sections: list[list[str]]) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    for section in sections:
        name = _PYTEST_SECTION.match(section[0])
        locations = [
            match for line in section if (match := _PYTEST_LOCATION.match(line))
        ]
        reasons = [line[1:].strip() for line in section if line.startswith("E ")]
        if not locations:
            continue
        message = reasons[0] if reasons else "failed"
        findings.append(
            Finding(
                locations[-1]["file"],
                int(locations[-1]["line"]),
                f"{name['name'] if name else 'test'}: {message}",
            )
        )
    return tuple(findings)


def _pytest_coverage_rows(lines: list[str]) -> list[str]:
    rows: list[str] = []
    for line in lines:
        match = _PYTEST_ROW.match(line)
        if (
            match
            and not line.startswith(("TOTAL", "Name"))
            and float(match["percent"]) < _FULL_COVERAGE
        ):
            missing = f"  {match['missing']}" if match["missing"] else ""
            rows.append(f"{relative_path(match['file'])}  {match['percent']}%{missing}")
    return rows


def _pytest_warnings(lines: list[str]) -> list[str]:
    warnings: list[str] = []
    collecting = False
    for line in lines:
        header = _PYTEST_HEADER.match(line)
        if header:
            collecting = header["title"] == "warnings summary"
            continue
        if _PYTEST_RESULT_LINE.match(line):
            collecting = False
        if collecting and not line.startswith("-- "):
            warnings.append(line)
    return warnings


def _pytest_slow_calls(lines: list[str]) -> list[Finding]:
    return [
        Finding(
            match["test"].split("::", 1)[0],
            None,
            f"{match['test']} took {match['seconds']}s in the test body",
        )
        for line in lines
        if (match := _PYTEST_SLOW_CALL.match(line))
    ]


def _pytest_summary_counts(counts: str) -> str:
    kept: list[str] = []
    warnings = ""
    for part in counts.split(", "):
        if _PYTEST_WARNING_COUNT.match(part):
            warnings = part
        else:
            kept.append(part)
    return "  ".join(part for part in (", ".join(kept), warnings) if part)


def parse_pytest(output: str, return_code: int) -> Parsed:
    lines = _lines(output)
    counts = ""
    coverage = ""
    for line in lines:
        result = _PYTEST_RESULT_LINE.match(line)
        if result:
            counts = _pytest_summary_counts(result["counts"])
        total = _PYTEST_TOTAL.match(line)
        if total:
            coverage = f"{total['percent']}% cov"
    slow = _pytest_slow_calls(lines)
    slow_count = f"{len(slow)} too slow" if slow else ""
    summary = "  ".join(part for part in (counts, coverage, slow_count) if part) or (
        "passed" if return_code == 0 else "failed"
    )
    sections = _pytest_failure_sections(lines)
    details = [line for section in sections for line in section]
    details.extend(line for line in lines if line.startswith(("FAILED ", "ERROR ")))
    details.extend(_pytest_warnings(lines))
    details.extend(_pytest_coverage_rows(lines))
    details.extend(line for line in lines if _PYTEST_GATE.search(line))
    details.extend(finding.message for finding in slow)
    return Parsed(summary, tuple(details), (*_pytest_findings(sections), *slow))


def parse_module_gate(output: str, return_code: int) -> Parsed:
    del return_code
    lines = _lines(output)
    summary = next((line for line in lines if _MODULE_GATE_SUMMARY.match(line)), None)
    if summary is None:
        return Parsed("failed", tuple(lines))
    findings = tuple(
        Finding(m["module"], None, m["message"])
        for line in lines
        if (m := _MODULE_GATE_FINDING.match(line))
    )
    details = tuple(f"{finding.file}  {finding.message}" for finding in findings)
    return Parsed(summary, details, findings)


def parse_ruff_format(output: str, return_code: int) -> Parsed:
    files = [m["file"] for line in _lines(output) if (m := _RUFF_REFORMAT.match(line))]
    if return_code == 0:
        return Parsed("formatted")
    findings = tuple(Finding(file, None, "would be reformatted") for file in files)
    details = tuple(f"{file}: would be reformatted" for file in files)
    return Parsed(f"{len(files)} to format" if files else "failed", details, findings)


def parse_ruff_check(output: str, return_code: int) -> Parsed:
    matches = [m for line in _lines(output) if (m := _RUFF_FINDING.match(line))]
    if return_code == 0:
        return Parsed("no findings")
    findings = tuple(
        Finding(relative_path(m["file"]), int(m["line"]), f"{m['code']} {m['message']}")
        for m in matches
    )
    details = tuple(
        f"{finding.file}:{finding.line} {finding.message}" for finding in findings
    )
    return Parsed(_plural(len(findings), "finding"), details, findings)


def parse_mypy(output: str, return_code: int) -> Parsed:
    matches = [m for line in _lines(output) if (m := _MYPY_LINE.match(line))]
    if return_code == 0:
        return Parsed("no errors")
    errors = [m for m in matches if m["level"] == "error"]
    findings = tuple(
        Finding(relative_path(m["file"]), int(m["line"]), m["message"]) for m in errors
    )
    details = tuple(
        f"{m['file']}:{m['line']} {m['level']}: {m['message']}" for m in matches
    )
    return Parsed(_plural(len(errors), "error"), details, findings)


def _import_linter_broken(lines: list[str]) -> tuple[list[str], list[str]]:
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line == _IMPORT_LINTER_BROKEN_TITLE
        ),
        len(lines),
    )
    body = lines[start + 1 :]
    names = [
        line
        for line, following in pairwise(body)
        if _IMPORT_LINTER_RULE.match(following) and not _IMPORT_LINTER_RULE.match(line)
    ]
    details = [line for line in body if not _IMPORT_LINTER_RULE.match(line)]
    return names, details


def parse_import_linter(output: str, return_code: int) -> Parsed:
    lines = _lines(output)
    counts = next(
        (m for line in lines if (m := _IMPORT_LINTER_SUMMARY.match(line))), None
    )
    if return_code == 0:
        return Parsed(f"{counts['kept']} kept" if counts else "contracts kept")
    names, details = _import_linter_broken(lines)
    if not details:
        details = [line for line in lines if not _IMPORT_LINTER_BANNER.match(line)]
    findings = tuple(Finding(None, None, name) for name in names)
    summary = (
        f"{counts['broken']} broken, {counts['kept']} kept" if counts else "failed"
    )
    return Parsed(summary, tuple(details), findings)


def parse_complexipy(output: str, return_code: int) -> Parsed:
    matches = [m for line in _lines(output) if (m := _COMPLEXIPY_LINE.match(line))]
    if return_code == 0:
        return Parsed("none over the limit")
    findings = tuple(
        Finding(m["file"], None, f"{m['function']} complexity {m['score']}")
        for m in matches
    )
    details = tuple(f"{f.file} {f.message}" for f in findings)
    return Parsed(
        f"{len(matches)} over the limit" if matches else "failed", details, findings
    )


def _jscpd_clone(line: str) -> tuple[str, int, str] | None:
    clone = _JSCPD_CLONE.match(line)
    if clone:
        prefix = clone["prefix"] or ""
        first_file = f"{prefix}{clone['first']}"
        first = f"{first_file}:{clone['first_start']}-{clone['first_end']}"
        second_file = f"{prefix}{clone['second']}"
        second = f"{second_file}:{clone['second_start']}-{clone['second_end']}"
        return first_file, int(clone["first_start"]), f"{first} \u2194 {second}"
    same_file = _JSCPD_SAME_FILE_CLONE.match(line)
    if same_file:
        name = same_file["file"]
        first = f"{name}:{same_file['first_start']}-{same_file['first_end']}"
        second = f"{name}:{same_file['second_start']}-{same_file['second_end']}"
        return name, int(same_file["first_start"]), f"{first} \u2194 {second}"
    return None


def parse_jscpd(output: str, return_code: int) -> Parsed:
    lines = [line for line in _lines(output) if not line.startswith(UV_WARNING_PREFIX)]
    clones = [clone for line in lines if (clone := _jscpd_clone(line))]
    if return_code == 0:
        return Parsed("no duplicates")
    if not clones:
        return Parsed("failed", tuple(lines))
    findings = tuple(
        Finding(file, start, f"duplicates {description.split(' \u2194 ')[1]}")
        for file, start, description in clones
    )
    details = tuple(description for _, _, description in clones)
    return Parsed(_plural(len(clones), "duplicated block"), details, findings)


def parse_tsc(output: str, return_code: int) -> Parsed:
    lines = _npm_lines(output)
    matches = [m for line in lines if (m := _TSC_LINE.match(line))]
    if return_code == 0:
        return Parsed("no errors")
    findings = tuple(
        Finding(
            relative_path(f"frontend/{m['file']}"),
            int(m["line"]),
            f"{m['code']} {m['message']}",
        )
        for m in matches
    )
    details = tuple(
        f"frontend/{m['file']}:{m['line']} {m['code']} {m['message']}"
        if (m := _TSC_LINE.match(line))
        else line
        for line in lines
    )
    return Parsed(_plural(len(matches), "error"), details, findings)


def parse_eslint(output: str, return_code: int) -> Parsed:
    matches = [m for line in _npm_lines(output) if (m := _ESLINT_LINE.match(line))]
    if return_code == 0:
        return Parsed("no findings")
    findings = tuple(
        Finding(
            relative_path(m["file"]),
            int(m["line"]),
            f"{m['rule']} {m['message']}",
        )
        for m in matches
    )
    details = tuple(f"{f.file}:{f.line} {f.message}" for f in findings)
    return Parsed(_plural(len(findings), "finding"), details, findings)


def parse_prettier(output: str, return_code: int) -> Parsed:
    messages = [m for line in _npm_lines(output) if (m := _PRETTIER_LINE.match(line))]
    if return_code == 0:
        return Parsed("formatted")
    files = [
        m["message"]
        for m in messages
        if m["level"] == "warn" and not m["message"].startswith("Code style issues")
    ]
    findings = tuple(
        Finding(f"frontend/{file}", None, "would be reformatted") for file in files
    )
    details = tuple(m["message"] for m in messages)
    return Parsed(f"{len(files)} to format" if files else "failed", details, findings)


def _vitest_failure_details(lines: list[str]) -> list[str]:
    start = next(
        (i for i, line in enumerate(lines) if _VITEST_FAILURE_START.match(line)),
        len(lines),
    )
    end = next(
        (i for i, line in enumerate(lines) if _VITEST_SUMMARY_START.match(line)),
        len(lines),
    )
    details = lines[start:end] if start < end else []
    if any(_VITEST_THRESHOLD.search(line) for line in lines):
        table_start = next(
            (i for i, line in enumerate(lines) if line.startswith("File ")),
            len(lines),
        )
        details.extend(lines[table_start - 1 :] if table_start else lines)
    return details


def _vitest_findings(details: list[str]) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    title = "test failed"
    for line in details:
        if _VITEST_FAILURE_START.match(line):
            title = line.strip().removeprefix("FAIL").strip()
        location = _VITEST_LOCATION.match(line)
        if location:
            findings.append(
                Finding(f"frontend/{location['file']}", int(location["line"]), title)
            )
    return tuple(findings)


def parse_vitest(output: str, return_code: int) -> Parsed:
    lines = _npm_lines(output)
    counts = next(
        (m["counts"] for line in lines if (m := _VITEST_TESTS.match(line))),
        "passed" if return_code == 0 else "failed",
    )
    if return_code == 0:
        return Parsed(counts)
    details = _vitest_failure_details(lines)
    return Parsed(counts, tuple(details), _vitest_findings(details))


def playwright(report: str) -> Parser:
    def parse(output: str, return_code: int) -> Parsed:
        lines = _npm_lines(output)
        counts = ", ".join(
            f"{m['count']} {m['kind']}"
            for line in lines
            if (m := _PLAYWRIGHT_RESULT.match(line))
        ) or ("passed" if return_code == 0 else "failed")
        if return_code == 0:
            return Parsed(counts)
        details = [
            line for line in lines if not line.lstrip().startswith("To open last")
        ]
        details.append(f"report: {report}")
        findings = tuple(
            Finding(f"frontend/{m['file']}", int(m["line"]), m["name"])
            for line in lines
            if (m := _PLAYWRIGHT_FAILURE.match(line))
        )
        return Parsed(counts, tuple(details), findings)

    return parse


def parse_vite_build(output: str, return_code: int) -> Parsed:
    names = [m["name"] for line in _npm_lines(output) if (m := _VITE_ASSET.match(line))]
    if return_code == 0:
        return Parsed(", ".join(names) or "built")
    return Parsed("build failed")


RELEASE_FINDING_PREFIXES = ("missing ", "version ", "tag ")


def parse_release_check(output: str, return_code: int) -> Parsed:
    if return_code == 0:
        return Parsed("release complete")
    lines = _lines(output)
    findings = [line for line in lines if line.startswith(RELEASE_FINDING_PREFIXES)]
    if not findings:
        return Parsed("failed", tuple(lines))
    return Parsed(_plural(len(findings), "release finding"), tuple(findings))


def parse_docs_check(output: str, return_code: int) -> Parsed:
    lines = _lines(output)
    if return_code == 0:
        return Parsed("documentation current")
    findings = [
        line.removeprefix("finding ") for line in lines if line.startswith("finding ")
    ]
    if not findings:
        return Parsed("failed", tuple(lines))
    return Parsed(_plural(len(findings), "documentation finding"), tuple(findings))


def parse_freeze_check(output: str, return_code: int) -> Parsed:
    lines = [line for line in _lines(output) if not line.startswith(UV_WARNING_PREFIX)]
    if return_code == 0:
        return Parsed(lines[0] if lines else "surface kept")
    broken = [line for line in lines if ": " in line]
    if any(line.startswith("error ") for line in lines) or not broken:
        return Parsed("failed", tuple(lines))
    return Parsed(_plural(len(broken), "freeze break"), tuple(broken))


def parse_template_check(output: str, return_code: int) -> Parsed:
    lines = [line for line in _lines(output) if not line.startswith(UV_WARNING_PREFIX)]
    if return_code == 0:
        return Parsed("templates current")
    findings = [
        line.removeprefix("finding ") for line in lines if line.startswith("finding ")
    ]
    if not findings:
        return Parsed("failed", tuple(lines))
    return Parsed(_plural(len(findings), "template finding"), tuple(findings))


def parse_hassfest(output: str, return_code: int) -> Parsed:
    if return_code == 0:
        return Parsed("manifest valid")
    integration = ""
    findings: list[Finding] = []
    for line in _lines(output):
        header = _HASSFEST_INTEGRATION.match(line)
        if header:
            integration = header["path"].removeprefix(_WORKSPACE_PREFIX)
        error = _HASSFEST_ERROR.match(line)
        if error:
            findings.append(
                Finding(
                    integration or None,
                    None,
                    f"{error['check']} {error['message']}",
                )
            )
    details = tuple(f"{f.file}: {f.message}" if f.file else f.message for f in findings)
    return Parsed(_plural(len(findings), "hassfest error"), details, tuple(findings))


def plain(success_summary: str) -> Parser:
    def parse(output: str, return_code: int) -> Parsed:
        del output
        return Parsed(success_summary if return_code == 0 else "failed")

    return parse
