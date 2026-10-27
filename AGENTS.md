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

.github/work/requirements.md and the three part requirement documents it links to are the authoritative source for project requirements. If a plan would deviate from these requirements to be more robust or better suited at the goals, it must be flagged to the user for approval.

Similarly, anything within `mock/` is not authoritative and must not dictate project requirements or design decisions related to modbus.

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

Run checks through the make targets. Each target runs one tool through the runner in `.github/scripts/`, which prints one `[x]` or `[ ]` line per step, the details of each failed step, and a final result line. The runner runs every selected step even after one fails and exits non-zero when any step fails. A step killed by a signal, a timeout or a missing tool is reported as that, not as a test or lint failure.

Never exclude `.github/work/` (requirements, code style, plans and done work) or `docs/` (the user and developer documentation) from the copy-paste check (the `ignore` list in `.jscpd.json`) or from any other check; duplicated text found there is fixed in the documents or the generator, not hidden. The one exception is a `jscpd:ignore-start` and `jscpd:ignore-end` marker pair around a passage, and only for a case the user has explicitly asked to be written into a plan as an exception and has explicitly approved. Each case is approved on its own: an approval never extends to another case, and an agent never adds a marker pair or writes an exception into a plan without that approval.

`make help` lists every make target with a one-line description and ends with a line naming `make help ARGS=<target>` for the detail of one target. `make help ARGS=<target>` prints the detail for one target: what the target runs, what the target prints on success and on failure, what `ARGS` does for the target, and for a grouping target the steps the target runs. The help lives with the step definitions in `.github/scripts/check_steps.py` and is printed by the runner, so a target added or changed there is described by `make help` without an edit of this file. An unknown target name exits non-zero.

`make ci` is the gate after code changes. `test-python` enforces a **100 % coverage gate** for lines and branches (`--cov-fail-under` and `--cov-branch` in `pyproject.toml`), including `.github/scripts`. GitHub runs `make ci` itself in the one `checks` job of `.github/workflows/ci.yml`, alongside the shared `roquerodrigo/workflows` jobs and the `hacs` job, so local and CI results match and every step of `make ci` runs in GitHub. Skip the checks only when the change literally cannot affect lint or tests (for example README-only edits). `validate` runs hassfest against the working tree and needs only Docker. `tests/scripts/test_runner_processes.py` holds the tests of the runner that start real processes; `test-runner-processes` runs them, and they are kept out of `test-python` and out of coverage. `tests/mock-integration` is run by `mock-smoke` and is kept out of `test-python` and out of coverage too.

### Options

