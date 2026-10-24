# Add Security Policy And Issue Templates

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Roadmap item:** Security policy and bug report diagnostics
- **Last revised:** 2026-10-23
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Order:** Before the roadmap item "Go live", whose checklist names the present roadmap item. Independent of "Release workflow and versioning".

## Outcome And Scope

A user who finds a security problem in SAJ Local knows how to report the problem privately and what happens next. A user who opens an issue picks a form that asks for exactly what a maintainer needs: an integration bug report requires the diagnostics download, a card bug report asks for the browser, the card configuration and a screenshot, and every issue arrives labelled. The repository labels are defined in a file, applied to GitHub by a workflow, and `make ci` fails when an issue template stops requiring the diagnostics download, names a label the file lacks, or lists models that differ from the supported models.

Included:

- `SECURITY.md` at the repository root.
- One new line in `../requirements.md`.
- `.github/labels.yml`, the label set, and `.github/workflows/labels.yml`, the label sync workflow.
- The issue templates in `.github/ISSUE_TEMPLATE/`: `bug.yml` reworked, `feature_request.yml` fixed, `card_bug.yml` and `other.yml` new, `config.yml` unchanged.
- A new `make ci` step, `template-check`, with the script `.github/scripts/template_check.py`, a parser in `.github/scripts/check_parsers.py`, the step in `.github/scripts/check_steps.py`, the `Makefile` target and unit tests in `tests/scripts/`.
- `docs_check.py` checks the links in `SECURITY.md`.
- Documentation: an "Issue labels" section in `CONTRIBUTING.md`, a reload step in `docs/en-gb/user/troubleshooting.md`, links to `SECURITY.md` from `README.md` and `troubleshooting.md`, a row in `docs/en-gb/developer/checks.md`, and two rows in the Sources table of `docs/en-gb/developer/documentation.md`.

Not in the present plan, because the roadmap item "Go live" holds the steps: making the repository public and switching on GitHub private vulnerability reporting. Both steps need a public repository.

No change to integration, card or simulator code, and no change to any `features.md`: the diagnostics download already holds what a bug report needs (`custom_components/saj_local/diagnostics.py`), and Home Assistant adds its own system information and the versions of the installed custom components to every diagnostics download.

## Requirements

- Diagnostics and debug logging in `../../custom_components/saj_local/docs/requirements.md`: "clear and detailed errors with good error handling", "extensive and useful debug dump tools using native HA solutions that are privacy focused" and "option to enable debug logging which will provide clear and helpful debug logs rather than spam that creates log fatigue". The bug report form asks for the outputs of the tools, so the tools reach a maintainer.
- Verification in `../requirements.md`: every check is a make target, `make ci` runs every check, and GitHub runs the same make targets.
- Testing in `../requirements.md`: 100 % unit test coverage from unit tests alone; unit tests are fast and read no project files; no tests of hard-coded values.
- Language in `../requirements.md`: English texts use British spelling. Applies to every new text in the present plan.

## Requirement Changes

One addition to `../requirements.md`, applied with the present plan, as a new section after "Compatibility":

```markdown
## Security

- Users can report a security problem privately, and know how to.
```

The bug report content is documentation, not a requirement (user decision, 2026-10-23).

## Decisions

All chosen by the user on 2026-10-23.

