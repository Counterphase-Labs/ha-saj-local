from __future__ import annotations

import check_parsers
import pytest
from check_parsers import Finding

PYTEST_FAILURE = """\
.F.                                                                      [100%]
=================================== FAILURES ===================================
__________________________________ test_total __________________________________
tests/test_sample.py:7: in test_total
    assert values == [1, 3]
E   assert [1, 2] == [1, 3]
E
E     At index 1 diff: 2 != 3
__________________________________ test_other __________________________________
tests/helpers.py:21: in check
    raise ValueError("boom")
E   ValueError: boom
================================ tests coverage ================================
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
custom_components/saj_local/a.py     100     40    60%   12-30, 44, 51-60
custom_components/saj_local/b.py     100      5    95%   7, 9-12
-----------------------------------------------------------------
TOTAL                                 200     45    77.5%

FAIL Required test coverage of 90% not reached. Total coverage: 77.50%
=========================== short test summary info ============================
FAILED tests/test_sample.py::test_total - assert [1, 2] == [1, 3]
FAILED tests/test_sample.py::test_other - ValueError: boom
2 failed, 1 passed in 0.31s
"""

PYTEST_PASS = """\
...                                                                      [100%]
================================ tests coverage ================================
TOTAL                                 200     10    95.0%

3 passed in 0.31s
"""


PYTEST_WARNINGS = """\
.....                                                                    [100%]
=============================== warnings summary ===============================
tests/test_a.py::test_one[1]
tests/test_a.py::test_one[2]
  /home/user/repo/tests/helpers.py:4: DeprecationWarning: careful now
    warnings.warn("careful now", DeprecationWarning)

tests/test_b.py::test_two
  custom_components/saj_local/x.py:9: UserWarning: multi
  line message
    warnings.warn("multi\\nline message", UserWarning)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
"""

PYTEST_GAPS = """\
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.7-final-0 ________________

Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
custom_components/saj_local/a.py       100      4    96%   12-14, 44
/home/user/repo/custom_components/saj_local/b.py   50   5   90%   7
-------------------------------------------------------------------
TOTAL                                   150      9    94.0%
"""


def test_pytest_success_reports_counts_and_coverage_only():
    parsed = check_parsers.parse_pytest(PYTEST_PASS, 0)

    assert parsed.summary == "3 passed  95.0% cov"
    assert parsed.details == ()


def test_pytest_passing_run_prints_the_warnings_exactly_as_pytest_shows_them():
    output = PYTEST_WARNINGS + "5 passed, 3 warnings in 0.31s\n"

    parsed = check_parsers.parse_pytest(output, 0)

    assert parsed.summary == "5 passed  3 warnings"
    assert parsed.details == (
        "tests/test_a.py::test_one[1]",
        "tests/test_a.py::test_one[2]",
        "  /home/user/repo/tests/helpers.py:4: DeprecationWarning: careful now",
        '    warnings.warn("careful now", DeprecationWarning)',
        "tests/test_b.py::test_two",
        "  custom_components/saj_local/x.py:9: UserWarning: multi",
        "  line message",
        '    warnings.warn("multi\\nline message", UserWarning)',
    )


def test_pytest_multi_line_warning_message_comes_through_in_full():
    output = (
        "=== warnings summary ===\n"
        "tests/t.py::test_x\n"
        "  a.py:3: RuntimeWarning: first line\n"
        "  second line\n"
        "  third line\n"
        "    source_call()\n"
        "-- Docs: https://docs.pytest.org\n"
        "1 passed, 1 warning in 0.1s\n"
    )

    parsed = check_parsers.parse_pytest(output, 0)

    assert parsed.details == (
        "tests/t.py::test_x",
        "  a.py:3: RuntimeWarning: first line",
        "  second line",
        "  third line",
        "    source_call()",
    )


def test_pytest_passing_run_lists_files_below_full_coverage_with_missing_lines():
    output = PYTEST_GAPS + "\n3 passed in 0.31s\n"

    parsed = check_parsers.parse_pytest(output, 0)

    assert parsed.summary == "3 passed  94.0% cov"
    assert parsed.details == (
        "custom_components/saj_local/a.py  96%  12-14, 44",
        "/home/user/repo/custom_components/saj_local/b.py  90%  7",
    )


