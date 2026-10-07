# Agents

**CRITICAL**: DO NOT modify git index or history in any way. This includes rebasing, force-pushing, adding, removing, staging, un-staging or any other git operations that alter the repository history.

## Project Boundary

This repository is a local-only Home Assistant integration. Do not add cloud services or companion SDKs unless explicitly requested.

## Critical Rules

If there are changes outside your working scope, mind your own business. Do not change, revert or otherwise interfere with something that does not concern your current task.

### Backwards Compatibility

So long as this notice is in place, any change of direction or course correction regarding existing functionality MUST NOT CONTAIN BACKWARDS COMPATIBLE CHANGES. Backwards compatibility is explicitly disallowed. The integration has not been released yet.

DO NOT include or reference backwards compatibility in ANY discussion, documentation, requirements, plans or implementations.

Creating backwards compatibility layers of any kind is STRICTLY PROHIBITED.

### Project Requirements Authority

If discussing project requirements, design decisions and similar, what is currently implemented has ZERO authority. Existing code must not direct project requirements or design decisions.

.github/work/requirements.md is the authoritative source for project requirements. If a plan would deviate from these requirements to be more robust or better suited at the goals, it must be flagged to the user for approval.

Similarly, anything within modbus_mock is not authoritative and must not dictate project requirements or design decisions related to modbus.

`modbus_mock` on the other hand, must not be designed around the integration. It must be built firmly around documented SAJ controller behaviour and specifications.

## Feedback

If the user asks for feedback on an implementation, fully understand the requirements and associate plan. Critically evaluate the implementation against the requirements and provide clear, concise, and actionable feedback.

## Requesting Decisions

When asking the user to make a decision, use this format for each problem, in this order and with nothing else:

1. **Problem statement:** State what is wrong in one or two sentences, with the governing requirement and the code reference.
2. **Options:** Use a Markdown table with exactly these columns: `Option`, `Pros`, and `Cons`. Name each option and state what it changes in the `Option` column. Put each pro and each con on its own table row; repeat the option name when an option has more than one pro or con. Give at least two distinct, substantive options, with brief table cells. Keep requirement and code references in the problem statement, outside the table. Include leaving the behaviour alone only when it is viable.
3. **Recommendation:** Name one option and state why it is preferred.

Rules:

- If the requirements and / or plan is clear on direction, do not offer a decision between following the plan or not following the plan. Material problems with the plan should be bought up for discussion explicitly.
- State plainly whether something is broken, working or unknown. Do not make the user infer a verdict from evidence.
- Do not report behaviour that is working as required unless the user asked about it, and then answer in one line.
- Do not include diagnostic evidence, tool output, file dumps or narration of the investigation. Cite the requirement and the code reference that support the conclusion.
- Do not assert that behaviour is intended or "by design" without a requirement that says so. If no requirement covers it, say the requirements are silent and treat that gap as part of the problem.

## Verification workflow

After code changes, run lint and tests in this order:

```bash
make ci
```

- Lint runs `ruff format`, `ruff check` and `mypy` — all configured in `pyproject.toml`. Fix any failure and re-run before moving on.
- `pytest` enforces a **100 % coverage gate** (`--cov-fail-under` in `pyproject.toml`).

Both gates mirror CI (`.github/workflows/ci.yml`). Skip this only when the change literally cannot affect lint or tests (e.g., README-only edits).

## Bumping the Home Assistant version

The Home Assistant version is pinned in three files and **must be updated together**, otherwise the development container, CI, HACS and the test harness drift apart:

1. `compose.yaml` — `ghcr.io/home-assistant/home-assistant:<X.Y.Z>` (development Home Assistant runtime).
2. `pyproject.toml` `[dependency-groups] dev` — `homeassistant==<X.Y.Z>` (CI lint + mypy) **and** `pytest-homeassistant-custom-component==<matching release>` (the test harness ships its own pinned `homeassistant`; the two pins must come from the same HA release, otherwise lint and tests resolve different cores).
3. `hacs.json` — `"homeassistant": "<X.Y.Z>"` (minimum HA core enforced by HACS).

Verify the pairing on PyPI before committing: the `requires_dist` of `pytest-homeassistant-custom-component` must list the same `homeassistant==<X.Y.Z>` you pinned in `pyproject.toml`.

## Repository Layout

- Integration code: `custom_components/saj_local/`
- Tests: `tests/`
- Development configuration: `config/`
- Project requirements: `.github/work/requirements.md`

Keep implementation and tests focused on observable Home Assistant behavior.
Add a module only when the integration has behaviors that needs it.

## Completed Work Index

When adding or moving a completed work document into `.github/work/done/`, update `.github/work/done/index.md` in the same change. Add one row with the completion date, the document title linked using a relative path, and a concise one- or two-sentence description. Keep entries in chronological order from oldest to newest and do not add the index itself as a work item.

## Project Documentation

`.github/work/requirements.md` is the primary source of truth for the project. It includes both requirements and non-functional requirements.

Use `.github/work/done/index.md` as the starting point when researching prior work, implementation decisions, or historical project context. Follow its links to the completed work documents for the authoritative detail.

`.github/work/code-style.md` is the authoritative source for the project's coding standards and style guidelines.

### Implementation Plans

Every new implementation plan must be written to a Markdown file in `.github/work/future/`. Use a specific, descriptive lowercase kebab-case name that identifies the planned work, such as `add-device-discovery.md`; do not use generic names such as `plan.md`. Future plans must not be placed in `.github/work/done/` or another planning directory.

The primary agent communicating with the user is responsible for drafting and updating the plan file. The file must identify its current status and record material revisions. Implementation may start after the user has explicitly approved the current plan. The plan file is the implementation handoff; conversational summaries do not replace it.

No agent may change a plan's status or move a plan between directories. Either action requires the user to explicitly instruct the primary agent to perform that specific action. User approval of a plan or a request to continue work does not, by itself, authorize a status change or move.

## Commit Message Guidelines

When requested, inspect the complete staged diff before writing the commit message. Base the message on the actual staged behaviour, the governing project requirements and the reason for the change, not merely the recent conversation or a list of modified files.

Semantic commit messages are mandatory and must include a title and body.

The title must:

- be a single line no longer than 50 characters;
- identify the primary behavioural change rather than use a broad description such as `update diagnostics` or `fix integration`;
- use the semantic type that best represents the staged change.

The body must:

- explain the problem or incorrect behaviour that motivated the change;
- explain the intended behaviour and why it fits the project design;
- describe important user-visible or architectural consequences, including fallback, health, quality or safety semantics where relevant;
- mention significant secondary changes when they form part of the same staged work, without becoming a file-by-file implementation summary;
- use paragraphs when the commit contains multiple related concerns;
- contain enough specific context that a future maintainer can understand the decision without opening the diff.

Do not produce a generic two-sentence body, repeat the title, claim only that tests were added, or simply enumerate code edits. Before responding, compare the draft message with the full staged diff and ensure no major behavioural change or important rationale has been omitted.
