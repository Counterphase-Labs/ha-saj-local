en | [de](docs/de/README.md) | [nl](docs/nl/README.md) | [fr](docs/fr/README.md) | [zh](docs/zh-hans/README.md) | [es](docs/es/README.md) | [it](docs/it/README.md) | [pl](docs/pl/README.md) | [sv](docs/sv/README.md)

# SAJ Local Home Assistant Integration

![SAJ Local](images/header.png)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Release](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![Active installs](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=active%20installs&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![CI](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![Licence](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local)](LICENSE)

⭐ [Star the project on GitHub](https://github.com/Counterphase-Labs/ha-saj-local): your support is a real motivation! 🙏😊

Your SAJ solar system in Home Assistant, read straight from the inverter over your own network. No cloud account, no vendor app in the middle, and a polling approach designed to be gentle on the hardware.

This is an unofficial, community-built integration. It is not made, supported or endorsed by SAJ. See the [disclaimer](docs/en-gb/user/README.md#disclaimer).

> **Status: in active development and not yet released.** There is no published release yet.

## Why SAJ Local

- **Sensible by default.** Add your inverter and get a working setup without wading through pages of options. The inverter, battery and related equipment are detected automatically.
- **Gentle on your inverter.** One connection and one request at a time, and a hard ceiling on requests that no setting, reload or failure can exceed. You choose what is read and how often.
- **Read-only unless you say otherwise.** Writing is opt-in per installation, so nothing changes on your inverter by accident.
- **The same names on every model.** Dashboards and automations are written once and keep working across SAJ models, and survive a move from an H2 to an HS3.
- **Several systems.** Connect more than one SAJ system to the same Home Assistant.
- **Dashboard cards.** Cards for viewing information and for changing configuration, added from the card picker.
- **Clear errors and safe diagnostics.** When something goes wrong you are told what and why, and debug dumps are built to be safe to share.
- **Fully local.** Everything talks to your inverter over your network. Nothing is sent to a cloud service.

## Supported equipment

The SAJ HS3 and the single-phase SAJ H2 are supported. See [supported equipment](docs/en-gb/user/supported-equipment.md) for the full list and what is not supported yet.

## Documentation

- [User documentation](docs/en-gb/user/README.md): install, set up and operate SAJ Local.
- [Developer documentation](docs/en-gb/developer/README.md): how SAJ Local is built, checked and released.
- [Contributing](CONTRIBUTING.md): set up a checkout and send a change.

## Help and feedback

Questions, bug reports and ideas are welcome on the [issue tracker](https://github.com/Counterphase-Labs/ha-saj-local/issues).

Report a security problem privately, see the [security policy](SECURITY.md).

## Licence

[MIT](LICENSE)