def test_pytest_passing_run_with_warnings_and_gaps_lists_warnings_first():
    output = PYTEST_WARNINGS + PYTEST_GAPS + "\n5 passed, 3 warnings in 0.31s\n"

    parsed = check_parsers.parse_pytest(output, 0)

    assert parsed.summary == "5 passed  3 warnings  94.0% cov"
    assert parsed.details[-2:] == (
        "custom_components/saj_local/a.py  96%  12-14, 44",
        "/home/user/repo/custom_components/saj_local/b.py  90%  7",
    )
    assert parsed.details[0] == "tests/test_a.py::test_one[1]"


def test_pytest_failed_gate_keeps_the_requirement_after_the_gap_rows():
    output = (
        PYTEST_GAPS
        + "\nFAIL Required test coverage of 95% not reached. Total coverage: 94.00%\n"
        + "3 passed in 0.31s\n"
    )

    parsed = check_parsers.parse_pytest(output, 1)

    assert parsed.details[0] == "custom_components/saj_local/a.py  96%  12-14, 44"
    assert "Required test coverage of 95% not reached" in parsed.details[-1]


def test_pytest_failure_keeps_tracebacks_and_names_the_failing_lines():
    parsed = check_parsers.parse_pytest(PYTEST_FAILURE, 1)

    assert parsed.summary == "2 failed, 1 passed  77.5% cov"
    assert "E   assert [1, 2] == [1, 3]" in parsed.details
    assert "tests/helpers.py:21: in check" in parsed.details
    assert parsed.findings == (
        Finding("tests/test_sample.py", 7, "test_total: assert [1, 2] == [1, 3]"),
        Finding("tests/helpers.py", 21, "test_other: ValueError: boom"),
    )


def test_pytest_coverage_gate_failure_lists_every_file_below_full_coverage():
    parsed = check_parsers.parse_pytest(PYTEST_FAILURE, 1)

    assert "custom_components/saj_local/a.py  60%  12-30, 44, 51-60" in parsed.details
    assert "custom_components/saj_local/b.py  95%  7, 9-12" in parsed.details
    assert any("Required test coverage of 90%" in line for line in parsed.details)


def test_pytest_coverage_gate_failure_without_a_missing_column_still_lists_the_file():
    output = (
        "custom_components/saj_local/a.py     100     40    60%\n"
        "TOTAL                                 100     40    60%\n"
        "FAIL Required test coverage of 90% not reached. Total coverage: 60.00%\n"
    )

    parsed = check_parsers.parse_pytest(output, 1)

    assert "custom_components/saj_local/a.py  60%" in parsed.details


def test_pytest_raw_result_line_inside_the_decoration_is_understood():
    output = (
        "TOTAL                                 200     10    95.0%\n"
        "=========================== 13 passed in 0.44s ===========================\n"
    )

    assert check_parsers.parse_pytest(output, 0).summary == "13 passed  95.0% cov"


def test_pytest_failure_without_a_result_line_still_reports_failed():
    parsed = check_parsers.parse_pytest("ERROR: file or directory not found: x\n", 4)

    assert parsed.summary == "failed"


def test_ruff_format_lists_every_unformatted_file():
    output = (
        "a.py:1:5: unformatted: File would be reformatted\n"
        "pkg/b.py:3:1: unformatted: File would be reformatted\n"
        "2 files would be reformatted, 10 files already formatted\n"
    )

    parsed = check_parsers.parse_ruff_format(output, 1)

    assert parsed.summary == "2 to format"
    assert [finding.file for finding in parsed.findings] == ["a.py", "pkg/b.py"]
    assert parsed.details[0] == "a.py: would be reformatted"


def test_ruff_format_success_is_one_word():
    parsed = check_parsers.parse_ruff_format("10 files already formatted\n", 0)

    assert parsed.summary == "formatted"


