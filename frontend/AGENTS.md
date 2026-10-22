# Card Guidance

This folder is the source of the SAJ Local cards, the tile card feature and the badge that the integration serves to Home Assistant dashboards. The root `AGENTS.md` also applies.

## Feature List

`docs/features.md` lists what each element shows and what the user can set on it. Users and developers read the file to learn what the cards offer.

- Give the file one section per element, plus sections for what all elements share. A section opens with a heading and an overview of one to three sentences, then a `Files:` line linking the card source files behind the section, then bullets.
- Write one bullet per thing the user can see or set, such as a figure, a status, a button or an editor option. Leave out the detail of a single logic path.
- List only what the elements do today. A behaviour that is merely required, planned or partly built stays out.
- Write in plain words, using the terms the integration shows to users. Element, file and function names stay out of the bullets, and dates, plan names and roadmap claims do not appear.
- A limitation a user would trip over, or an element part shown for one model only, is stated inside its bullet.
- Format `docs/features.md` and this file with Prettier, because the `prettier` check covers Markdown in this folder.

## Requirements

`docs/requirements.md` holds the requirements on the cards and links to the global requirements in `.github/work/requirements.md`. Each section of `docs/features.md` that has a section of the same name there links to it with a `Requirements:` line, and that section links back with a `Features:` line. A requirement change that concerns the cards goes into `docs/requirements.md`.
