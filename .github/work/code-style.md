# Code Style

## Documentation

- Markdown files must not be artificially wrapped at a fixed line length; lines should only break at natural boundaries like paragraphs or list items.
- Do not document trivial or self-evident information; focus on meaningful and necessary details.
- Any documentation SHOULD almost exclusively focus on the WHY (which rarely changes), rather than the HOW (which is evident from the code itself).


## Code

This includes both application code and testing.

- SOLID principles MUST be followed.
- High cohesion and low coupling MUST be maintained throughout the codebase.
- Code MUST be self documenting, clear and descriptive names must be used for variables, functions, classes, and other identifiers.
- Use named arguments for functions and methods
- Avoid using magic numbers; use named constants instead.
- Use type hints for all function and method signatures.

## Testing

In addition to the general code style guidelines, testing code must also adhere to the following principles:

- Use multivariate tests to cover multiple scenarios and edge cases without excessive duplication.
- Tests MUST be isolated and independent from each other.
- Use descriptive names for test functions to clearly indicate the scenario being tested.
- Avoid testing implementation details; focus on testing behaviour and outcomes.
- Mock external dependencies to ensure tests are deterministic and reliable.
