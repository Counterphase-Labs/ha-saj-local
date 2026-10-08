# Add Configurable Entity ID Prefix

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-08
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Builds on:** `add-polling-groups-with-per-sensor-cadence.md`. Everything in that plan that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

Every sensor has an entity ID that is fixed by code and by one user setting, never by display text. A user with more than one SAJ system gives each installation its own prefix and gets predictable IDs instead of `_2` suffixes.

Requirements delivered:

| Requirement | Delivered by |
| --- | --- |
| Entity IDs are fixed by code, never derived from display text | Entity IDs built from the sensor key, not from the label or the device name |
| Each system has an optional prefix, empty by default | One optional field on the existing forms |
| Prefixes must be unique across systems, empty counting as a value | Prefix validation at setup and on Configure |
| A prefix can be added, changed or removed later, with a warning first | A confirmation step on Configure |
| Changing a prefix renames the entities and must keep their history | Renaming through the entity registry |
| Sensor names must remain stable | A sensor key becomes part of the entity ID and is treated as fixed |
| Connecting to multiple different modbus systems can happen | Distinct prefixes give distinct, predictable IDs |
| Convention over configuration, without pages of config flow | No new page at setup; one extra step only when a prefix changes |

The first five rows are the Entity IDs section of `../requirements.md`. The Prefix Rules section below adds detail the requirements leave open: allowed characters, length, and the key-shadowing rule.

Included:

- A fixed entity ID format with an optional prefix.
- The prefix field on setup and on Configure.
- Renaming an installation's entities when its prefix is added, changed or removed, after a confirmation step.
- Translations, diagnostics and documentation for the above.

Not changed:

- Sensor unique IDs, which stay config entry ID plus sensor key. Polling groups and device replacement are unaffected.
- The device name and the sensor display names.
- The SAJ library. The prefix is a Home Assistant concern only.
- The browser tier.

## Rules Replaced From Earlier Plans

| Earlier rule | Now |
| --- | --- |
| Entity IDs are whatever Home Assistant derives from the device name and the English sensor label. | Entity IDs follow Entity ID Format below. |
| Setup and Configure keep their five fields. | Both have six: the prefix is added. |

## Behaviour

### Entity ID Format

```text
sensor.saj_<key>             no prefix
sensor.saj_<prefix>_<key>    with a prefix
```

`saj` is fixed. `<key>` is the sensor key from the SAJ library, for example `pv_power`.

This changes four of today's six IDs, because today's IDs come from the English labels:

| Sensor key | Today | After |
| --- | --- | --- |
| `operating_mode` | `sensor.saj_operating_mode` | `sensor.saj_operating_mode` |
| `pv_power` | `sensor.saj_solar_power` | `sensor.saj_pv_power` |
| `battery_power` | `sensor.saj_battery_power` | `sensor.saj_battery_power` |
| `battery_soc` | `sensor.saj_battery_charge` | `sensor.saj_battery_soc` |
| `grid_power` | `sensor.saj_grid_power` | `sensor.saj_grid_power` |
| `load_power` | `sensor.saj_household_load` | `sensor.saj_load_power` |

A sensor key is part of the entity ID from now on. Renaming a key is a breaking change; rewording a label is not.

### Prefix Rules

- The prefix is optional and empty by default.
- It holds lowercase letters and digits only, with no underscores, and is at most 32 characters. Input is trimmed and lowercased before it is checked; anything else is rejected, not silently rewritten.
- Underscores are excluded so that two prefixes can never produce the same ID. With them, prefix `a` with key `b_x` and prefix `a_b` with key `x` would both give `sensor.saj_a_b_x`.
- It is unique across all `saj_local` installations. Empty counts as a value, so only one installation can have no prefix.
- It is rejected when a sensor key of any supported model starts with `<prefix>_`, not only the keys of the installation's current model. Otherwise prefix `battery` on one installation could produce the same ID as key `battery_power` on an unprefixed one.
- It can be added, changed or removed at any time through Configure.
- The rules are applied when a prefix is set or changed. A Configure submission that leaves the prefix unchanged does not re-apply them, so a sensor key added by a later release never blocks an installation from changing its other settings.

### Setting The Prefix At Setup

The setup form gains an optional prefix field. Setup is refused, with the error on the prefix field, when:

- the prefix breaks a rule above, or
- another installation already uses it, including the case where both are empty, or
- any entity ID the installation would create is already taken in Home Assistant. The error names the first taken ID.

