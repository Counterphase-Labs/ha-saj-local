# Security policy

SAJ Local reads and can change the settings of a solar inverter and its battery, so a security problem in SAJ Local can matter in the real world. Thank you for reporting one privately.

## Report a problem

Use the [Report a vulnerability](https://github.com/Counterphase-Labs/ha-saj-local/security/advisories/new) form on GitHub. The report is visible only to the maintainers of SAJ Local. Do not open a public issue for a security problem.

Describe what you found, how to reproduce the problem and what an attacker could do with the problem. A [diagnostics download](docs/en-gb/user/troubleshooting.md#download-diagnostics) helps and is safe to attach, see [what the file and the log leave out](docs/en-gb/user/troubleshooting.md#what-the-file-and-the-log-leave-out).

## What happens next

- You get an answer within 7 days.
- The fix ships in a new release of SAJ Local.
- After the release, a GitHub security advisory describes the problem and the fix.
- The advisory credits you, unless you ask not to be named.

## Supported releases

Only the latest release receives security fixes. Update SAJ Local through HACS to get a fix.

## Scope

Everything in this repository: the integration, the dashboard cards and the Modbus simulator. Examples of a security problem:

- A change reaches the inverter while Allow control is off.
- SAJ Local writes to the inverter without being asked to.
- The diagnostics download, the debug log or a repair issue shows the host, the full serial number, network addresses or other private data.
- A card or the card bundle served by Home Assistant runs code the card should not run, or mishandles entity state, for example by showing data from another system.
- The simulator's web page or Modbus server lets a client reach files or commands on the computer that runs the simulator.

Not a security problem in SAJ Local:

- Modbus TCP has no authentication. Anyone who reaches the Modbus port of the inverter can read and change the inverter, with or without SAJ Local. Keep the inverter on a private network, such as a separate VLAN.
- A problem in Home Assistant itself. Report the problem to [Home Assistant](https://www.home-assistant.io/security/).
- A problem in HACS. Report the problem to the HACS project.
- A problem in the inverter firmware or the SAJ communication module. Report the problem to SAJ.