- **Reporting channel.** GitHub private vulnerability reporting, through the form at `https://github.com/Counterphase-Labs/ha-saj-local/security/advisories/new`. The form only works on a public repository, so switching the form on is a checklist step of the roadmap item "Go live".
- **Supported releases.** Only the latest release receives security fixes. The text needs no version scheme, so the roadmap item "Release workflow and versioning" does not change the policy.
- **Scope of the policy.** The whole repository, the simulator in `mock/` included. Out of scope: Modbus TCP having no authentication, Home Assistant itself, HACS and SAJ firmware.
- **Response promise.** Acknowledge within 7 days, fix in a new release, publish a GitHub security advisory after the fix, credit the reporter unless the reporter declines. No fix deadline.
- **Requirement.** One line in `../requirements.md`, worded as the user need only, under "Requirement Changes".
- **Debug logs in bug reports.** The integration page's "Enable debug logging" menu is the documented way. The log field is optional; the diagnostics download is required.
- **Reload step in the user documentation.** `troubleshooting.md` gains the step for a system that failed to set up. The bug report links to the section and adds no instruction of its own.
- **Model and connection.** `bug.yml` has two required dropdowns: the model and the route from SAJ Local to the inverter.
- **Card bugs.** A separate template, `card_bug.yml`.
- **Other issues.** A fourth template, `other.yml`, for the simulator, developer tooling and documentation. Blank issues stay off.
- **Feature request template.** Fixed in the same change as `bug.yml`.
- **Template labels.** `bug.yml` and `card_bug.yml` apply `🛠 goal: fix` and `🚦 status: awaiting triage`; `feature_request.yml` applies `⭐ goal: addition` and `🚦 status: awaiting triage`; `other.yml` applies `🚦 status: awaiting triage`. `bug.yml` adds `🔌 part: integration` and `card_bug.yml` adds `🃏 part: cards`.
- **Label source of truth.** `.github/labels.yml`, applied by `crazy-max/ghaction-github-labeler`. A GitHub label missing from the file is deleted on the next sync. The repository has no issues or pull requests on 2026-10-23, so the first sync removes no label from any issue.
- **Label sync workflow.** A workflow of its own, `.github/workflows/labels.yml`, with `issues: write`; `ci.yml` stays read-only.
- **Label set.** The Creative Commons repository label guide (`https://opensource.creativecommons.org/contributing-code/repo-labels/`), with the priority labels from the user's own list, a new Part category, and the guide's Talk labels. Full set under "Label Set".
- **Label rules.** The Creative Commons rules are adopted and written in `CONTRIBUTING.md`.
- **The template check.** Checks the diagnostics field, every label a template applies or names in a link, and the model dropdown against the model labels in the translations.
- **Roadmap.** The roadmap item "Go live" was created on 2026-10-23 directly before "Beta release", and "Beta release" names "Go live" as a prerequisite. Done outside the present plan.

## Security Policy

New file `SECURITY.md` at the repository root, in British English. GitHub shows a link to the policy in the issue template chooser, so `config.yml` needs no `contact_links` entry.

The policy holds, in order:

1. **Title and introduction:** "Security policy"; one sentence on why security matters (SAJ Local can change inverter and battery settings) and thanks for reporting privately.
2. **Report a problem:** the GitHub "Report a vulnerability" form at `https://github.com/Counterphase-Labs/ha-saj-local/security/advisories/new`; reports are seen only by the maintainers; never a public issue. Ask for what was found, how to reproduce the problem and the possible impact. The diagnostics download helps and is safe to attach, with relative links to the `troubleshooting.md` sections "Download diagnostics" and "What the file and the log leave out" instead of restating the privacy list.
3. **What happens next:** the response promise from "Decisions": acknowledgement within 7 days, the fix in a new release, a GitHub security advisory after the release, and credit unless the reporter declines.
4. **Supported releases:** only the latest release receives security fixes; updating through HACS gets the fix.
5. **Scope:** the whole repository (integration, dashboard cards, Modbus simulator), with these examples of a security problem:
   - a change reaching the inverter while Allow control is off;
   - SAJ Local writing to the inverter without being asked;
   - the host, full serial number, network addresses or other private data in the diagnostics download, the debug log or a repair issue;
   - a card or the card bundle served by Home Assistant running code the card should not run, or mishandling entity state, such as showing another system's data;
   - the simulator's web page or Modbus server letting a client reach files or commands on the computer running the simulator.
6. **Not a security problem in SAJ Local**, each with the advice or owner:
   - Modbus TCP having no authentication: anyone reaching the inverter's Modbus port can read and change the inverter with or without SAJ Local, so keep the inverter on a private network such as a separate VLAN;
   - Home Assistant itself, reported to Home Assistant through `https://www.home-assistant.io/security/`;
   - HACS, reported to the HACS project;
   - the inverter firmware or the SAJ communication module, reported to SAJ.

The scope examples come from the research and both grilling rounds of 2026-10-23. A simulator that answers more freely than a real inverter is not a security problem, so the simulator example concerns the computer running the simulator.