Setup does not check the recorder. A new installation that takes the prefix of a deleted one continues that installation's statistics, which is what re-adding the same system needs.

### Changing The Prefix

Configure shows the current prefix. Submitting a different one applies the same three checks and the recorder check below, then shows a confirmation step before anything is saved.

Recorder check: the change is refused when the recorder already holds long-term statistics under any target ID, for example from a deleted installation that used the prefix. Home Assistant will not move statistics onto an ID that already has them, so the rename would leave this installation's history behind and mix its new readings into the old data. The error names the first such ID.

- The check is one metadata lookup against Home Assistant's own database for all target IDs together. It sends nothing to the inverter and does not grow with the amount of recorded data.
- It is skipped when the recorder is not running.
- It covers long-term statistics only. Short-term state history under a target ID is not detectable through a public recorder interface; in that case the old ID's recent state history is not carried over, and statistics still are.

The confirmation states:

- the old and new ID pattern;
- that history and long-term statistics move to the new IDs;
- that automations, scripts, dashboards, templates and Energy settings that use the old IDs will stop working until the user updates them.

On confirm, each of the installation's entities is renamed through the entity registry, then the entry is saved and reloaded. Renaming through the registry is what carries recorder history and statistics across.

- An entity is renamed only when its current ID is exactly the ID the old prefix produces. An entity the user renamed by hand is left alone.
- Disabled entities are renamed too.
- The uniqueness and taken-ID checks are repeated when the confirmation is submitted, because another flow may have finished in between. A failure there aborts and renames nothing.
- A taken target ID is checked before the first rename, so a change is applied completely or not at all.
- A prefix change is confirmed after model and replacement confirmation when one submission needs several.

### Sensors Added By A Later Release

A new sensor is registered at the ID the format gives. If that ID is already taken at that moment, Home Assistant registers it with a numeric suffix and the integration logs one warning naming both IDs.

## Implementation Design

### Integration

- `const.py`: `CONF_PREFIX`, and `sensor_object_id(prefix, key)` as the single place the format is defined.
- `sensor.py`: `SajSensor` sets `entity_id` from `sensor_object_id`. Home Assistant uses it for a new registration and keeps the registry's ID for an existing one.
- `config_flow.py`:
  - `Submission` carries the prefix; it is stored in entry options beside the default interval.
  - Prefix validation is a pure function taking the submitted value, the prefixes of the other installations and the sensor keys.
  - The taken-ID check and the recorder check each take the target IDs and a lookup, so they are tested without a registry or a database.
  - `PendingChange` gains `prefix_confirmed`, and `_async_advance` gains a `confirm_prefix` step in the existing confirmation chain.
  - `_save_changes` renames before `async_update_entry`.
  - The form field uses a suggested value, not a default, so clearing it submits empty.
- `diagnostics.py`: the prefix text never appears. Diagnostics reports the entity ID pattern as `sensor.saj_<key>` or `sensor.saj_[redacted]_<key>`, which shows whether a prefix is set without revealing it.
- `manifest.json`: `recorder` is added to `after_dependencies`.
- `translations/`: field label and help text, three errors, the confirmation step.

### What Is Removed

Nothing. Home Assistant's derived object ID is simply no longer relied on.

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced:

- The format with and without a prefix.
- Each prefix rule: accepted shapes, rejected shapes, trimming and lowercasing, duplicate, duplicate empty, key-shadowing.
- Setup refused on a taken ID, accepted otherwise.
- Configure: unchanged prefix skips confirmation; add, change and remove each reach it; confirm renames, saves and reloads; a hand-renamed entity is skipped; a taken target renames nothing; existing statistics under a target refuse the change; no recorder skips that check.
- Diagnostics shows the redacted pattern with a prefix and the plain pattern without one, and never the prefix text.
- The sensor's entity ID for a prefixed and an unprefixed installation.

Acceptance:

- Two installations with different prefixes produce no `_2` entity ID.
- A second installation cannot be added while it and the first both have no prefix.
- After a prefix change, history recorded under the old ID is shown under the new one.
- `make ci` passes with the coverage gate.

## Work Sequence

1. Format and sensor entity ID.
2. Prefix validation and the setup form.
3. Configure, confirmation and rename.
4. Diagnostics, translations, documentation.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-08 | First draft. |
