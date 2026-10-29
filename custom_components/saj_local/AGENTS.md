# Integration Guidance

This folder is the SAJ Local Home Assistant integration, with the SAJ library in `saj/`. The root `AGENTS.md` also applies.

## Feature List

`docs/features.md` lists what the integration does today. Home Assistant users and developers read it to learn what SAJ Local offers, so write it for them.

- Split the file into sections. Each section has a heading, an overview of one to three sentences, a `Files:` line linking the files that implement the section, and a bullet list of implemented features.
- Write one bullet per capability a user or developer would recognise, such as a reading, a control, a setup step or a repair issue. Leave out the detail of a single logic path.
- Describe only what the code does now. Anything that is only required, planned or partly built is not listed.
- Use plain words and the terms the integration's translations show to users, such as Allow control, Meter A and power control. Bullets do not name modules, classes, functions or files, and do not give dates, plan names or roadmap claims.
- Where the HS3 and the H2 differ, the bullet says which model has what.
- State a limitation inside its bullet when a user would trip over it.
- The SAJ library belongs in this list, because users see what the library does only through the integration.
- The cards have their own list in `frontend/docs/features.md`. The integration's list only says that the integration serves the card bundle and links there.

## Requirements

`docs/requirements.md` holds the integration's functional and non-functional requirements, including the SAJ library's, and links to the global requirements in `.github/work/requirements.md`. A section of `docs/features.md` with a matching section there has a `Requirements:` line linking to it, and the matching section has a `Features:` line linking back. A requirement change that concerns the integration goes into `docs/requirements.md`.

## Stored Forms

From the first beta, `1.0.0b1`, a change to any stored form (config entry data or options, a subentry's data, the power control store, or a value stored in one of them) raises the config entry `VERSION` or `MINOR_VERSION`, or the store version, and adds a migration. The one exception is a breaking change that the user approved under the Backwards Compatibility rules in the root `AGENTS.md`.
