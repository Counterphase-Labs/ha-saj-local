# Rename Mock And Clone To SAJ Local

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Roadmap item:** Rename everything to saj_local
- **Last revised:** 2026-10-21
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Prior work:** `../done/rename-integration-to-saj-local.md` renamed the integration to `saj_local` and kept the simulator package name; the present plan finishes the rename.

## Outcome And Scope

Every name the project owns follows the integration domain `saj_local`. The word "modbus" no longer appears in any project-owned name: not in a folder, package, compose service, volume, image, container or project name. "Modbus" stays only where text describes the protocol, for example "a SAJ Modbus device" in `../requirements.md` and the protocol error class `ModbusError`.

The simulator's saved state moves from Docker named volumes to bind-mounted, git-ignored folders inside the project, in the same way as the development Home Assistant configuration in `config/`. The compose project name is fixed in `compose.yaml`, so the clone folder name no longer decides where state lives or which containers `make up` and `make down` manage.

| Today | With the present plan |
| --- | --- |
| folder `modbus_mock/` | `mock/` |
| package `saj_modbus_mock`, run as `python -m saj_modbus_mock` | `saj_local_mock`, run as `python -m saj_local_mock` |
| compose services `modbus-mock`, `modbus-mock-h2` | `mock`, `mock-h2` |
| simulator state in named volumes `modbus-mock-state`, `modbus-mock-h2-state` | bind-mounted folders `mock/state/hs3/` and `mock/state/h2/` |
| compose project name taken from the clone folder (the running stack is `home-assistant-saj-modbus`, the folder gives `ha-saj-modbus`) | `name: ha-saj-local` in `compose.yaml` |
| smoke image and project `saj-modbus-mock-smoke-<pid>` | `saj-local-mock-smoke-<pid>` |
| `pyproject.toml` project name `home-assistant-saj-modbus` | `ha-saj-local` |
| `origin` at `Counterphase-Labs/ha-saj-modbus.git` (GitHub redirects) | `Counterphase-Labs/ha-saj-local.git` |
| clone folder `ha-saj-modbus` | `ha-saj-local` |

Not changed:

- Completed plans in `../done/` keep the old names as history, as ruled on 2026-10-06 in `../done/rename-integration-to-saj-local.md` revision 3 and confirmed on 2026-10-21.
- The integration, the SAJ library and the cards. Neither entity IDs nor stored settings change; the integration domain is already `saj_local`.
- The make target names `mock-build` and `mock-smoke` and the test folders `tests/mock` and `tests/mock-integration`, which already use "mock" without "modbus".
- Protocol wording, such as in `../requirements.md`, `README.md` and `AGENTS.md`, the requirements heading "Modbus Mock", and protocol classes such as `ModbusError` and `ExceptionCode`.

## Requirements

- Main Integration in `../requirements.md`: integration domain `saj_local`, display name **SAJ Local**.
- Modbus Mock in `../requirements.md`: changes made on the simulator page "are kept across restarts; the traffic record is not". The bind-mounted state folders keep the simulator state across restarts, as the named volumes do today.
- Non Functional in `../requirements.md`: development in a completely isolated docker environment; all commands exposed as make targets; 100 % unit test coverage from unit tests alone.

## Requirement Changes

None.

## Decisions