def test_ruff_check_reports_location_code_and_message_per_finding():
    output = (
        "a.py:6:1: E402 Module level import not at top of file\n"
        "pkg/b.py:2:8: F401 [*] `os` imported but unused\n"
        "Found 2 errors.\n"
        "[*] 1 fixable with the `--fix` option.\n"
    )

    parsed = check_parsers.parse_ruff_check(output, 1)

    assert parsed.summary == "2 findings"
    assert parsed.details == (
        "a.py:6 E402 Module level import not at top of file",
        "pkg/b.py:2 F401 [*] `os` imported but unused",
    )
    assert parsed.findings[1] == Finding(
        "pkg/b.py", 2, "F401 [*] `os` imported but unused"
    )


def test_ruff_check_success():
    parsed = check_parsers.parse_ruff_check("All checks passed!\n", 0)

    assert parsed.summary == "no findings"


def test_mypy_reports_errors_and_keeps_notes_as_context():
    output = (
        "a.py:5: error: Incompatible return value type  [return-value]\n"
        "a.py:5: note: expected str\n"
    )

    parsed = check_parsers.parse_mypy(output, 1)

    assert parsed.summary == "1 error"
    assert parsed.details == (
        "a.py:5 error: Incompatible return value type  [return-value]",
        "a.py:5 note: expected str",
    )
    assert parsed.findings == (
        Finding("a.py", 5, "Incompatible return value type  [return-value]"),
    )


def test_mypy_success_has_no_details():
    assert check_parsers.parse_mypy("", 0) == check_parsers.Parsed("no errors")


def test_complexipy_names_each_function_over_the_limit():
    output = "pkg/a.py handle 25\npkg/b.py Thing.method 31\n"

    parsed = check_parsers.parse_complexipy(output, 1)

    assert parsed.summary == "2 over the limit"
    assert parsed.details == (
        "pkg/a.py handle complexity 25",
        "pkg/b.py Thing.method complexity 31",
    )


def test_complexipy_success():
    assert check_parsers.parse_complexipy("", 0).summary == "none over the limit"


def test_jscpd_reports_each_duplicated_block_with_both_locations():
    output = (
        "Using config from .jscpd.json\n"
        "Clones:\n"
        "a.py:1-30 ~ pkg/b.py:5-34\n"
        "---\n"
        "1 clones · 48.3% duplication\n"
    )

    parsed = check_parsers.parse_jscpd(output, 1)

    assert parsed.summary == "1 duplicated block"
    assert parsed.details == ("a.py:1-30 ↔ pkg/b.py:5-34",)
    assert parsed.findings == (Finding("a.py", 1, "duplicates pkg/b.py:5-34"),)


def test_jscpd_clones_with_a_format_suffix_or_inside_one_file_are_located():
    output = (
        "Clones:\na.md:markdown:1-7 ~ b.md:markdown:3-9\nci.yml 87-97 ~ 108-118\n---\n"
    )

    parsed = check_parsers.parse_jscpd(output, 1)

    assert parsed.summary == "2 duplicated blocks"
    assert parsed.details == (
        "a.md:1-7 \u2194 b.md:3-9",
        "ci.yml:87-97 \u2194 ci.yml:108-118",
    )
    assert parsed.findings[1] == Finding("ci.yml", 87, "duplicates ci.yml:108-118")


def test_jscpd_joins_the_shared_folder_prefix_back_onto_both_files():
    output = (
        "Clones:\n"
        ".github/ work/future/add-security-policy-and-issue-templates.md:yaml:141-174"
        " ~ workflows/labels.yml:1-34\n---\n"
    )

    parsed = check_parsers.parse_jscpd(output, 1)

    assert parsed.summary == "1 duplicated block"
    assert parsed.details == (
        (
            ".github/work/future/add-security-policy-and-issue-templates.md:141-174"
            " ↔ .github/workflows/labels.yml:1-34"
        ),
    )
    assert parsed.findings == (
        Finding(
            ".github/work/future/add-security-policy-and-issue-templates.md",
            141,
            "duplicates .github/workflows/labels.yml:1-34",
        ),
    )


def test_jscpd_same_file_clone_drops_the_format_tag():
    parsed = check_parsers.parse_jscpd("Clones:\np.md:yaml 4-37 ~ 40-73\n---\n", 1)

    assert parsed.details == ("p.md:4-37 ↔ p.md:40-73",)
    assert parsed.findings == (Finding("p.md", 4, "duplicates p.md:40-73"),)