`ARGS`, `ONLY` and `V` are explained in [docs/en-gb/developer/checks.md](docs/en-gb/developer/checks.md#options), and how a subset run measures coverage is under [Coverage of a subset run](docs/en-gb/developer/checks.md#coverage-of-a-subset-run). Agents never use `V=1`, see Agent use below.

### Agent use

Use the make target where one exists. A covered tool may be run directly for anything else; the tool configuration and the agent environment keep the tool as sparse as the make target. Agent shells get the quiet git, docker compose and uv settings from the `env` block of the user-level Claude Code settings (`~/.claude/settings.json`), which applies to every project and is not stored in this repository. The runner sets the docker compose and uv settings for its own steps, so make targets are quiet without the block.

Allowed, because none of the following adds output: filtering, piping or redirecting any output, make targets included (`| grep`, `| tail`, `> file`). Allowed because the agent chose to see more of its own run: selecting tests or stopping early with a test path or node ID, `-k`, `-x`, `--lf` and `-s`. A long target such as `make ci` or a full `make test-python` may be given a longer shell timeout or run in the background.

Forbidden: any way of getting verbose output out of the trimmed output, that is `V=1`, options such as `--cov-report=term`, `-v` or `--reporter=verbose`, environment or configuration overrides, and unsetting the agent environment. `--no-cov` is forbidden too. Run `make complexipy` and never `uv run complexipy` without `--plain`, because complexipy has no setting that removes the banner.

When the trimmed output does not explain a failure clearly enough to fix the failure, stop and ask the user to run the verbose command for the target in the session, for example `! make test-python V=1 ARGS="tests/saj/test_poller.py"`, so the raw output lands in the conversation. After the cause is understood, fix the parser of the target in `.github/scripts/check_parsers.py` so the same kind of failure is explained clearly in the trimmed output from then on, and add a unit test for the case in `tests/scripts/`.

## Efficient reading

- Read the files a task needs instead of exploring; use the repository structure below to find them.
- Do not read the same content twice in one task.
- Never list or search `.venv`, `.venv-isolated` or `node_modules`.
- This never means reading less of something you need: a code review reads the whole diff. The built card bundle (`custom_components/saj_local/frontend/saj-local-*.js`), `uv.lock` and `frontend/package-lock.json` print as one `Binary files differ` line in `git diff` and `git show`; use `git diff --text` only when their content is the subject.

## Bumping the Home Assistant version

The files that pin the Home Assistant version and the steps to bump the version are in [docs/en-gb/developer/releasing.md](docs/en-gb/developer/releasing.md#bumping-the-home-assistant-version).

## Repository Layout

- `custom_components/saj_local/`: the integration; `saj/` is the SAJ library, which can be tested without Home Assistant, `frontend/` holds the built card bundle, `docs/` holds the integration's `features.md` and `requirements.md`, and `AGENTS.md` holds the integration's agent rules.
- `mock/`: the Modbus simulator of a SAJ controller; `docs/` holds the simulator's `features.md` and `requirements.md`, and `AGENTS.md` holds the simulator's agent rules.
- `frontend/`: the card source, its unit tests, the Playwright browser tests, and the Vite, Vitest, Playwright, ESLint and TypeScript configuration; `docs/` holds the cards' `features.md` and `requirements.md`, and `AGENTS.md` holds the cards' agent rules.
- `tests/`: Python tests in exactly six folders: `tests/saj` (unit tests of the SAJ library), `tests/saj-integration` (unit tests of the Home Assistant integration), `tests/mock` (unit tests of the Modbus mock, with `profiles/` and `simulation/`), `tests/mock-integration` (the container smoke script and the shipped-scenario test of the Modbus mock), `tests/playwright` (the Docker scripts for the browser tests) and `tests/scripts` (the unit tests of the check runner, and its real-process tests in `test_runner_processes.py`). `tests/mock-integration` and `tests/scripts/test_runner_processes.py` are outside the unit run and outside coverage.
- `.github/scripts/`: the check runner and its helpers behind the make targets.
- `.github/work/`: global project requirements (`requirements.md`), coding standards (`code-style.md`), `future/` plans and `done/` work.
- `config/`: development Home Assistant configuration; the compose and Dockerfile files define the Docker environments.
- `docs/en-gb/`: the user documentation (`user/`, with the generated entity reference in `user/entities/`) and the developer documentation (`developer/`); `docs/images/en-gb/` holds the screenshots.
- `Makefile`, `pyproject.toml`: entry points and tool configuration.

Keep implementation and tests focused on observable Home Assistant behavior.
Add a module only when the integration has behaviors that needs it.

## Feature Lists

Each part of the repository keeps a feature list, `docs/features.md`, and its own `AGENTS.md` in its own folder:

- the integration: `custom_components/saj_local/docs/features.md` and `custom_components/saj_local/AGENTS.md`;
- the cards: `frontend/docs/features.md` and `frontend/AGENTS.md`;
- the simulator: `mock/docs/features.md` and `mock/AGENTS.md`.

Read a part's `AGENTS.md` before working in the part.

A change that adds, changes or removes a capability of a part updates the part's `features.md` in the same change, and every user page under `docs/en-gb/user/` that links to the changed `features.md` section in the same change too. A change with no observable effect does not.

Every section of a `features.md` has a `Files:` line after its overview, with one or more Markdown links, relative to the `features.md`, to the files that implement the section. Link whole files only. Never link or cite line numbers, line ranges or anchors in these code links, because they go stale as the code changes.

The feature lists record what is built. The requirement documents record the goal. Neither is written from the other.

Each part also keeps a requirement document, `docs/requirements.md`, beside its `features.md`. A `features.md` section with a matching requirement section has a `Requirements:` line after its `Files:` line, linking to the requirement section by its heading anchor. The matching requirement section has a `Features:` line linking back. Matching sections use exactly the same name, so the heading anchors stay valid.

## Completed Work Index

When adding or moving a completed work document into `.github/work/done/`, update `.github/work/done/index.md` in the same change. Add one row with the completion date, the document title linked using a relative path, and a concise one- or two-sentence description. Keep entries in chronological order from oldest to newest and do not add the index itself as a work item.

## Project Documentation

`.github/work/requirements.md` is the primary source of truth for the project. It holds the global requirements, functional and non-functional, that span parts, and links to the requirements of each part: `custom_components/saj_local/docs/requirements.md`, `frontend/docs/requirements.md` and `mock/docs/requirements.md`. A requirement change goes into the part document whose section the change concerns, or into `.github/work/requirements.md` when the change spans parts.

Use `.github/work/done/index.md` as the starting point when researching prior work, implementation decisions, or historical project context. Follow its links to the completed work documents for the authoritative detail.

`.github/work/code-style.md` is the authoritative source for the project's coding standards and style guidelines.

The user documentation is in `docs/en-gb/user/`, the developer documentation in `docs/en-gb/developer/` and the screenshots in `docs/images/en-gb/`. `docs/en-gb/user/entities/` is generated by `make docs` and is never edited by hand. [docs/en-gb/developer/documentation.md](docs/en-gb/developer/documentation.md) describes how the pages are made and checked, and `make docs-check` is part of `make ci`.

The roadmap is the [Roadmap project](https://github.com/orgs/Counterphase-Labs/projects/1) on GitHub (project 1, owner `Counterphase-Labs`), read and changed with `gh project`. This repository's items have the Product `saj-local`. Kind `Roadmap` marks a feature the requirements ask for; Kind `Idea` marks an idea or open question that no requirement backs yet. Status `Backlog` items are open, in the order they are expected to be worked on; `Done` items are delivered and `Dropped` items were withdrawn without being delivered.

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
