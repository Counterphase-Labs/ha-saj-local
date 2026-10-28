# Fix jscpd Prefixed Clone Parsing

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-27
- **Requirements:** the Verification workflow and Agent use sections of `AGENTS.md`
- **Code style:** `../code-style.md`
- **Approval record:** The user asked on 2026-10-27 for the plan to be created and implemented.

## Problem

`make copy-paste` reports a failed jscpd run as a bare "failed" with the raw jscpd output when a clone line carries a shared-folder prefix. jscpd 5.2.0 with the `ai` reporter prints, for a clone between two files under a common folder that differs from the folder other clones of the run share, the common folder once followed by a space and then the clone, for example:

```text
.github/ work/future/add-security-policy-and-issue-templates.md:yaml:141-174 ~ workflows/labels.yml:1-34
```

`_JSCPD_CLONE` and `_JSCPD_SAME_FILE_CLONE` in `.github/scripts/check_parsers.py` match neither form, so `parse_jscpd` finds no clone, `_plural(0, …)` returns "failed", and the runner in `.github/scripts/check_runner.py` falls back to the raw output, which carries the uv warning line `warning: \`VIRTUAL_ENV=…\` does not match the project environment path …`.

Same-file clones are printed without a split prefix (`d/e/dup.py 1-589 ~ 590-1178`). Whether a same-file clone inside an embedded block carries a format tag (`p.md:yaml 4-37 ~ 40-73`) is not confirmed.

## Outcome And Acceptance

1. `parse_jscpd` parses a clone line with a shared-folder prefix. The prefix is joined back in front of both file names, so the line above gives the detail `.github/work/future/add-security-policy-and-issue-templates.md:141-174 ↔ .github/workflows/labels.yml:1-34` and the finding `Finding(".github/work/future/add-security-policy-and-issue-templates.md", 141, "duplicates .github/workflows/labels.yml:1-34")`.
2. `parse_jscpd` parses a same-file clone line whose file name carries an optional format tag (`p.md:yaml 4-37 ~ 40-73`), dropping the tag as `_JSCPD_CLONE` already does: detail `p.md:4-37 ↔ p.md:40-73`.
3. `parse_jscpd` ignores lines starting with `UV_WARNING_PREFIX`, as `parse_freeze_check` and `parse_template_check` already do, so a failed run with no parsable clone never shows a uv warning in the fallback details. The runner fallback in `.github/scripts/check_runner.py` is left unchanged; the fallback uses the raw output, so the filtering must make `parse_jscpd` return the remaining lines as details when no clone is parsed and the return code is non-zero, with the summary "failed".
4. Unit tests in `tests/scripts/test_check_parsers.py` cover items 1, 2 and 3, using the exact prefixed line from the Problem section and a `warning: \`VIRTUAL_ENV=/x/.venv\` does not match …` line. The existing jscpd tests keep passing.
5. `make ci` passes with the 100 % line and branch coverage gate.

## Scope

- Changes only `.github/scripts/check_parsers.py` and `tests/scripts/test_check_parsers.py`.
- No change to `.jscpd.json`, the jscpd step in `.github/scripts/check_steps.py`, the runner, the documentation or `.github/work/bugs.md`.
- Language: Python, following the existing regex-and-helper style of `check_parsers.py`.

## Settled Decisions

- The prefix is handled in the regular expressions and `_jscpd_clone`, not by switching jscpd to another reporter.
- The format tag in item 2 is accepted as optional, so the parser works whether or not jscpd prints the tag.
