en | [de](../../de/user/installation.md) | [nl](../../nl/user/installation.md) | [fr](../../fr/user/installation.md) | [zh](../../zh-hans/user/installation.md) | [es](../../es/user/installation.md) | [it](../../it/user/installation.md) | [pl](../../pl/user/installation.md) | [sv](../../sv/user/installation.md)

# Installation

The Installation page installs SAJ Local with HACS, the Home Assistant Community Store. The full list of what setup does is in the [Setup and detection](../../../custom_components/saj_local/docs/features.md#setup-and-detection) section of the integration feature list.

SAJ Local has no published release yet. Check the [supported equipment](supported-equipment.md) before you install.

## What you need

- Home Assistant at the minimum version named in [`hacs.json`](../../../hacs.json), and HACS.
- A supported SAJ inverter that answers Modbus TCP on your local network. You need the address of the inverter, and the port and the unit ID when the port or the unit ID is not the default.
- Nothing else. SAJ Local talks to the inverter directly and sends nothing to a cloud service.

## Install

1. Open SAJ Local in HACS with the first button below. HACS asks you to add the repository if the repository is not listed yet.
2. Download SAJ Local in HACS.
3. Restart Home Assistant.
4. Add your system with the second button below, or follow [get started](getting-started.md).

[![Open your Home Assistant instance and open the SAJ Local repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Open your Home Assistant instance and start setting up SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local serves dashboard cards, so there is no card resource to add. See [dashboard cards](cards/README.md).

## Beta versions

Until the first stable release, every release of SAJ Local is a beta. In HACS, open SAJ Local, open the menu, choose Redownload, turn on "Show beta versions" and download the newest beta. Without the switch, HACS installs the development version of SAJ Local.