def test_jscpd_failure_without_a_clone_hides_the_uv_warning():
    output = (
        "warning: `VIRTUAL_ENV=/x/.venv` does not match the project environment path "
        "`.venv` and will be ignored\n"
        "Error: boom\n"
    )

    parsed = check_parsers.parse_jscpd(output, 1)

    assert parsed.summary == "failed"
    assert parsed.details == ("Error: boom",)


def test_jscpd_success():
    output = "Clones:\n---\n0 clones · 0.0% duplication\n"

    assert check_parsers.parse_jscpd(output, 0).summary == "no duplicates"


def test_tsc_prefixes_frontend_paths_and_keeps_continuation_lines():
    output = (
        "src/a.ts(3,7): error TS2322: "
        "Type 'string' is not assignable to type 'number'.\n"
        "  Types are incompatible.\n"
    )

    parsed = check_parsers.parse_tsc(output, 2)

    assert parsed.summary == "1 error"
    assert parsed.details == (
        "frontend/src/a.ts:3 TS2322 Type 'string' is not assignable to type 'number'.",
        "  Types are incompatible.",
    )
    assert parsed.findings[0].file == "frontend/src/a.ts"
    assert parsed.findings[0].line == 3


def test_tsc_success():
    assert check_parsers.parse_tsc("", 0).summary == "no errors"


