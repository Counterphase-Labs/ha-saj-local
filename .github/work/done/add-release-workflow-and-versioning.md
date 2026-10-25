# Add Release Workflow And Versioning

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Roadmap item:** Release workflow and versioning
- **Last revised:** 2026-10-24
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Order:** Before the roadmap item "Go live", whose checklist names the present roadmap item, and before "Beta release".

## Outcome And Scope

A maintainer releases SAJ Local by setting one version in three files, committing the change to `main` and pushing a tag equal to the version. GitHub checks that the tagged commit is on `main`, runs `make ci` on the tagged commit and creates a draft GitHub release with GitHub's generated notes. A beta tag such as `1.0.0b1` makes a draft marked as a pre-release. The maintainer edits the notes and publishes the draft. HACS offers a published beta to users who turn on "Show beta versions", and a published stable release to every user.

Included:

- The versioning rule, as requirement lines in `../requirements.md`.
- `.github/workflows/release.yml`, the release workflow, and a `workflow_call` trigger in `.github/workflows/ci.yml`.
- `release-check` also checks the version in `custom_components/saj_local/manifest.json`, `pyproject.toml` and `frontend/package.json`, and the tag at `HEAD`.
- `freeze-check` compares only with the newest stable tag.
- Documentation: `docs/en-gb/developer/releasing.md`, `docs/en-gb/developer/checks.md` and `docs/en-gb/user/installation.md`.

No change to integration, card or simulator code, and no change to any `features.md`, because no part gains, changes or loses a capability.

## Requirements

- Verification in `../requirements.md`: every check is a make target, `make ci` runs every check, and "All testing and verification can run in github workflows using the same make targets". The release workflow runs `make ci` through `ci.yml`.
- Verification in `../requirements.md`: the freeze line ("Once a release exists, `make ci` fails when a change removes an entity key … compared with the newest release tag"). The present plan narrows the comparison to stable tags, see Requirement Changes.
- Purpose and scope in `../requirements.md`: "This HACS repository will be the sole repository". The release installs from the tagged tree through HACS, with no zip asset.
- Testing in `../requirements.md`: 100 % unit test coverage from unit tests alone; unit tests are fast and read no project files.
- Language in `../requirements.md`: English texts use British spelling.

## Requirement Changes

Applied to `../requirements.md` with the present plan.

1. A new section "Releases" after "Security", with three lines:
   - A release is a GitHub release made from a version tag on `main`. The tag and the versions in `manifest.json`, `pyproject.toml` and `frontend/package.json` are equal, and `make ci` runs on the tagged commit before the release is created.
   - Stable versions are `X.Y.Z` and betas are `X.Y.ZbN`, published as GitHub pre-releases. The betas `1.0.0b1`, `1.0.0b2` and so on come before the first stable release `1.0.0`, and Semantic Versioning applies from `1.0.0`.
   - Release notes live in the GitHub release. The notes of a beta name every change to an entity, stored setting, card type or card setting since the previous beta.

2. Under Verification, the freeze line changes "compared with the newest release tag" to "compared with the newest stable release tag". A beta tag never freezes the surface.

## Decisions

All chosen by the user on 2026-10-24.

- **Version numbers.** Betas are `1.0.0bN`, the first stable release is `1.0.0`, and Semantic Versioning applies from `1.0.0`. Home Assistant (hassfest) and HACS both read the beta form through AwesomeVersion, the same form Home Assistant core uses (`2026.10.0b1`).
- **Bare tags.** A tag is the version with no `v` prefix, so the tag and the `manifest.json` version are compared as equal strings.
- **Only stable tags freeze.** The line of `../requirements.md` that forbids backwards-compatibility layers stays until the roadmap item "Leave pre-release status", so a beta finding must still be able to change the surface without a migration.
- **Notes in GitHub only.** No changelog file. The workflow creates a draft with GitHub's generated notes; the maintainer edits the notes and publishes. HACS ignores drafts.
- **HACS fallback to `main` accepted.** The HACS source (`repositories/base.py`, `version_to_download`) downloads the tip of the default branch when a repository has no stable release and the user has not turned on "Show beta versions". `hide_default_branch` in `hacs.json` only hides `main` in the version picker, so the plan leaves `hacs.json` alone. `installation.md` tells beta testers to turn on "Show beta versions", and `make ci` on every push keeps `main` working.
- **One version in three files, checked.** `manifest.json`, `pyproject.toml` and `frontend/package.json` carry the same version, edited by hand. `release-check` fails a mismatch.
- **Tags only from `main`.** The release workflow fails when the tagged commit is not on `main`.
- **Screenshots stay manual.** `make docs-images` needs a person to look at every changed image, and the copy to the `website` repository is outside the reach of the workflow. Both steps stay in the release checklist in `releasing.md`.

## Release Check

`.github/scripts/release_check.py` keeps the archive check and gains a version check. The step runs in `make ci`, so the version check runs on every push and, through `release.yml`, on every tagged commit.