- **Package and folder names.** The simulator package is `saj_local_mock` inside the folder `mock/`. The compose services are `mock` and `mock-h2`. Chosen 2026-10-21.
- **State in the project folder.** Simulator state is a bind mount of a project folder, not a Docker named volume, so a folder or project rename never strands the state again. Chosen 2026-10-21.
- **Live state is copied.** The live simulator state is copied into the new folders before the old volumes are removed. Chosen 2026-10-21.
- **Fixed compose project name.** `compose.yaml` sets `name: ha-saj-local`, matching the GitHub repository name, so containers and networks no longer depend on the clone folder name.
- **State folders exist before start.** Docker creates a missing bind-mount source as a root-owned folder, whose files the host user then cannot delete. `mock/state/hs3/.gitkeep`, `mock/state/h2/.gitkeep` and `mock/state/off-grid/.gitkeep` are committed, and `.gitignore` ignores everything else under `mock/state/`.
- **Simulators run as root, like Home Assistant.** No requirement asks for a non-root simulator, and the `homeassistant` service already writes to its bind-mounted `config/` as root. `mock/Dockerfile` drops the system user `mock`, so the simulator runs as root and can write to the bind-mounted state folders whatever their owner. No `user:` and no UID is set anywhere. The host user can still delete or reset the root-owned `state.json` files, because the host user owns the folders.
- **Smoke run keeps away from development state.** `tests/mock-integration/smoke.sh` starts its own compose project from `compose.yaml`. With bind mounts, the smoke run would otherwise write into the development state folders. The state folder root is `${SAJ_MOCK_STATE_DIR:-./mock/state}` in `compose.yaml`; `smoke.sh` points `SAJ_MOCK_STATE_DIR` at a fresh temporary folder with `hs3/` and `h2/` inside, and removes the temporary folder in `smoke_cleanup`.
- **Done plans stay unchanged.** See "Not changed".

## Findings From The Investigation

- The running development stack is the compose project `home-assistant-saj-modbus` (containers `home-assistant-saj-modbus-homeassistant-1`, `home-assistant-saj-modbus-modbus-mock-1`, `home-assistant-saj-modbus-modbus-mock-h2-1`). The live simulator state is `state.json` in the volumes `home-assistant-saj-modbus_modbus-mock-state` (6,447 bytes) and `home-assistant-saj-modbus_modbus-mock-h2-state` (6,292 bytes), owned by UID 999.
- The volumes `ha-saj-modbus_modbus-mock-state` and `ha-saj-modbus_modbus-mock-h2-state` exist and are empty.
- Two containers from a smoke run were left behind and have been running for 2 days: `saj-modbus-mock-smoke-858106-modbus-mock-1` and `saj-modbus-mock-smoke-858106-modbus-mock-h2-1`, with the volumes `saj-modbus-mock-smoke-858106_modbus-mock-state` and `saj-modbus-mock-smoke-858106_modbus-mock-h2-state`. `smoke_cleanup` did not run for process 858106, most likely because the run was killed with a signal `trap` cannot catch.
- The development Home Assistant config entries in `config/.storage/core.config_entries` connect to the hosts `modbus-mock` and `modbus-mock-h2`, which stop resolving once the services are renamed.
- `.github/workflows/ci.yml` needs no change: no workflow step names the simulator.
- The simulator keeps state only when `/data` is a mount point (`StateStore` in `persistence.py` checks `os.path.ismount`). A bind mount is a mount point, so state keeping works unchanged.
- A saved state loads only when the `scenario_hash` stored in `state.json` matches `sha256(repr(scenario))` of the running scenario. The scenario files are not edited, and the dataclass and enum `repr` carries no module name, so the package rename keeps the hash. Step 6.3 confirms the copied state loads; if the hash differs, the simulator logs "the scenario changed since the state was saved", and the agent stops and reports to the user before removing the old volumes.

## Implementation

### 1. Package and folder

1. `git mv modbus_mock mock`, then `git mv mock/saj_modbus_mock mock/saj_local_mock`.
2. Replace `saj_modbus_mock` with `saj_local_mock` in every import in `mock/saj_local_mock/` and `tests/mock/` (48 files), in `tests/mock-integration/test_scenario_files.py`, and in `tests/mock/test_main.py` (the `sys.argv`, `sys.modules` and `runpy.run_module` names).
3. `mock/Dockerfile`: `COPY saj_local_mock ./saj_local_mock`; `python -m saj_local_mock` in `HEALTHCHECK` and `CMD`; the `useradd` of `mock`, the `mkdir /data && chown mock /data` and `USER mock` are removed (see the decision "Simulators run as root, like Home Assistant").
4. `pyproject.toml`: project name `ha-saj-local`; `--cov=mock/saj_local_mock`; the source and path entries `mock/saj_local_mock`; `known-first-party = ["saj", "saj_local_mock"]`; import-linter `root_packages` and `source_modules` with `saj_local_mock`. Regenerate `uv.lock` with `uv lock`.
5. `mock/saj_local_mock/persistence.py`: the warning "no volume is mounted at %s, so changes will not be kept" becomes "nothing is mounted at %s, so changes will not be kept", because the state is now a bind-mounted folder; the expected message in `tests/mock/test_persistence.py` changes with it. The module docstring and the `StateStore` docstring say "Without a mounted folder" in place of "Without a volume".