def test_eslint_makes_absolute_paths_relative_to_the_repository(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    output = f"{tmp_path}/frontend/src/a.ts:2:5 prefer-const 'x' is never reassigned.\n"

    parsed = check_parsers.parse_eslint(output, 1)

    assert parsed.findings == (
        Finding("frontend/src/a.ts", 2, "prefer-const 'x' is never reassigned."),
    )
    assert parsed.details == (
        "frontend/src/a.ts:2 prefer-const 'x' is never reassigned.",
    )


def test_eslint_keeps_paths_outside_the_repository(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    parsed = check_parsers.parse_eslint("/elsewhere/a.ts:1:1 rule message\n", 1)

    assert parsed.findings[0].file == "/elsewhere/a.ts"


def test_eslint_success():
    assert check_parsers.parse_eslint("", 0).summary == "no findings"


def test_prettier_lists_unformatted_files_with_the_closing_summary_as_context():
    output = (
        "[warn] src/a.ts\n"
        "[warn] src/b.ts\n"
        "[warn] Code style issues found in 2 files. Run Prettier with --write to fix.\n"
    )

    parsed = check_parsers.parse_prettier(output, 1)

    assert parsed.summary == "2 to format"
    assert [finding.file for finding in parsed.findings] == [
        "frontend/src/a.ts",
        "frontend/src/b.ts",
    ]
    assert len(parsed.details) == 3


def test_prettier_success():
    assert check_parsers.parse_prettier("", 0).summary == "formatted"


def test_vitest_success_reports_the_test_count_only():
    output = " Test Files  11 passed (11)\n      Tests  165 passed (165)\n"

    parsed = check_parsers.parse_vitest(output, 0)

    assert parsed.summary == "165 passed"
    assert parsed.details == ()


def test_vitest_failure_keeps_the_failing_test_and_assertion_message():
    output = (
        " RUN  v5.0.0 /repo/frontend\n"
        " FAIL  tests/format.test.ts > formats > pads\n"
        "AssertionError: expected 'a' to be 'b'\n"
        " \u276f tests/format.test.ts:12:20\n"
        " Test Files  1 failed (1)\n"
        "      Tests  1 failed | 164 passed (165)\n"
    )

    parsed = check_parsers.parse_vitest(output, 1)

    assert parsed.summary == "1 failed | 164 passed"
    assert parsed.details == (
        " FAIL  tests/format.test.ts > formats > pads",
        "AssertionError: expected 'a' to be 'b'",
        " \u276f tests/format.test.ts:12:20",
    )
    assert parsed.findings == (
        Finding(
            "frontend/tests/format.test.ts", 12, "tests/format.test.ts > formats > pads"
        ),
    )


def test_vitest_coverage_gate_failure_includes_the_coverage_table():
    output = (
        " Test Files  1 passed (1)\n"
        "      Tests  3 passed (3)\n"
        "-------------|---------|\n"
        "File         | % Stmts |\n"
        "-------------|---------|\n"
        "All files    |   50.00 |\n"
        "ERROR: Coverage for lines (50%) does not meet global threshold (90%)\n"
    )

    parsed = check_parsers.parse_vitest(output, 1)

    assert any(line.startswith("File ") for line in parsed.details)
    assert any("does not meet global threshold" in line for line in parsed.details)


def test_playwright_failure_adds_the_report_path_and_drops_the_open_hint():
    parse = check_parsers.playwright("frontend/playwright-report/controlled")
    output = (
        "·F\n"
        "  1) tests/browser/a.spec.ts:3:5 \u203a opens the panel \u2500\u2500\u2500\n"
        "    Error: expect(locator).toBeVisible() failed\n"
        "  1 failed\n"
        "  1 passed (4.1s)\n"
        "To open last HTML report run:\n"
        "  npx playwright show-report playwright-report/controlled\n"
    )

    parsed = parse(output, 1)

    assert parsed.summary == "1 failed, 1 passed"
    assert "    Error: expect(locator).toBeVisible() failed" in parsed.details
    assert parsed.details[-1] == "report: frontend/playwright-report/controlled"
    assert not any("To open last" in line for line in parsed.details)
    assert parsed.findings == (
        Finding("frontend/tests/browser/a.spec.ts", 3, "opens the panel"),
    )


def test_playwright_success():
    parsed = check_parsers.playwright("report")("  2 passed (1.0s)\n", 0)

    assert parsed.summary == "2 passed"


def test_vite_build_lists_the_built_asset_names():
    output = (
        "vite v8.3.0 building for production...\n"
        "../custom_components/saj_local/frontend/asset-manifest.json  0.17 kB\n"
        "../custom_components/saj_local/frontend/"
        "saj-local-ABC123.js  190.2 kB\n"
    )

    parsed = check_parsers.parse_vite_build(output, 0)

    assert parsed.summary == "asset-manifest.json, saj-local-ABC123.js"


def test_vite_build_failure():
    assert check_parsers.parse_vite_build("boom", 1).summary == "build failed"


def test_release_check_names_every_missing_entry():
    output = "missing saj_local/frontend/a.json\nmissing saj_local/frontend/b.js\n"

    parsed = check_parsers.parse_release_check(output, 1)

    assert parsed.summary == "2 release findings"
    assert len(parsed.details) == 2


def test_release_check_with_one_version_finding_is_singular_and_named():
    output = "version manifest.json: v1 is not X.Y.Z or X.Y.ZbN\n"

    parsed = check_parsers.parse_release_check(output, 1)

    assert parsed.summary == "1 release finding"
    assert parsed.details == ("version manifest.json: v1 is not X.Y.Z or X.Y.ZbN",)


def test_release_check_names_a_tag_finding():
    output = "tag 1.0.1 differs from version 1.0.0\n"

    parsed = check_parsers.parse_release_check(output, 1)

    assert parsed.summary == "1 release finding"


def test_release_check_success():
    assert check_parsers.parse_release_check("", 0).summary == "release complete"


def test_docs_check_names_every_finding_without_the_prefix():
    output = "finding a.md: stale, run make docs\nfinding b.md: missing target c.md\n"

    parsed = check_parsers.parse_docs_check(output, 1)

    assert parsed.summary == "2 documentation findings"
    assert parsed.details == ("a.md: stale, run make docs", "b.md: missing target c.md")


def test_docs_check_with_one_finding_is_singular():
    parsed = check_parsers.parse_docs_check("finding a.md: stale\n", 1)

    assert parsed.summary == "1 documentation finding"


def test_docs_check_reports_an_unexpected_failure_as_failed_with_the_output():
    parsed = check_parsers.parse_docs_check("Traceback\nKeyError: x\n", 1)

    assert parsed.summary == "failed"
    assert parsed.details == ("Traceback", "KeyError: x")


def test_docs_check_success_says_the_documentation_is_current():
    assert check_parsers.parse_docs_check("", 0).summary == "documentation current"


def test_template_check_names_every_finding_without_the_prefix():
    output = "finding bug.yml: a\nwarning: ignored\nfinding other.yml: b\n"

    parsed = check_parsers.parse_template_check(output, 1)

    assert parsed.summary == "2 template findings"
    assert parsed.details == ("bug.yml: a", "other.yml: b")


def test_template_check_with_one_finding_is_singular():
    parsed = check_parsers.parse_template_check("finding bug.yml: a\n", 1)

    assert parsed.summary == "1 template finding"


def test_template_check_reports_an_unexpected_failure_as_failed_with_the_output():
    parsed = check_parsers.parse_template_check("Traceback\nKeyError: x\n", 1)

    assert parsed.summary == "failed"
    assert parsed.details == ("Traceback", "KeyError: x")


def test_template_check_success_says_the_templates_are_current():
    assert check_parsers.parse_template_check("", 0).summary == "templates current"


def test_freeze_check_names_every_break():
    output = "hs3 sensor battery_power: unit W -> kW\nh2 sensor soc: missing\n"

    parsed = check_parsers.parse_freeze_check(output, 1)

    assert parsed.summary == "2 freeze breaks"
    assert parsed.details == (
        "hs3 sensor battery_power: unit W -> kW",
        "h2 sensor soc: missing",
    )


def test_freeze_check_with_one_break_is_singular():
    parsed = check_parsers.parse_freeze_check("h2 sensor soc: missing\n", 1)

    assert parsed.summary == "1 freeze break"


def test_freeze_check_reports_an_unavailable_surface_as_failed_with_the_message():
    parsed = check_parsers.parse_freeze_check("error git archive failed\n", 1)

    assert parsed.summary == "failed"
    assert parsed.details == ("error git archive failed",)


@pytest.mark.parametrize(
    ("output", "summary"),
    [
        ("no stable release tag\n", "no stable release tag"),
        (
            "warning: `VIRTUAL_ENV=/x/.venv` does not match\nno stable release tag\n",
            "no stable release tag",
        ),
        ("", "surface kept"),
    ],
)
def test_freeze_check_success_repeats_the_first_line(output, summary):
    assert check_parsers.parse_freeze_check(output, 0).summary == summary


def test_hassfest_reports_each_error_against_the_integration_directory():
    output = (
        "Validating manifest... done in 0.00s\n"
        "Integration saj_local - /github/workspace/custom_components/saj_local:\n"
        "* [ERROR] [DEPENDENCIES] Using component http but it is not declared\n"
        "* [WARNING] [CONFIG_SCHEMA] something minor\n"
    )

    parsed = check_parsers.parse_hassfest(output, 1)

    assert parsed.summary == "1 hassfest error"
    assert parsed.details == (
        (
            "custom_components/saj_local: "
            "DEPENDENCIES Using component http but it is not declared"
        ),
    )
    assert parsed.findings[0].file == "custom_components/saj_local"


def test_hassfest_error_before_any_integration_header_has_no_file():
    parsed = check_parsers.parse_hassfest("* [ERROR] [JSON] bad\n", 1)

    assert parsed.findings == (Finding(None, None, "JSON bad"),)
    assert parsed.details == ("JSON bad",)


def test_hassfest_success():
    assert check_parsers.parse_hassfest("", 0).summary == "manifest valid"


def test_plain_parser_reports_the_given_summary_on_success_only():
    parse = check_parsers.plain("synced")

    assert parse("anything", 0).summary == "synced"
    assert parse("anything", 1).summary == "failed"


@pytest.mark.parametrize(
    "parse",
    [
        check_parsers.parse_ruff_format,
        check_parsers.parse_ruff_check,
        check_parsers.parse_mypy,
        check_parsers.parse_complexipy,
        check_parsers.parse_jscpd,
        check_parsers.parse_tsc,
        check_parsers.parse_eslint,
        check_parsers.parse_prettier,
        check_parsers.parse_release_check,
        check_parsers.parse_freeze_check,
        check_parsers.parse_docs_check,
        check_parsers.parse_template_check,
        check_parsers.parse_hassfest,
    ],
)
def test_a_failure_the_parser_cannot_read_is_reported_as_failed_not_as_zero_findings(
    parse,
):
    assert parse("an unexpected message\n", 1).summary == "failed"


NPM_BANNER = "\n> saj-local@0.1.0 typecheck\n> tsc --noEmit\n\n"


def test_npm_banner_is_dropped_from_the_lines_a_parser_keeps():
    parsed = check_parsers.parse_tsc(
        f"{NPM_BANNER}src/a.ts(3,1): error TS2304: Cannot find name 'x'.\n"
        "  detail line\n",
        1,
    )

    assert parsed.details == (
        "frontend/src/a.ts:3 TS2304 Cannot find name 'x'.",
        "  detail line",
    )


def test_playwright_failure_details_drop_the_npm_banner_and_keep_npm_errors():
    parse = check_parsers.playwright("report")

    parsed = parse(f"{NPM_BANNER}npm error Lifecycle script failed\n", 1)

    assert parsed.details == ("npm error Lifecycle script failed", "report: report")


def test_strip_npm_banner_keeps_a_quoted_source_line_that_is_not_a_banner():
    lines = ["> assert x", "> 1 + 1", "npm error boom"]

    assert check_parsers.strip_npm_banner(lines) == lines


def test_strip_npm_banner_removes_the_script_line_and_the_command_line_together():
    lines = ["> pkg@1.0.0 lint", "> eslint .", "> not a banner", "npm error boom"]

    assert check_parsers.strip_npm_banner(lines) == ["> not a banner", "npm error boom"]


def test_pytest_failure_section_without_a_source_location_has_no_finding():
    output = (
        "=== FAILURES ===\n"
        "___ test_x ___\n"
        "E   boom\n"
        "FAILED tests/t.py::test_x - boom\n"
        "1 failed in 0.1s\n"
    )

    parsed = check_parsers.parse_pytest(output, 1)

    assert parsed.findings == ()
    assert "FAILED tests/t.py::test_x - boom" in parsed.details


BRANCH_GAPS = """\
================================ tests coverage ================================
Name                          Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------
custom_components/saj_local/a.py     100      4     40      3    94%   12-14, 20->25, 44
/home/user/repo/mock/b.py      50      0     10      1    98%   7->9
-------------------------------------------------------------------------
TOTAL                            150      4     50      4    95.0%
"""


def test_pytest_branch_coverage_rows_keep_the_missing_lines_and_branch_arcs():
    output = BRANCH_GAPS + "\n3 passed in 0.31s\n"

    parsed = check_parsers.parse_pytest(output, 0)

    assert parsed.summary == "3 passed  95.0% cov"
    assert parsed.details == (
        "custom_components/saj_local/a.py  94%  12-14, 20->25, 44",
        "/home/user/repo/mock/b.py  98%  7->9",
    )


def test_pytest_branch_coverage_row_without_a_missing_column_is_still_listed():
    output = (
        "custom_components/saj_local/a.py   100   4   40   3   94%\n"
        "TOTAL                              100   4   40   3   94.0%\n"
    )

    parsed = check_parsers.parse_pytest(output, 1)

    assert parsed.summary == "94.0% cov"
    assert parsed.details == ("custom_components/saj_local/a.py  94%",)


IMPORT_LINTER_BANNER = """\
\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557
 \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d
  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2

---------
Contracts
---------

Analyzed 12 files, 40 dependencies.
-----------------------------------
"""

IMPORT_LINTER_KEPT = (
    IMPORT_LINTER_BANNER
    + """
Library does not import Home Assistant KEPT
Mock is standalone KEPT

Contracts: 2 kept, 0 broken.
"""
)

IMPORT_LINTER_BROKEN = (
    IMPORT_LINTER_BANNER
    + """
Library does not import Home Assistant BROKEN
Mock is standalone BROKEN
Library is layered KEPT

Contracts: 1 kept, 2 broken.


----------------
Broken contracts
----------------

Library does not import Home Assistant
--------------------------------------

saj is not allowed to import homeassistant:

-   saj.device -> homeassistant.core (l.3)


Mock is standalone
------------------

saj_local_mock is not allowed to import custom_components:

-   saj_local_mock.service -> custom_components.saj_local (l.9)
-   saj_local_mock.panel -> custom_components.saj_local.saj (l.2)
"""
)


def test_import_linter_success_reports_the_number_of_kept_contracts():
    parsed = check_parsers.parse_import_linter(IMPORT_LINTER_KEPT, 0)

    assert parsed == check_parsers.Parsed("2 kept")


def test_import_linter_success_without_a_summary_line_still_passes():
    assert check_parsers.parse_import_linter("", 0).summary == "contracts kept"


def test_import_linter_failure_keeps_each_broken_contract_with_its_import_chains():
    parsed = check_parsers.parse_import_linter(IMPORT_LINTER_BROKEN, 1)

    assert parsed.summary == "2 broken, 1 kept"
    assert parsed.details == (
        "Library does not import Home Assistant",
        "saj is not allowed to import homeassistant:",
        "-   saj.device -> homeassistant.core (l.3)",
        "Mock is standalone",
        "saj_local_mock is not allowed to import custom_components:",
        "-   saj_local_mock.service -> custom_components.saj_local (l.9)",
        "-   saj_local_mock.panel -> custom_components.saj_local.saj (l.2)",
    )
    assert parsed.findings == (
        Finding(None, None, "Library does not import Home Assistant"),
        Finding(None, None, "Mock is standalone"),
    )


def test_import_linter_failure_without_broken_contracts_drops_the_banner():
    output = (
        IMPORT_LINTER_BANNER.split("---------", maxsplit=1)[0]
        + "\nCould not find package 'x'.\n"
    )

    parsed = check_parsers.parse_import_linter(output, 1)

    assert parsed.summary == "failed"
    assert parsed.details == ("Could not find package 'x'.",)
    assert parsed.findings == ()


def test_a_module_gate_that_covers_every_module_reports_the_count_only():
    parsed = check_parsers.parse_module_gate("90 of 90 modules covered\n", 0)

    assert parsed == check_parsers.Parsed("90 of 90 modules covered")


def test_a_module_gate_names_each_module_with_a_gap_and_the_gap():
    output = (
        "finding custom_components/saj_local/a.py: 90.0% missing 7, 9->exit\n"
        "finding custom_components/saj_local/b.py: no unit test file\n"
        "88 of 90 modules covered\n"
    )

    parsed = check_parsers.parse_module_gate(output, 1)

    assert parsed.summary == "88 of 90 modules covered"
    assert parsed.details == (
        "custom_components/saj_local/a.py  90.0% missing 7, 9->exit",
        "custom_components/saj_local/b.py  no unit test file",
    )
    assert parsed.findings[1] == Finding(
        "custom_components/saj_local/b.py", None, "no unit test file"
    )


def test_a_module_gate_that_did_not_finish_is_failed_with_the_output():
    parsed = check_parsers.parse_module_gate("Traceback\nValueError: x\n", 1)

    assert parsed == check_parsers.Parsed("failed", ("Traceback", "ValueError: x"))


PYTEST_SLOW = """\
=========================== slowest 0.20 durations ===========================
0.35s call     tests/saj/test_a.py::test_slow[1-x]
0.25s setup    tests/saj/test_a.py::test_fixture
0.21s teardown tests/saj/test_a.py::test_fixture

(3 durations < 0.2s hidden.  Use -vv to show these durations.)
"""


def test_a_test_body_over_the_limit_fails_the_run_with_its_id_and_time():
    parsed = check_parsers.parse_pytest(PYTEST_SLOW + "5 passed in 0.31s\n", 0)

    assert parsed.summary == "5 passed  1 too slow"
    assert parsed.details == (
        "tests/saj/test_a.py::test_slow[1-x] took 0.35s in the test body",
    )
    assert parsed.findings == (
        Finding(
            "tests/saj/test_a.py",
            None,
            "tests/saj/test_a.py::test_slow[1-x] took 0.35s in the test body",
        ),
    )


def test_a_slow_fixture_and_the_hidden_durations_line_print_nothing():
    output = "\n".join(PYTEST_SLOW.splitlines()[:1] + PYTEST_SLOW.splitlines()[2:])

    parsed = check_parsers.parse_pytest(output + "\n5 passed in 0.31s\n", 0)

    assert parsed == check_parsers.Parsed("5 passed")
