# Keep Unchanged Documentation Screenshots

## Plan Metadata

- **Revision:** 2
- **Status:** Approved
- **Last revised:** 2026-11-05
- **Requirements:** `.github/work/requirements.md` (Language, Development environment, Testing, Verification), `mock/docs/requirements.md` (Variation, Control page, Register inspector and traffic log)
- **Code style:** `../code-style.md`
- **Builds on:** [Add User And Developer Documentation](../done/add-user-and-developer-documentation.md), [Add Target Language Translations](../done/add-target-language-translations.md)

## Goal

A second `make docs-images` run with no interface change leaves every screenshot unchanged in git, apart from rare browser noise of a few pixels. A full run of all nine languages finishes well inside the existing time limit of the step. No Playwright run leaves files owned by root in the working tree, also when the run stops early.

## Problem

### Root-owned result folders

The services `playwright-docs` and `playwright` in `compose.playwright.yaml` run as root. Playwright empties and makes again its output folder at the start of a run, so `frontend/test-results/<suite>/` becomes owned by root. Only a `chown` at the end of the container command gives the files back to the user: in `compose.playwright.yaml` for `playwright-docs`, and in `tests/playwright/run-browser-tests.sh` for `playwright`. On 2026-11-04, the runner time limit stopped `make docs-images`. The `chown` did not run, and `tests/playwright/run-docs-images.sh` then could not write `home-assistant.log` into the root-owned folder.

### Run time

`tests/playwright/run-docs-images.sh` runs the nine languages one after the other. On 2026-11-04, each language took about 4 minutes 7 seconds: 229 seconds of Playwright test and about 20 seconds of fresh containers. Nine languages and the first build need about 41 minutes, but the step stops at 30 minutes (`BROWSER_TIMEOUT_SECONDS` in `.github/scripts/check_steps.py`). The run of 2026-11-04 stopped after seven languages. Most of the test time is waits for Home Assistant, while the machine is idle.

### Screenshot churn

Each language has 33 images. On 2026-11-04, two runs of `make docs-images ARGS=en-GB` gave these results for the English images:

- 19 images were the same, byte for byte, in both runs. The PNG output is stable when the picture is the same.
- 2 card images had different readings in each run, because the simulated clock runs from the start of each simulator.
- 10 simulator page images had different timing text in each run: the request rates and counts, the time since the last request, the times and durations in the traffic log, the request chart, the time since each register was last read, and the client port. All of the values come from the wall clock of the simulator and from when Home Assistant polls.
- The repair screenshot had a different relative time ("2 seconds ago", "4 seconds ago"), which the Home Assistant page takes from the browser clock.
- `getting-started-manual-model.png` differed in 2 pixels in one run.

On 2026-11-05, after the work of revision 1, two full runs changed 99 of the 297 images: 80 simulator page images, 4 repair screenshots, 6 `getting-started-manual-model.png` images with 2 to 13 pixels of browser noise, and 8 `optional-equipment-equipment-section.png` images. The equipment image shows the top of the form in some languages and runs, and the opened Equipment section in others, because the spec takes the image directly after the click that opens the section.

## Scope

In scope:

- The user of the two Playwright services in `compose.playwright.yaml`, and the `chown` steps.
- Running the languages of `make docs-images` at the same time: `tests/playwright/run-docs-images.sh`, the image names in `compose.playwright.yaml`, the result and report folders of the docs run, and the `docs-images` step, parser and help text in `.github/scripts/`.
- The state of the two docs simulators at the start of the screenshot spec `frontend/tests/browser/docs/screenshots.spec.ts`.
- The timing text of the simulator page screenshots and of the repair screenshot, and the capture of the equipment screenshot, in the same spec.
- The Screenshots section and the Languages section of `docs/<code>/developer/documentation.md`, in all nine languages.

Out of scope:

- A comparison of new and old screenshots in the spec. Source: User, in the question tool answer "Fixed values, no compare".
- A check that fails on a screenshot difference. No step of `make ci` compares screenshots.
- The time limit of `make docs-images`. Source: User, in the session message "4. no".
- Shorter waits in the spec. The long waits come from the reloads of the integration, which the roadmap item "Faster controls and readings after a reload" covers for users and for the screenshot test.
- Any change to the simulator or to its page. The fixed values exist only in the browser of the screenshot run.
- The browser noise of a few pixels in `getting-started-manual-model.png`.

## Settled Decisions