### 2. Check runner

1. `.github/scripts/pytest_scope.py`: `MOCK_DIRECTORY = Path("mock/saj_local_mock")`. `.github/scripts/pytest_scope.json`: the two `modbus_mock/saj_modbus_mock/...` paths.
2. `.github/scripts/check_steps.py`: `IMPORT_LINT_ENVIRONMENT = {"PYTHONPATH": ".:mock"}`, `MOCK_SERVICE = "mock"`.
3. `tests/scripts/test_pytest_scope.py`, `tests/scripts/test_check_steps.py` and the import-linter sample output in `tests/scripts/test_check_parsers.py`: the new package, folder and service names.

### 3. Compose, state and smoke

1. `compose.yaml`: `name: ha-saj-local` at the top; services `mock` and `mock-h2` with build context `./mock`, scenario mounts `./mock/scenarios/...`, and state mounts `${SAJ_MOCK_STATE_DIR:-./mock/state}/hs3:/data` and `${SAJ_MOCK_STATE_DIR:-./mock/state}/h2:/data`; the `volumes:` section with the two named volumes is removed.
2. `compose.playwright.yaml`: anchor `x-mock: &mock`, services `mock` and `mock-h2`, build context `./mock`, scenario mounts and `depends_on` with the new names. The Playwright simulators keep no state, as today.
3. `compose.override.yaml.example`: service `mock`, scenario path `./mock/scenarios/hs3-ev.yaml`.
4. `tests/mock-integration/smoke.sh`: `saj-local-mock-smoke-$$` for image and project, `python -m saj_local_mock healthcheck`, the temporary `SAJ_MOCK_STATE_DIR` with its removal in `smoke_cleanup`, and the new service names. The `mktemp -d` and `mkdir` of the temporary state folder come directly after `trap smoke_cleanup EXIT HUP INT TERM`, so a signal between the two never leaks the temporary folder. After the healthcheck and panel checks of the compose services, `smoke.sh` makes one harmless change on each service's panel (posting the current link settings back to `/api/link`) and fails unless `$smoke_state_directory/hs3/state.json` and `$smoke_state_directory/h2/state.json` appear within 5 seconds. The check covers the requirement that simulator changes are kept across restarts, and fails while the image runs the simulator as a non-root user.
5. `tests/playwright/run-home-assistant.sh`: `up --detach --wait homeassistant mock mock-h2`. `frontend/tests/browser/home-assistant/configuration.spec.ts`: hosts `mock` and `mock-h2` in `addIntegration`.
6. `.gitignore`: `mock/state/*/*` and `!mock/state/*/.gitkeep`. Commit `mock/state/hs3/.gitkeep`, `mock/state/h2/.gitkeep` and `mock/state/off-grid/.gitkeep`.
7. `mock/.dockerignore`: add `state/`, so the live `state.json` files are never sent in the image build context or copied into an image.

### 4. Documentation