## Label Set

New file `.github/labels.yml`, in the format of `crazy-max/ghaction-github-labeler` (`name`, `color`, `description`). Names are exact, emoji included; `⛔️` carries the variation selector U+FE0F as typed by the user.

| Category | Name | Colour | Description |
| --- | --- | --- | --- |
| Priority | `🔴 priority: critical` | `#cc0008` | Must be fixed ASAP |
| Priority | `🟠 priority: high` | `#f36a30` | Stalls work on the project or its dependents |
| Priority | `🟡 priority: medium` | `#e1db00` | Not blocking but should be fixed soon |
| Priority | `🟢 priority: low` | `#0c8a00` | Low priority and doesn't need to be rushed |
| Status | `🚦 status: awaiting triage` | `#111111` | Has not been triaged & therefore, not ready for work |
| Status | `🚧 status: blocked` | `#484848` | Blocked & therefore, not ready for work |
| Status | `⛔️ status: discarded` | `#eeeeee` | Will not be worked on |
| Status | `🙅 status: discontinued` | `#dfdfdf` | Not suitable for work as component is in maintenance |
| Status | `🏷 status: label work required` | `#484848` | Needs proper labelling before it can be worked on |
| Status | `🏁 status: ready for dev` | `#dfdfdf` | This issue is ready for development |
| Status | `🧹 status: ticket work required` | `#484848` | Needs more details before it can be worked on |
| Goal | `⭐ goal: addition` | `#ffffff` | Addition of a completely new feature |
| Goal | `✨ goal: improvement` | `#ffffff` | Improvement to an already existing feature |
| Goal | `🛠 goal: fix` | `#ffffff` | Fixing something that does not work as intended |
| Goal | `🧹 goal: refactor` | `#ffffff` | Refactoring and/or cleaning up existing systems |
| Aspect | `💻 aspect: code` | `#017cc1` | Concerns the software code in the repository |
| Aspect | `📖 aspect: docs` | `#017cc1` | Concerns the documentation in the repository |
| Aspect | `🤖 aspect: dx` | `#017cc1` | Concerns developers' experience with the codebase |
| Aspect | `🕹 aspect: interface` | `#017cc1` | Concerns end-users' experience with the software |
| Aspect | `📄 aspect: text` | `#017cc1` | Concerns the textual material in the repository |
| Part | `🔌 part: integration` | `#5319e7` | Concerns the Home Assistant integration |
| Part | `🃏 part: cards` | `#5319e7` | Concerns the dashboard cards |
| Part | `🧪 part: simulator` | `#5319e7` | Concerns the Modbus simulator |
| Talk | `❓ talk: question` | `#d876e3` | Can be resolved with an answer |
| Talk | `💬 talk: discussion` | `#d876e3` | Open for discussions and feedback |
| Other | `good first issue` | `#dfbc9d` | New-contributor friendly |
| Other | `help wanted` | `#dfbc9d` | Open to participation from the community |
| Other | `invalid` | `#e4e669` | Inappropriate or invalid, such as spam |

Sources: the priority, status, goal, aspect (except docs) and good first issue / help wanted rows are the user's list of 2026-10-23. `📖 aspect: docs`, the Talk rows and `invalid` follow the Creative Commons guide. The guide gives no colour for the Part and Talk rows; the user approved `#5319e7` for Part and `#d876e3` for Talk on 2026-10-23. `good first issue` and `help wanted` keep the plain names GitHub recognises.

The ten default GitHub labels on the repository on 2026-10-23 (`accessibility`, `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`) are replaced: the first sync deletes the seven not in the file and updates the colour and description of `good first issue`, `help wanted` and `invalid`.

## Label Sync Workflow

New file `.github/workflows/labels.yml`, workflow name `Labels`:

- **Triggers:** pushes to `main` and pull requests, each limited to changes of `.github/labels.yml` or `.github/workflows/labels.yml`.
- **Permissions:** `contents: read` at workflow level; one job `labels` on `ubuntu-latest` with `timeout-minutes: 5` and `contents: read` plus `issues: write`.
- **Steps:** check out the repository with `actions/checkout` pinned to `3d3c42e5aac5ba805825da76410c181273ba90b1` (`# v7.0.1`) and `persist-credentials: false`; then apply the label file with `crazy-max/ghaction-github-labeler` pinned to `548a7c3603594ec17c819e1239f281a3b801ab4d` (`# v6.0.0`), `yaml-file: .github/labels.yml`, and `dry-run` true only when the event is a pull request.

Notes:

- `v6.0.0` is the latest release on 2026-10-23 (published 2026-03-01); the SHA is the commit of the tag. Renovate updates SHA pins with a version comment the same way as in `ci.yml`.
- `skip-delete` stays at its default `false`, so labels missing from the file are deleted.
- On a pull request, the action only reports the changes it would make.

## Issue Templates

Every template is a GitHub issue form in `.github/ISSUE_TEMPLATE/`. Each field that the template check reads carries an `id`, so the check finds the field by `id`, not by its label text. Every duplicate-search link uses `../../issues?q=` with the label percent-encoded, for example `label%3A%22%F0%9F%9B%A0+goal%3A+fix%22` for `🛠 goal: fix`.

`jscpd` (`make copy-paste`, `minLines` 5, `minTokens` 50) scans the YAML templates. Keep blocks shared by `bug.yml` and `card_bug.yml`, such as the checklist, short and worded for each form, so no block of five or more lines repeats.

### `bug.yml`: Bug report

- `name: Bug report`, `description: Something in the SAJ Local integration does not work as it should`.
- `labels: ["🛠 goal: fix", "🚦 status: awaiting triage", "🔌 part: integration"]`.
- Body, in order:
  1. Markdown: search existing bug reports first (duplicate-search link on `🛠 goal: fix`); a problem with a dashboard card has its own form; a security problem goes through `SECURITY.md` (absolute link `https://github.com/Counterphase-Labs/ha-saj-local/blob/main/SECURITY.md`), never an issue.
  2. Dropdown `id: model`, "Model", required. Options: `HS3`, `H2`, `Other`. The template check keeps the options equal to the model labels in the translations plus `Other`.
  3. Dropdown `id: connection`, "How SAJ Local reaches the inverter", required. Options: `The inverter's own network port`, `SAJ communication module (such as the AIO3)`, `RS485 to Modbus TCP gateway`, `Other`. The HS3's own network port answers Modbus TCP (confirmed by the user on 2026-10-23); an H2 behind an AIO3 is described in `.github/work/done/add-full-h2-support.md`.
  4. Textarea `id: description`, "What happened", required.
  5. Textarea `id: reproduction`, "Steps to reproduce", required, with the numbered placeholder of today's template.
  6. Textarea `id: diagnostics`, "Diagnostics download", required. Description: drag the file downloaded from the system's menu, link `https://github.com/Counterphase-Labs/ha-saj-local/blob/main/docs/en-gb/user/troubleshooting.md#download-diagnostics`; when the system never loaded, write "No diagnostics: the system did not load".
  7. Textarea `id: logs`, "Debug log", optional, `render: text`. Description: link to `troubleshooting.md#turn-on-debug-logging`.
  8. Textarea `id: system-health`, "System Health details", required, kept from today's template.
  9. Checkboxes, "Checklist": one issue per report; not a duplicate.
- Removed from today's template: the required checkbox "I have enabled debug logging for my installation", which conflicts with the optional log field, and the logger-integration instruction for logs "from startup of Home Assistant", which conflicts with `troubleshooting.md`.

### `card_bug.yml`: Card bug report

- `name: Card bug report`, `description: A dashboard card, badge or card feature of SAJ Local shows or does something wrong`.
- `labels: ["🛠 goal: fix", "🚦 status: awaiting triage", "🃏 part: cards"]`.
- Body: Markdown with the duplicate-search link on `🃏 part: cards`; input `id: card`, "Card", required; input `id: browser`, "Browser and version", required; textarea `id: configuration`, "Card configuration (YAML)", required, `render: yaml`; textarea `id: screenshot`, "Screenshot", required; textarea `id: description`, required; textarea `id: diagnostics`, "Diagnostics download", optional, linked as in `bug.yml`.

