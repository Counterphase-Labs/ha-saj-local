# Rename Integration To SAJ Local

## Plan Metadata

- **Revision:** 3
- **Status:** Approved
- **Last revised:** 2026-10-06
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Approval record:** User authorised this rename plan and its implementation on 2026-10-06, explicitly requesting placement in `done/`, then directed that all instances be updated, including current documentation. User clarified that historical completed plans must not be changed.

## Purpose And Scope

Use integration domain `saj_local` and display name **SAJ Local** to avoid conflicts with other SAJ integrations. The requirements currently prescribe no integration name; record the new domain and display name under Main Integration.

## Implementation

1. Rename `custom_components/saj_modbus/` to `custom_components/saj_local/`; update the manifest, constants, translations, HACS display name and integration imports.
2. Update integration paths and identifiers in Python tooling, Docker mounts and builds, logging configuration, release archive checks, browser tests and current documentation, including the repository layout in `AGENTS.md`.
3. Rename the frontend card element and asset prefix to `saj-local-card`, update its package name and tests, and regenerate its committed build assets under the new integration directory.
4. Audit active repository references and update integration naming and path references wherever needed in code, configuration and current documentation. Preserve historical completed plans, existing GitHub repository URLs, and the standalone mock package and scenario identities. Keep edits confined to the rename. Do not alter the git index or history.

## Verification

Run `make ci` after the rename, fixing any rename-related failures. Confirm that active integration configuration, imports and build paths use `saj_local`, and that the UI presents **SAJ Local**.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-06 | Approved rename plan created at the user's direction. |
| 2 | 2026-10-06 | Expanded the reference audit to completed work documents; this was an incorrect interpretation of the user's request to update all instances. |
| 3 | 2026-10-06 | User clarified that completed plans must remain unchanged; restricted documentation edits to current documentation and directed restoration of historical plans. |