- **Versions.** Read the version of `custom_components/saj_local/manifest.json` (`version`), `pyproject.toml` (`[project] version`, read with `tomllib`) and `frontend/package.json` (`version`).
- **Form.** Each version matches `^[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+)?$`. A version in another form prints `version <file>: <value> is not X.Y.Z or X.Y.ZbN`.
- **Agreement.** When the three versions differ, print `version mismatch: manifest.json <a>, pyproject.toml <b>, frontend/package.json <c>`.
- **Tag.** `git describe --tags --exact-match HEAD` names the tag at `HEAD`, if any. When a tag exists and differs from the `manifest.json` version, print `tag <tag> differs from version <version>`. With no tag at `HEAD` the tag comparison is skipped. The git command is passed in as a function, the way `freeze_check.py` passes `run`, so the unit tests start no process.
- **Result.** The script exits 1 when any `missing` or `version`/`tag` line was printed.
- **Parser.** `parse_release_check` in `.github/scripts/check_parsers.py` reports "release complete" on success, and on failure a summary counting the finding lines ("2 release findings") with each line as detail.
- **Help.** The `release-check` step in `.github/scripts/check_steps.py`: summary "HACS archive and release version", runs "a check of the files the HACS archive holds and of the version in the three version files and the tag at HEAD", success "release complete", failure "each missing archive entry and each version finding".
- **Tests** in `tests/scripts/test_release_check.py`, with files in `tmp_path`: three equal stable versions pass; three equal beta versions pass; one differing file is reported with all three values; a version in another form is reported per file; a tag equal to the version passes; a differing tag is reported; no tag skips the comparison. Parser tests in the existing parser test file for success and for a failure with a version line.

## Freeze Check

`newest_tag` in `.github/scripts/freeze_check.py` runs `git describe --tags --abbrev=0 --match "[0-9]*.[0-9]*.[0-9]*" --exclude "*b*"`, so beta tags and tags that are not versions are skipped. `NO_TAG_MESSAGE` becomes "no stable release tag". The `freeze-check` help in `check_steps.py` says "newest stable release tag" in `runs` and `"no stable release tag"` in `success`, and `parse_freeze_check` matches the new message if the parser names the message. The tests in `tests/scripts/test_freeze_check.py` assert the `--match` and `--exclude` arguments of the git command.

## Release Workflow

`.github/workflows/ci.yml` gains `workflow_call:` under `on:`, with no inputs. Nothing else in `ci.yml` changes.

`.github/workflows/release.yml`, workflow name `Release`, with actions pinned by commit hash the way `ci.yml` pins them:

- **Trigger:** a pushed tag matching `[0-9]*`.
- **Concurrency and permissions:** group `release-<ref>`, never cancelled; `contents: read` at the top level.
- **Job `tag`** (5 minutes): check out with full history and no persisted credentials; fail unless the tagged commit is an ancestor of `origin/main`; output the `--prerelease` flag when the tag contains `b`.
- **Job `checks`:** after `tag`, call `ci.yml`.
- **Job `release`** (5 minutes, `contents: write`): after `tag` and `checks`, create a draft release named after the tag with `gh release create`, verifying the tag, with GitHub's generated notes and the pre-release flag from `tag`.

- The concurrency group `release-<tag>` differs from the `ci-<ref>` group of the called `ci.yml`, so the caller and the called workflow never wait on each other.
- The tag form is checked by `release-check` inside `make ci`, so a tag such as `1.0` fails in the `checks` job and no draft is made.
- A workflow file is a YAML file that `make copy-paste` scans, so `release.yml` calls `ci.yml` and copies no setup step from `ci.yml`.

## Documentation Changes

- `docs/en-gb/developer/releasing.md`:
  - The opening paragraph drops "SAJ Local has no release workflow yet" and names the workflow.
  - A new section "Versions" states the rule of Requirement Changes item 1 in one paragraph and links to the section "Releases" of `../../../.github/work/requirements.md`.
  - "Before a release" keeps steps 1 to 4 and adds step 5: set the new version in `custom_components/saj_local/manifest.json`, `pyproject.toml` and `frontend/package.json`, run `uv lock` so `uv.lock` records the project version, run `npm install --package-lock-only` in `frontend/` so `frontend/package-lock.json` records the version, run `make release-check`, commit to `main` and wait for CI to pass.
  - A new section "Publishing a release": push the tag (`git tag 1.0.0b1` then `git push origin 1.0.0b1`), wait for the `Release` workflow, open the draft release, edit the generated notes (for a beta, name every change to an entity, stored setting, card type or card setting since the previous beta), and press Publish. A failed run makes no draft; delete the tag (`git push origin :refs/tags/<tag>` and `git tag -d <tag>`), fix `main` and tag again.
  - A paragraph on HACS: a user without "Show beta versions" gets the tip of `main` until `1.0.0` exists, which is why `main` must pass `make ci` before every push.
- `docs/en-gb/developer/checks.md`: the `make release-check` row adds the version check; the `make freeze-check` row says "newest stable release tag" and that beta tags are skipped.
- `docs/en-gb/user/installation.md`: a short section "Beta versions" after "Install": until the first stable release, every release of SAJ Local is a beta; in HACS, open SAJ Local, open the menu, choose Redownload, turn on "Show beta versions" and download the newest beta. Without the switch, HACS installs the development version of SAJ Local.

The lines stating that SAJ Local has no published release (`README.md`, `docs/en-gb/user/README.md`, `docs/en-gb/user/installation.md`) stay true until a release is published, so the present plan leaves the lines alone.

## Implementation Order

1. Freeze Check: the `newest_tag` change, the message, the help and the tests.
2. Release Check: the version check, the parser, the help and the tests.
3. The `workflow_call` trigger in `ci.yml` and the new `release.yml`.
4. Requirement Changes in `../requirements.md`.
5. Documentation Changes.
6. `make ci`.

## Verification And Acceptance

- `make ci` passes, including `release-check`, `freeze-check`, `copy-paste`, `docs-check` and the 100 % coverage gate of `test-python`.
- `make help ARGS=release-check` and `make help ARGS=freeze-check` print the new help.
- On the push to `main`, the `CI` workflow passes and the `Release` workflow does not run.
- A test tag on `main` whose name differs from the version (for example `0.1.0b1` while the files say `0.1.0`): the `Release` workflow fails in the `checks` job on `release-check`, and no draft release exists. Delete the test tag afterwards.
- A tag pushed for a commit not on `main` fails in the `tag` job.

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-24 | Draft created from the research and the user's decisions of 2026-10-24. |
