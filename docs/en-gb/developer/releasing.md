# Releasing

What to do before a release and how the Home Assistant version is bumped. SAJ Local has no release workflow yet, so the page holds only the steps that exist.

## Before a release

Do these on `main`, in order.

1. **Run `make ci`.** The [checks page](checks.md) lists what `make ci` runs.
2. **Run `make docs-images`.** The user documentation shows the interface, and CI does not regenerate the images, so each release needs a fresh set. The target needs Docker. Run the target, look at every changed image, commit the changed images in `docs/images/en-gb/` and run `make docs-check`. A run that fails writes no image, so do not release with a failed run. Read [Screenshots](documentation.md#screenshots) for what the run does and why every reading in an image is simulated.
3. **Copy the site screenshot in the same step.** Copy `docs/images/en-gb/cards-power-flow-card.png` to `assets/images/saj-local-power-flow.png` in the `website` repository and commit the copy there, because the SAJ Local page on `counterphase.dev` shows a copy of the image. No check catches a stale copy, because CI in this repository cannot see the website repository.
4. **Run `make release-check`.** The step makes an archive from `custom_components/saj_local/` and fails when the archive lacks `asset-manifest.json` or the built card bundle. Run `make build` and commit the bundle first when the cards changed.

The screenshots are the only part of a release that CI cannot check. A change that adds or removes an image fails `make docs-check` through the unused-image and missing-image rules. A change to the interface that leaves an image outdated fails nothing, so step 2 is what keeps the images current.

## Bumping the Home Assistant version

The Home Assistant version is pinned in several files that must be updated together, otherwise the development container, the browser tests and screenshot run, CI, HACS and the test harness drift apart:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, the development Home Assistant runtime.
2. `Dockerfile.playwright-home-assistant`: the `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` line of the image that `make test-browser-home-assistant` and `make docs-images` use.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` for CI lint and mypy, **and** `pytest-homeassistant-custom-component==<matching release>`. The test harness ships its own pinned `homeassistant`, so the two pins must come from the same Home Assistant release, otherwise lint and tests resolve different cores.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, the minimum Home Assistant core that HACS enforces.
5. `uv.lock`: run `uv lock` after the edit of `pyproject.toml`, so the lock file records the new pins.

Verify the pairing on PyPI before committing: the `requires_dist` of `pytest-homeassistant-custom-component` must list the same `homeassistant==<X.Y.Z>` pinned in `pyproject.toml`.

After a bump, run `make ci` and `make docs-images`, because a new Home Assistant version can change the screens that the images show.
