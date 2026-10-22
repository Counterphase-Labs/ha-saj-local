# Cards Requirements

Global requirements: [requirements.md](../../.github/work/requirements.md)

## Elements and setup

Features: [Elements and setup](features.md#elements-and-setup)

- Expose UI elements that can be added to lovelace dashboards, including informational and configuration
    - Cards for power flow, system status, faults, the battery, controls and schedules, a weekday picker for schedule slots and a status badge
    - Each element is set up by choosing a system, so the same element can be added once for each system
    - Each element shows only what its system has, and keeps working when the system's prefix changes
    - Elements look and behave like standard Home Assistant cards and follow the user's theme and language
