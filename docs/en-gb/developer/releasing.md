en | [de](../../de/developer/releasing.md) | [nl](../../nl/developer/releasing.md) | [fr](../../fr/developer/releasing.md) | [zh](../../zh-hans/developer/releasing.md) | [es](../../es/developer/releasing.md) | [it](../../it/developer/releasing.md) | [pl](../../pl/developer/releasing.md) | [sv](../../sv/developer/releasing.md)

# Releasing

What to do before a release, how a release is published and how the Home Assistant version is bumped. Pushing a version tag starts the `Release` workflow in `.github/workflows/release.yml`, which checks the tag, runs the checks and creates a draft GitHub release.

## Versions

A release is a GitHub release made from a version tag on `main`. The tag has no `v` prefix and equals the version in `custom_components/saj_local/manifest.json`, `pyproject.toml` and `frontend/package.json`. A stable release is `X.Y.Z` and a beta is `X.Y.ZbN`, published as a GitHub pre-release. The betas before the first stable release are `1.0.0b1`, `1.0.0b2` and so on, the first stable release is `1.0.0`, and Semantic Versioning applies from `1.0.0`. The release notes live in the GitHub release only, and the notes of a beta name every change to an entity, a stored setting, a card type or a card setting since the previous beta. The section [Releases](../../../.github/work/requirements.md#releases) of the project requirements holds the rule.

## Before a release

Do these on `main`, in order.

1. **Run `make ci`.** The [checks page](checks.md) lists what `make ci` runs.
2. **Run `make docs-images`.** The user documentation shows the interface, and CI does not regenerate the images, so each release needs a fresh set. The target needs Docker. Run the target, look at every changed image, commit the changed images in `docs/images/en-gb/` and run `make docs-check`. A run that fails writes no image, so do not release with a failed run. Read [Screenshots](documentation.md#screenshots) for what the run does and why every reading in an image is simulated.
3. **Maintainers only: update the site screenshot.** The project website shows a copy of `docs/images/en-gb/cards-power-flow-card.png`. Update the copy in the same step. No check in this repository catches a stale copy.
4. **Run `make release-check`.** The step makes an archive from `custom_components/saj_local/` and fails when the archive lacks `asset-manifest.json`, the built card bundle or `THIRD_PARTY_LICENSES.md`, the licences of the libraries in the bundle. Run `make build` and commit the bundle and the licence file first when the cards changed.
5. **Set the new version.** Set the version in `custom_components/saj_local/manifest.json`, `pyproject.toml` and `frontend/package.json`. Run `uv lock` so `uv.lock` records the project version, and run `npm install --package-lock-only` in `frontend/` so `frontend/package-lock.json` records the version. Run `make release-check`, commit to `main` and wait for CI to pass.

For `1.0.0`, also remove the pre-release status: the status line in `README.md` and in `docs/<code>/README.md`, and the first sentence about the stable release in `docs/<code>/user/README.md` and `docs/<code>/user/installation.md`, in every language. Write the Beta versions section of `installation.md` again for the betas after `1.0.0`.

The screenshots are the only part of a release that CI cannot check. A change that adds or removes an image fails `make docs-check` through the unused-image and missing-image rules. A change to the interface that leaves an image outdated fails nothing, so step 2 is what keeps the images current.

## Publishing a release

1. Push the tag: `git tag 1.0.0b1`, then `git push origin 1.0.0b1`.
2. Wait for the `Release` workflow. The workflow requires the tagged commit on `main`, runs `make ci` through `ci.yml` and creates a draft release with GitHub's generated notes.
3. Open the draft release and edit the generated notes. For a beta, name every change to an entity, a stored setting, a card type or a card setting since the previous beta.
4. Press Publish.

A failed run makes no draft. Delete the tag with `git push origin :refs/tags/<tag>` and `git tag -d <tag>`, fix `main` and tag again.

HACS offers a published beta to users who turn on "Show beta versions" and a published stable release to every user. A user without the switch gets the tip of `main` until `1.0.0` exists, which is why `main` must pass `make ci` before every push.

## Bumping the Home Assistant version

The Home Assistant version is pinned in several files that must be updated together, otherwise the development container, the browser tests and screenshot run, CI, HACS and the test harness drift apart:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, the development Home Assistant runtime.
2. `Dockerfile.playwright-home-assistant`: the `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` line of the image that `make test-browser-home-assistant` and `make docs-images` use.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` for CI lint and mypy, **and** `pytest-homeassistant-custom-component==<matching release>`. The test harness ships its own pinned `homeassistant`, so the two pins must come from the same Home Assistant release, otherwise lint and tests resolve different cores.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, the minimum Home Assistant core that HACS enforces.
5. `uv.lock`: run `uv lock` after the edit of `pyproject.toml`, so the lock file records the new pins.

Verify the pairing on PyPI before committing: the `requires_dist` of `pytest-homeassistant-custom-component` must list the same `homeassistant==<X.Y.Z>` pinned in `pyproject.toml`.

After a bump, run `make ci` and `make docs-images`, because a new Home Assistant version can change the screens that the images show.