### `feature_request.yml`: Feature request

- Add `labels: ["⭐ goal: addition", "🚦 status: awaiting triage"]`.
- Replace the duplicate-search link label `Feature+Request` with `⭐ goal: addition`, percent-encoded.
- No other change.

### `other.yml`: Something else

- `name: Something else`, `description: The Modbus simulator, developer tooling or the documentation`.
- `labels: ["🚦 status: awaiting triage"]`.
- Body: dropdown `id: part`, "Part", required, options `Modbus simulator`, `Developer tooling`, `Documentation`, `Other`; textarea `id: description`, "Describe the issue", required.

### `config.yml`

Unchanged: `blank_issues_enabled: false`.

## Template Check

New script `.github/scripts/template_check.py`. The script imports `yaml` (PyYAML, pinned in the `test` dependency group, stubs `types-PyYAML` in `lint`), so the step runs the script through `uv run python`, like `freeze-check`, not through `sys.executable`.

Inputs, read from the working directory:

- every `*.yml` in `.github/ISSUE_TEMPLATE/` except `config.yml`;
- `.github/labels.yml`;
- `custom_components/saj_local/translations/en.json`, key `selector.model.options`.

Findings, each printed as `finding <file>: <message>`, exit code 1 when any finding exists, 0 otherwise:

1. `bug.yml` has no body element with `id: diagnostics`, or the element is not a `textarea`, or the element lacks `validations.required: true`.
2. A template's `labels` entry names a label missing from `.github/labels.yml`.
3. A string anywhere in a template (markdown values, descriptions, checkbox labels) holds an `issues?q=` link whose decoded query names a label, as `label:"<name>"` or `label:<name>`, missing from `.github/labels.yml`.
4. The options of the dropdown `id: model` in `bug.yml`, without the last option `Other`, differ from the values of `selector.model.options` in `en.json` without the key `automatic`, in order. On 2026-10-23 the expected options are `HS3`, `H2`, `Other`. The user chose a check against the model profiles (Q14); the translations stand in for the profiles because `_model_selector` in `config_flow.py` offers `automatic` plus the key of every profile in `PROFILES`, and `en.json` holds the label users see for each key, so the script reads the user-facing names without importing the integration.
5. `bug.yml` has no dropdown `id: model`.
6. `.github/labels.yml` names one label twice.

Functions, keyword-only arguments as in the other scripts:

- `template_findings(*, template_name, template, label_names, model_labels) -> list[str]`: findings 1 to 5 for one parsed template; findings 1, 4 and 5 apply only when `template_name` is `bug.yml`.
- `link_labels(*, text) -> list[str]`: the label names in every `issues?q=` link in a string, decoded with `urllib.parse`.
- `duplicate_labels(*, labels) -> list[str]`: finding 6.
- `main() -> int`: reads the inputs, prints the findings, returns the exit code.

Runner wiring:

- `check_parsers.py`: `parse_template_check(output, return_code)`, shaped like `parse_docs_check`: `Parsed("templates current")` on success; on failure one detail line per `finding ` line, with a summary such as "2 template findings"; the raw lines when no finding line exists.
- `check_steps.py`: `_template_check(invocation)` returning one `Command(("uv", "run", "python", str(script)), check_parsers.parse_template_check, timeout=SHORT_TIMEOUT_SECONDS)`, and a `Step("template-check", ...)` after `docs-check` with `Help(summary="issue templates against the label file and the models", runs="a check that bug.yml requires the diagnostics download, that every label a template applies or links exists in .github/labels.yml, and that the model dropdown matches the models in the translations", success="templates current", failure="one line per finding, as file: message", args=NO_ARGS)`. The step joins `CHECK_STEP_NAMES` and so `make ci`.
- `Makefile`: add `template-check` to `.PHONY` and to the forwarded target list.
- `docs/en-gb/developer/checks.md`: a row after `make docs-check`: "`make template-check` | `bug.yml` requires the diagnostics download, every label an issue template applies or links exists in `.github/labels.yml`, and the model dropdown of `bug.yml` matches the models in `translations/en.json`."

Unit tests:

- `tests/scripts/test_template_check.py`: every finding and the clean case through `template_findings`, `link_labels` and `duplicate_labels` with plain dictionaries and strings; `main` against templates, label file and translations written to `tmp_path` (as `test_release_check.py` does), success and failure; the `__main__` entry through `runpy`. No test reads the real templates.
- `tests/scripts/test_check_parsers.py`: `parse_template_check` for success, findings and output without finding lines.
- `tests/scripts/test_check_steps.py`: the command of `template-check`, and the step name in the expected order of the `ci` step list (the list near line 362).

## Documentation Changes

- `../requirements.md`: the Security section under "Requirement Changes".
- `.github/scripts/docs_check.py`: add `Path("SECURITY.md")` to `ROOT_DOCUMENTS`, so `docs-check` checks the relative links of the policy. Update the `docs-check` help text in `check_steps.py` and the link rule in `docs/en-gb/developer/documentation.md`, which name the checked root documents.
- `README.md`, "Help and feedback": add "Report a security problem privately, see the [security policy](SECURITY.md)."
- `docs/en-gb/user/troubleshooting.md`:
  - "Turn on debug logging": after step 2, a step "When the system failed to set up, reload the system from the system's menu, so the log covers the setup." Renumber the later steps.
  - "Help and feedback": name the bug report forms, say the integration form requires the diagnostics download, and add "Report a security problem privately, see the [security policy](../../../SECURITY.md)."
- `CONTRIBUTING.md`: a new section "Issue labels" before "Read more":
  - the labels are defined in `.github/labels.yml` and applied by the workflow `.github/workflows/labels.yml`; a label made by hand on GitHub is deleted on the next sync, so a new label goes into the file;
  - every issue carries one priority, one status, one goal and one aspect label once triaged, plus one part label when the issue concerns the integration, the cards or the simulator; an issue about developer tooling or the documentation as a whole carries no part label; an issue labelled `🚦 status: awaiting triage` may lack the others;
  - a closed issue gets `🏁 status: ready for dev` when resolved or `⛔️ status: discarded` when not;
  - status labels are kept current as the issue changes;
  - the rules come from the Creative Commons repository label guide, linked.
- `docs/en-gb/developer/documentation.md`, Sources table: rows "How to report a security problem | `SECURITY.md`" and "Issue labels and the rules for labels | `.github/labels.yml` and `CONTRIBUTING.md`".
- `docs/en-gb/developer/checks.md`: the `make template-check` row under "Template Check".

## Implementation Order

1. Requirement line in `../requirements.md`.
2. `.github/labels.yml` and `.github/workflows/labels.yml`.
3. `template_check.py` with `tests/scripts/test_template_check.py`; run `make test-python ARGS="tests/scripts/test_template_check.py"`.
4. Parser, step, `Makefile` target and the tests in `test_check_parsers.py` and `test_check_steps.py`; run `make help ARGS=template-check`.
5. The four templates; run `make template-check`, which must pass, then break `bug.yml` by hand once (drop `required` from the diagnostics field) to see the finding, and restore.
6. `SECURITY.md`, the `docs_check.py` change, and the documentation changes; run `make docs-check` and `make copy-paste`.
7. `make ci`.

## Verification And Acceptance

- `make ci` passes, including `template-check`, `docs-check`, `copy-paste` and the 100 % coverage gate of `test-python`.
- `make help` lists `template-check`, and `make help ARGS=template-check` prints the help.
- On a pull request: the `Labels` workflow runs in dry-run mode and lists the planned label changes, and the `CI` workflow passes.
- After the merge to `main`: the `Labels` workflow applies the file, and `gh label list -R Counterphase-Labs/ha-saj-local` shows exactly the 28 labels of "Label Set".
- On GitHub, "New issue" shows the four forms plus the security policy link, each form renders without a form error, and an issue opened from each form carries the planned labels. The duplicate-search link of each form opens a search that filters on an existing label. Close and delete the test issues afterwards.
- `SECURITY.md` renders on GitHub, and every relative link opens the right section. The advisory link answers only once "Go live" switches private vulnerability reporting on; the "Go live" checklist holds the confirmation.

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-23 | Draft created from the research and the user's decisions of 2026-10-23. |
