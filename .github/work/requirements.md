# SAJ Integration

## Purpose and scope

High level requirements is to provide a stable integration with wide SAJ support for common household inverter, battery and related equipment.

Development is done with HS3 system for reference

Platform stability and correctness is paramount.

- This HACS repository will be the sole repository and must contain all elements of the integration, including the SAJ stand alone library, the actual SAJ integration, any lovelace components and custom dashboards

## Compatibility

- Backwards compatibility MUST drive architecture decisions.
- Sensor names MUST remain stable.
- Architecture decisions SHOULD limit the risk of a future breaking change.
- A breaking change is a change that breaks an existing installation, dashboard or automation.
- Before the first beta, `1.0.0b1`, a change MUST NOT add a backwards compatibility layer, and a breaking change is acceptable.
- From the first beta until `1.0.0`, a change MUST NOT be a breaking change, unless the maintainer approves the breaking change as an exception.
- An approved exception MUST NOT add a backwards compatibility layer.
- From `1.0.0`, a change MUST NOT be a breaking change.

## Security

- Users can report a security problem privately, and know how to.

## Releases

- A release is a GitHub release made from a version tag on `main`. The tag, the version in `custom_components/saj_local/manifest.json`, the version in `pyproject.toml` and the version in `frontend/package.json` are the same, and the release runs `make ci` on the tagged commit before the release is created.
- Versions are `X.Y.Z` for a stable release and `X.Y.ZbN` for a beta. A beta is published as a GitHub pre-release. The first stable release is `1.0.0`, and the betas before the first stable release are `1.0.0b1`, `1.0.0b2` and so on. From `1.0.0`, Semantic Versioning applies.
- The release notes are written in the GitHub release. A beta's release notes name every change to an entity, a stored setting, a card type or a card setting since the previous beta.

## Model abstraction

- The different implementations of SAJ systems form an abstraction layer. There is a single unified interface (entities, controls, Lovelace elements) that does the same thing across all models, as closely as each model allows: consistent names, values, units and behaviour. Where models differ, each model's implementation translates to and from the common form.

- A feature is left out only on a model that lacks the possibility to do it.

## Language

- The integration, the cards and the user and developer documentation are available in English and in every target language. The target languages are the eight languages SAJ translates its own website into that have the most Home Assistant installations: German, Dutch, French, Simplified Chinese, Spanish, Italian, Polish and Swedish.

- The feature lists and the requirement documents are in English only.

- English texts and keys use British spelling

## Development environment

- Development in completely isolated docker environment

## Testing

- 100% unit test coverage for all lines, statements and paths.

- **CRITICAL**: The 100% coverage MUST come from unit tests alone. Integration tests are NOT an acceptable replacement and MUST NOT count towards the coverage requirement.

- A unit test exercises a single module in isolation through its own public interface, with plain inputs and every collaborating module replaced by a stub, fake or mock. A test is NOT a unit test if it assembles several real modules together, opens a socket or network connection, starts a server, reads fixture or configuration files from the project, depends on real time, or runs a long simulation to reach its assertion.

- Unit tests MUST be fast. A unit test that takes more than a few milliseconds is not a unit test.

- Integration tests MUST ONLY be used as critical path smoke tests, for example: can the service be connected to and does it return a value. They MUST be few, MUST NOT be used to prove application logic or behaviour, and MUST be kept separate from the unit tests.

- noqa or any other inline test or lint bypass is FORBIDDEN in this project. Exceptions can be granted by the user on a case by case basis.

- DO NOT write unit tests that test hard coded values, constants or similar. Tests MUST focus on application logic, behaviour and interactions.

- Playwright tests for UI covering only critical paths

- Playwright tests split into 1. fake UI with controlled data 2. actual HA development environment through docker

## Verification

- All commands for things like building, running, testing, linting, etc are exposed as make targets
  - One `make build` builds everything the project builds. There is no build target per feature or part, such as `frontend-build` or `showcase-build`
  - One `make test` runs every test. Each test suite also has its own target, which `make test` runs
  - One `make ci` runs every check. The partial targets that make up `make ci` stay

- From `1.0.0`, `make ci` fails when a change removes an entity key, a stored setting key, a card type or a card setting, changes an entity's platform, unit, device class, state class or state values, removes a value a card setting accepts, or lowers a config entry or store version, compared with the newest stable release tag.

- All testing and verification can run in github workflows using the same make targets

## Part Requirements

- [Integration requirements](../../custom_components/saj_local/docs/requirements.md)
- [Cards requirements](../../frontend/docs/requirements.md)
- [Simulator requirements](../../mock/docs/requirements.md)