1. `AGENTS.md`: repository layout `mock/`, and the test folder table rows `tests/mock` → `mock/saj_local_mock`, `tests/mock/profiles` → `mock/saj_local_mock/profiles`, `tests/mock/simulation` → `mock/saj_local_mock/simulation`.
2. `documentation/development.md`: every path, service name and command (22 references), for example `docker compose exec mock python -m saj_local_mock healthcheck`, plus a short note saying simulator state lives in `mock/state/` and is reset by deleting the folder contents. The off-grid example `docker compose run --rm --no-deps -p 5030:502 -v ./mock/scenarios/hs3-off-grid.yaml:/config/config.yaml:ro mock` gains the bind mount `-v ./mock/state/off-grid:/data`, with one sentence saying why: the `mock` service otherwise brings its `/data` mount of `mock/state/hs3/`, and the first change in the off-grid run would replace the development HS3 `state.json` with off-grid state. The off-grid run keeps its own state in `mock/state/off-grid/` across runs. A `-v` given to `docker compose run` for `/data` replaces the service's `/data` mount (checked 2026-10-21).
3. `README.md` and `CONTRIBUTING.md`: no old name found; checked again after the rename.

### 5. Verification in the working tree

1. `git grep -i -E "modbus[-_]mock|saj[-_]modbus|ha-saj-modbus" -- . ':!.github/work/done' ':!.github/work/future/rename-mock-and-clone-to-saj-local.md'` finds nothing, and `git grep -i modbus` outside `.github/work/done` finds only protocol wording.
2. `make ci` passes, including `mock-build`, `mock-smoke` and both Playwright suites.

### 6. Move the live development stack (after `make ci` passes)

The agent carries out each command and checks the result before the next one.

1. Stop the old development stack: `docker compose --project-name home-assistant-saj-modbus down` (containers only; volumes stay for the copy).
2. Copy the live state into the new folders before any new simulator starts, because a starting simulator writes a fresh `state.json`. The copy uses the new simulator image, so no other image is pulled, and writes through the service's `/data` mount:
   `docker compose run --rm --no-deps -v home-assistant-saj-modbus_modbus-mock-state:/from:ro --entrypoint cp mock /from/state.json /data/state.json`, and the same with `home-assistant-saj-modbus_modbus-mock-h2-state` and the service `mock-h2`. Both files are then in `mock/state/hs3/` and `mock/state/h2/`.
3. Start the new stack with `make up`, and confirm on both simulator pages (ports 5080 and 5081) that the copied state was loaded: the settings and faults match the old pages.
4. Point the two development Home Assistant config entries at the new hosts through the integration's reconfigure flow: `modbus-mock` → `mock`, `modbus-mock-h2` → `mock-h2`. Confirm both systems read values again.
5. Remove the leftovers: the volumes `home-assistant-saj-modbus_modbus-mock-state`, `home-assistant-saj-modbus_modbus-mock-h2-state`, `ha-saj-modbus_modbus-mock-state` and `ha-saj-modbus_modbus-mock-h2-state`; the containers `saj-modbus-mock-smoke-858106-modbus-mock-1` and `saj-modbus-mock-smoke-858106-modbus-mock-h2-1` with their two volumes; and the dangling images of the old compose projects.
6. `git remote set-url origin git@github.com:Counterphase-Labs/ha-saj-local.git`, then `git fetch` to confirm.

### 7. Clone folder (by the user, last)

The agent session runs inside the clone folder, so the user renames the clone folder after the work is committed and the agent session has ended:

1. `make down`.
2. `mv ha-saj-modbus ha-saj-local`.
3. `make up` from the new folder. Because `compose.yaml` fixes the project name and the state is in `mock/state/`, the stack and the simulator state carry over unchanged.

Claude Code keeps per-project settings and memory by folder path, so the new path starts with fresh project settings. The memory folder for the old path is empty today, so no memory is lost.

## Verification

- `make ci` passes.
- The `git grep` checks in step 5.1 come back clean.
- After step 6, `docker ps -a` and `docker volume ls` list no name containing `modbus-mock`, `saj-modbus` or `ha-saj-modbus`, and both simulator pages show the copied state.
- After step 7, `make up` from `ha-saj-local` starts the containers `ha-saj-local-homeassistant-1`, `ha-saj-local-mock-1` and `ha-saj-local-mock-h2-1`, and both simulators show the state in `mock/state/`.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-21 | Draft created from the roadmap item and the investigation of 2026-10-21. |