- **The host user runs the Playwright containers.** The services `playwright-docs` and `playwright` run as the user and group that the `run-*.sh` scripts already export. Reason: no file is then ever owned by root, so a stopped run leaves nothing to repair. Source: User, in the session message "the fucking root isssue is "root" ownership".
- **No `chown` steps.** The `chown` in `compose.playwright.yaml` and in `tests/playwright/run-browser-tests.sh` goes. Reason: a repair step that a stopped run skips is the fault. Source: Agent.
- **A writable home folder in the containers.** Each Playwright service gets a home folder that the host user can write, for the caches of npm and Playwright. Reason: without root, the default home folder of the image is not writable. Source: Agent.
- **Stopped simulators.** Before the spec adds a system to Home Assistant, the spec resets each docs simulator to its scenario and stops its simulated clock at the scenario start time, through the simulator page controls. The clock stays stopped for the whole run. Reason: the same seed and start time give the same readings (`mock/docs/requirements.md`, Variation). Source: User, in the question tool answer "Fixed values, no compare".
- **Wait for the stopped values.** The spec takes the first dashboard screenshot only after Home Assistant shows the solar power that the stopped HS3 simulator reports, and the same for the H2. Reason: a reading polled before the stop would put an old value in the image. Source: Agent.
- **Fixed timing text on the simulator page.** For each simulator page screenshot, the spec takes the real data of the page at that moment and gives the page in the test browser a copy of the data with fixed timing values. Every refresh of the page then gets the same copy, so the page stops changing, and the page draws the copy with its own code. The browser clock of the page is fixed too. Faults, settings, register values, refused registers, and the requests and answers that the fixed traffic log repeats stay real. Source: User, in the session message "simulator: stop the refresh and use fixed text that is suitable for the docs".
- **The fixed values.** Each value suits a home system with the HS3 docs installation, which uses 14 requests of its budget of 40 a minute, as the connection form shows. Source: Agent.
  - The time now, of the simulator and of the browser: the scenario start time.
  - The traffic log is a fixed log of 60 entries made from one poll cycle. The cycle is a fixed list of requests in the spec: the read requests of one full poll of the HS3 docs system, as the poll plan of the integration defines them for the HS3 model with the equipment of the docs scenario and Allow control on, and the read of the polling group for the inverter temperature, in address order, on one connection. Each request takes its real answer from the newest matching entry of the real log. The H2 simulator page gets an empty traffic log with the same fixed counters, because no H2 screenshot shows the traffic log. The cycle repeats until the log holds 60 entries, the connections are numbered from 1, one for each cycle, and the transactions of each connection are numbered from 1. Reason: on 2026-11-05, every cycle taken from the real log by time window or by count held a different set of requests in two runs (for example 33 and 28 requests), because the timing of the polls differs between runs. Source: Agent. Reason: on 2026-11-05, the newest real entries differed between runs in their order, their connections and their error rows, because the phase of the Home Assistant polls at the freeze differs. Source: Agent.
  - The request chart: 14 answered requests and 1 exception in each period, because the refused register is read every 10 seconds. Source: Agent.
  - The overview diagram shows the same state of its moving lines on every run. Source: Agent.
  - The newest traffic log entry: 2 seconds before now, each older entry 1 second before the next. Each request takes 30 ms, answered or not.
  - The last request of each client: 2 seconds ago. Each client connected 10 minutes ago. Each register that was read: last read 20 seconds ago. A register that was never read stays "never".
  - Requests in the last 10 seconds: 2. Requests in the last 60 seconds: 14. Registers in the last 60 seconds: 700. Highest 60-second count: 28.
  - The running totals since the start of the simulator count the entries of the fixed traffic log. Reason: on 2026-11-05, the real totals differed between two runs (115 and 119 requests). Source: Agent.
  - The client address: `192.168.1.20`, port `50000`.
- **Fixed browser clock for the repair screenshot.** The spec fixes the browser clock at 5 seconds after the time that Home Assistant gives for the repair issue, so the issue shows "5 seconds ago". Source: User, in the session message "repair: do". The 5 seconds are an Agent decision: a short, likely time after the refusal.
- **The equipment screenshot shows the whole Equipment section.** The spec waits until the Equipment section is fully open, then scrolls the scroll container of the dialog to its end and waits until the dialog stays at its end, so the image shows every equipment field. Reason: the file name names the section, and a capture directly after the click is a race. Source: User, in the session message "equipment: do".
- **A stable polling group step.** Before the spec reads the language of Home Assistant or clicks the system in the polling group picker, the spec waits until Home Assistant is loaded and the picker is ready. Reason: on 2026-11-05, the polling group step failed in Italian in two full runs, once when it read the language before Home Assistant had loaded, and once when the picker dialog took the click. Source: Agent.
- **Languages at the same time.** `make docs-images` runs the languages at the same time, each language in its own compose project with its own Home Assistant and simulators. Reason: the run is mostly waits, so the languages share the machine with little loss. Source: User, in the session message "ok, let's do parallel (add to plan)".
- **The number of languages at once follows the machine.** The run starts one language for each four processors of the machine, at least one and at most all selected languages, and starts the next language when one ends. Reason: a fixed number overloads a small machine or wastes a large one. Source: Agent.
- **One build for all languages.** The run builds the Home Assistant image and the Playwright runner image one time, before the first language starts, and every language project uses those two images. The script removes the two images when the run ends, also after a failure or an interrupt. Reason: separate compose projects build separate images by default, and a named image is not removed by the cleanup of a single project. Source: Agent.
- **A result folder and a report folder for each language.** The docs run writes `frontend/test-results/docs/<code>/` and `frontend/playwright-report/docs/<code>/`, and the Home Assistant log of a failed language goes into the result folder of that language. Reason: Playwright empties its output folder at the start of a run. Source: Agent.
- **Every language runs to its end.** A failed language does not stop the other languages. The step fails when one or more languages fail, and the failure output names each failed language with its failing steps and its report folder. Source: Agent.
- **One language keeps working.** `ARGS=<code>` still runs one language only. Source: Agent.
- **No pixel gate in CI.** CI does not compare screenshots pixel for pixel. Source: Record (the done plan Add User And Developer Documentation, Boundaries And Decisions).

## Work

1. **Container user.** Both Playwright services run as the host user, with a writable home folder, and the two `chown` steps are gone. Outcome: after a full run and after a run stopped part way, every file in `frontend/test-results/`, `frontend/playwright-report/` and `docs/images/` belongs to the host user.
2. **Stopped simulators.** At the start of the spec, both docs simulators are reset to their scenarios with the simulated clock stopped at the scenario start time, and the spec waits for Home Assistant to show the stopped readings. Outcome: two runs give the same card images.
3. **Languages at the same time.** `make docs-images` builds the two images once, then runs the selected languages at the same time by the number of processors, each in its own compose project, with a result folder and a report folder for each language. The `docs-images` parser reads the report of each language, and the help text of the step says that the languages run at the same time. Outcome: a full run of nine languages on a machine with 36 processors takes less than 10 minutes, a failed language is named with its report folder, and `ARGS=<code>` runs one language.
4. **Fixed timing text and a stable equipment image.** The simulator page screenshots show the fixed values, the repair screenshot shows "5 seconds ago" in the language of the run, and the equipment screenshot shows the opened Equipment section to its end. Outcome: two full runs give the same simulator page, repair and equipment images in every language.
5. **Developer documentation, all nine languages.** The Screenshots section and the Languages section of `docs/<code>/developer/documentation.md` say that the simulated clocks are stopped at the scenario start time for the run, that the simulator page and the repair screenshot show fixed timing values and not the real ones, that the languages run at the same time with a result folder and a report folder for each language, and that the Playwright containers run as the host user. No sentence says that English runs first. Outcome: the nine pages say the same thing, and `make docs-check` passes.

## Errors and failure behaviour

- A Playwright run stops part way: the result folders stay owned by the host user, and `run-*.sh` can write the Home Assistant log.
- A simulator refuses the reset or the clock stop: the run fails with the reason that the simulator gives, and the spec writes no image.
- Home Assistant does not show the stopped readings within the existing two-minute reading wait: the run fails as the reading wait fails today, and the spec writes no image.
- The simulator page does not answer the data request that the fixed copy starts from: the run fails with the failed request, and the spec writes no simulator page image.
- The real traffic log holds no entry for a request of the fixed cycle: the run fails with the function, start address and count of the missing request and of every request that the real log holds, with the number of times each occurs, and the spec writes no simulator page image.
- One language fails: the other languages run to their end and write their images. The step fails and names the failed language, its failing steps and its report folder.
- The image build fails: no language starts, and the step fails with the build error.
- The run stops part way, by the time limit or by an interrupt: the script stops and removes the compose projects of every language.

## Data changes

None. The committed images in git stay the backup of the screenshot set.

## Compatibility

No public interface changes. The containers, the spec and the developer pages are internal to the repository.

## Tests and verification

- Unit tests in `tests/scripts/` for the changed `docs-images` parser: one failed language, two failed languages, and a passed run of several languages. `make ci` passes, with `.github/scripts` at 100 % line and branch coverage. `make ci` runs `test-browser-home-assistant`, which uses the changed `playwright` service.
- Live checks, run by the main session with Docker, at no cost:
  1. Run `make docs-images` for all nine languages two times. Expected: each run passes in less than 10 minutes, each language has its own result folder and report folder, and the second run changes no image except browser noise of a few pixels. Every file in the result folders belongs to the host user.
  2. Stop a full `make docs-images` run part way. Expected: no compose project and no image of the run is left, and no file in `frontend/test-results/`, `frontend/playwright-report/` or `docs/images/` belongs to root.

## Dependencies and risks

- The screenshot run needs Docker. Nine languages at once need about nine Home Assistant containers, eighteen simulators and nine browsers at the same time, and the processor rule keeps a small machine to fewer languages at once.
- The spec writes settings during the run, for example Allow control. A setting that the simulator applies only when its clock moves does not show while the clock is stopped. The spec then fails at the existing read-back wait for the setting.
- A fixed browser clock can stop timers in the Home Assistant page. The repair screenshot is then not drawn, and live check 1 finds the case.
- The fixed cycle lists the requests of the poll plan of the integration. A change of the poll plan makes the run fail until the list is changed to match.
- Rare differences of a few pixels, such as the 2 to 13 pixels in `getting-started-manual-model.png`, come from the browser and can still occur. On 2026-11-05, the smoothing of text and lines also gave scattered single pixels in some simulator page images, up to about 900 pixels in one image.

## Open questions

None.

## Revision History

- **Revision 1 — 2026-11-04:** Initial draft.
- **Revision 2 — 2026-11-05:** Fixed timing text on the simulator page and in the repair screenshot, and a stable equipment screenshot, after two full runs changed 99 of 297 images.
