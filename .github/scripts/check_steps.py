from __future__ import annotations

import re
import shlex
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import check_parsers
from pytest_scope import (
    RUNNER_PROCESSES_TESTS,
    ScopeError,
    companion_test_files,
    coverage_configuration,
    gated_modules,
    module_tests,
    scope_for,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from check_parsers import Parsed, Parser

SPARSE_ENVIRONMENT = {
    "COMPOSE_PROGRESS": "quiet",
    "UV_NO_PROGRESS": "1",
}
DEFAULT_TIMEOUT_SECONDS = 1800
SHORT_TIMEOUT_SECONDS = 600
PYTEST_TIMEOUT_SECONDS = 3600
BROWSER_TIMEOUT_SECONDS = 1800
FRONTEND_DIRECTORY = "frontend"
CONTROLLED_REPORT = "frontend/playwright-report/controlled"
HOME_ASSISTANT_REPORT = "frontend/playwright-report/home-assistant"
HASSFEST_IMAGE = "ghcr.io/home-assistant/hassfest"
ISOLATED_TEST_PATHS = ("tests/saj", "tests/mock")
ISOLATED_ENVIRONMENT = {"UV_PROJECT_ENVIRONMENT": ".venv-isolated"}
IMPORT_LINT_ENVIRONMENT = {"PYTHONPATH": ".:mock"}
UNCOVERED_ADDOPTS = "-q --tb=short"
MOCK_INTEGRATION_DIRECTORY = "tests/mock-integration"
MOCK_SERVICE = "mock"
MOCK_SMOKE_SCRIPT = f"{MOCK_INTEGRATION_DIRECTORY}/smoke.sh"
MOCK_BYTECODE_CHECK = (
    "import pathlib, sys; "
    "sys.exit(any(pathlib.Path('/app').rglob('*.py[cod]')) "
    "or any(pathlib.Path('/app').rglob('__pycache__')))"
)
PYTEST_QUIET_OPTIONS = re.compile(r"^(-q+|--tb=.*|--cov-report=.*)$")


class StepUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class Invocation:
    args: tuple[str, ...]
    verbose: bool
    root: Path
    scratch: Path


@dataclass(frozen=True)
class Command:
    argv: tuple[str, ...]
    parser: Parser
    cwd: str | None = None
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    environment: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Help:
    summary: str
    runs: str
    success: str
    failure: str
    args: str


@dataclass(frozen=True)
class Step:
    name: str
    build: Callable[[Invocation], tuple[Command, ...]]
    help: Help
    requires: tuple[str, ...] = ()
    combine: Callable[[tuple[Parsed, ...]], Parsed] | None = None


def _pyproject_addopts(root: Path) -> list[str]:
    with (root / "pyproject.toml").open("rb") as handle:
        configuration = tomllib.load(handle)
    return list(configuration["tool"]["pytest"]["ini_options"]["addopts"])


def pytest_verbose_addopts(addopts: list[str]) -> str:
    kept = [option for option in addopts if not PYTEST_QUIET_OPTIONS.match(option)]
    kept.append("--cov-report=term-missing")
    return shlex.join(kept)


def _verbose_options(invocation: Invocation) -> list[str]:
    if not invocation.verbose:
        return []
    addopts = pytest_verbose_addopts(_pyproject_addopts(invocation.root))
    return ["-o", f"addopts={addopts}"]


def _pytest_options(invocation: Invocation) -> list[str]:
    options = _verbose_options(invocation)
    modules = scope_for(invocation.args, invocation.root)
    if modules is not None:
        configuration = invocation.scratch / "coverage-scope.ini"
        configuration.write_text(coverage_configuration(modules), encoding="utf-8")
        sources = dict.fromkeys(module.parent.as_posix() for module in modules)
        options.extend(f"--cov={source}" for source in sources)
        options.extend(["--cov-config", str(configuration)])
        companions = companion_test_files(invocation.args, modules, invocation.root)
        options.extend(test_file.as_posix() for test_file in companions)
    return options


def _test_python(invocation: Invocation) -> tuple[Command, ...]:
    return (
        Command(
            (
                "uv",
                "run",
                "pytest",
                *_pytest_options(invocation),
                *invocation.args,
            ),
            check_parsers.parse_pytest,
            timeout=PYTEST_TIMEOUT_SECONDS,
        ),
    )


def _test_isolated(invocation: Invocation) -> tuple[Command, ...]:
    selected = Invocation(
        args=invocation.args or ISOLATED_TEST_PATHS,
        verbose=invocation.verbose,
        root=invocation.root,
        scratch=invocation.scratch,
    )
    return (
        Command(
            (
                "uv",
                "run",
                "--only-group",
                "test",
                "pytest",
                *_pytest_options(selected),
                *selected.args,
            ),
            check_parsers.parse_pytest,
            timeout=PYTEST_TIMEOUT_SECONDS,
            environment=ISOLATED_ENVIRONMENT,
        ),
    )


def _uncovered_pytest(*paths: str) -> Command:
    return Command(
        ("uv", "run", "pytest", "-o", f"addopts={UNCOVERED_ADDOPTS}", *paths),
        check_parsers.parse_pytest,
        timeout=PYTEST_TIMEOUT_SECONDS,
    )


def _test_runner_processes(invocation: Invocation) -> tuple[Command, ...]:
    default = (RUNNER_PROCESSES_TESTS.as_posix(),)
    return (_uncovered_pytest(*(invocation.args or default)),)


def _requested_modules(invocation: Invocation) -> tuple[Path, ...]:
    modules = gated_modules(invocation.root)
    if not invocation.args:
        return modules
    requested = tuple(Path(argument) for argument in invocation.args)
    unknown = [module.as_posix() for module in requested if module not in modules]
    if unknown:
        message = f"not a module with code: {', '.join(unknown)}"
        raise StepUnavailableError(message)
    return requested


def _test_modules(invocation: Invocation) -> tuple[Command, ...]:
    modules = _requested_modules(invocation)
    mapping = module_tests(invocation.root)
    untested = [module.as_posix() for module in modules if module not in mapping]
    if untested:
        message = f"no unit test file for: {', '.join(untested)}"
        raise ScopeError(message)
    commands: list[Command] = []
    for index, module in enumerate(modules):
        configuration = invocation.scratch / f"coverage-module-{index}.ini"
        configuration.write_text(coverage_configuration((module,)), encoding="utf-8")
        commands.append(
            Command(
                (
                    "uv",
                    "run",
                    "pytest",
                    *_verbose_options(invocation),
                    f"--cov={module.parent.as_posix()}",
                    "--cov-config",
                    str(configuration),
                    *(test_file.as_posix() for test_file in mapping[module]),
                ),
                check_parsers.module_coverage(module.as_posix()),
                timeout=SHORT_TIMEOUT_SECONDS,
            )
        )
    return tuple(commands)


def _mock_smoke(invocation: Invocation) -> tuple[Command, ...]:
    del invocation
    return (
        Command(
            (MOCK_SMOKE_SCRIPT,),
            check_parsers.plain("scenarios answered"),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        ),
        _uncovered_pytest(MOCK_INTEGRATION_DIRECTORY),
    )


def _ruff(invocation: Invocation) -> tuple[Command, ...]:
    paths = invocation.args or (".",)
    check_options = ("--output-format=full",) if invocation.verbose else ()
    return (
        Command(
            ("uv", "run", "ruff", "format", "--check", *paths),
            check_parsers.parse_ruff_format,
            timeout=SHORT_TIMEOUT_SECONDS,
        ),
        Command(
            ("uv", "run", "ruff", "check", *check_options, *paths),
            check_parsers.parse_ruff_check,
            timeout=SHORT_TIMEOUT_SECONDS,
        ),
    )


def _mypy(invocation: Invocation) -> tuple[Command, ...]:
    options = ("--pretty", "--error-summary") if invocation.verbose else ()
    return (
        Command(
            ("uv", "run", "mypy", *options, *invocation.args),
            check_parsers.parse_mypy,
        ),
    )


def _import_lint(invocation: Invocation) -> tuple[Command, ...]:
    return (
        Command(
            ("uv", "run", "lint-imports", *invocation.args),
            check_parsers.parse_import_linter,
            timeout=SHORT_TIMEOUT_SECONDS,
            environment=IMPORT_LINT_ENVIRONMENT,
        ),
    )


def _complexipy(invocation: Invocation) -> tuple[Command, ...]:
    options = () if invocation.verbose else ("--plain",)
    return (
        Command(
            ("uv", "run", "complexipy", *options, *invocation.args),
            check_parsers.parse_complexipy,
            timeout=SHORT_TIMEOUT_SECONDS,
        ),
    )


def _copy_paste(invocation: Invocation) -> tuple[Command, ...]:
    options = ("--reporters", "console") if invocation.verbose else ()
    paths = invocation.args or (".",)
    return (
        Command(
            ("uv", "run", "jscpd", *options, *paths),
            check_parsers.parse_jscpd,
            timeout=SHORT_TIMEOUT_SECONDS,
        ),
    )


def _npm_script(
    script: str,
    parser: Parser,
    verbose_options: tuple[str, ...],
    timeout: int = SHORT_TIMEOUT_SECONDS,
) -> Callable[[Invocation], tuple[Command, ...]]:
    def build(invocation: Invocation) -> tuple[Command, ...]:
        forwarded = (
            (*verbose_options, *invocation.args)
            if invocation.verbose
            else invocation.args
        )
        separator = ("--",) if forwarded else ()
        return (
            Command(
                ("npm", "run", script, *separator, *forwarded),
                parser,
                cwd=FRONTEND_DIRECTORY,
                timeout=timeout,
            ),
        )

    return build


def _browser_home_assistant(invocation: Invocation) -> tuple[Command, ...]:
    options = ("--reporter=list",) if invocation.verbose else ()
    return (
        Command(
            (
                "tests/playwright/run-home-assistant.sh",
                *options,
                *invocation.args,
            ),
            check_parsers.playwright(HOME_ASSISTANT_REPORT),
            timeout=BROWSER_TIMEOUT_SECONDS,
        ),
    )


def _release_check(invocation: Invocation) -> tuple[Command, ...]:
    del invocation
    script = Path(__file__).with_name("release_check.py")
    return (
        Command(
            (sys.executable, str(script)),
            check_parsers.parse_release_check,
            timeout=SHORT_TIMEOUT_SECONDS,
        ),
    )


def _validate(invocation: Invocation) -> tuple[Command, ...]:
    return (
        Command(
            (
                "docker",
                "run",
                "--quiet",
                "--rm",
                "--volume",
                f"{invocation.root}:/github/workspace",
                HASSFEST_IMAGE,
            ),
            check_parsers.parse_hassfest,
            timeout=SHORT_TIMEOUT_SECONDS,
        ),
    )


def _fixed(
    argv: tuple[str, ...],
    summary: str,
    cwd: str | None = None,
    timeout: int = SHORT_TIMEOUT_SECONDS,
) -> Callable[[Invocation], tuple[Command, ...]]:
    def build(invocation: Invocation) -> tuple[Command, ...]:
        del invocation
        return (Command(argv, check_parsers.plain(summary), cwd=cwd, timeout=timeout),)

    return build


def _mock_build(invocation: Invocation) -> tuple[Command, ...]:
    del invocation
    return (
        Command(
            ("docker", "compose", "build", MOCK_SERVICE),
            check_parsers.plain("built"),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        ),
        Command(
            (
                "docker",
                "compose",
                "run",
                "--rm",
                "--no-deps",
                "--entrypoint",
                "python",
                MOCK_SERVICE,
                "-c",
                MOCK_BYTECODE_CHECK,
            ),
            check_parsers.plain("no bytecode"),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        ),
    )


NO_ARGS = "not used"
PATHS_ARGS = "paths to check instead of the whole repository"
TOOL_ARGS = "options and paths passed to the tool"

STEPS: tuple[Step, ...] = (
    Step(
        "ruff",
        _ruff,
        Help(
            summary="formatting and lint of the Python code",
            runs="ruff format --check, then ruff check",
            success="formatted, no findings",
            failure=(
                "each unformatted file, and file:line code message for each finding"
            ),
            args=PATHS_ARGS,
        ),
    ),
    Step(
        "mypy",
        _mypy,
        Help(
            summary="strict type check of the Python code",
            runs="mypy in strict mode",
            success="no errors",
            failure="file:line error: message [code] for each error",
            args="paths and mypy options passed to mypy",
        ),
    ),
    Step(
        "import-lint",
        _import_lint,
        Help(
            summary="import-linter architecture contracts",
            runs="lint-imports",
            success="contracts kept",
            failure="each broken contract with its import chains",
            args="options passed to lint-imports",
        ),
    ),
    Step(
        "complexipy",
        _complexipy,
        Help(
            summary="cognitive complexity limit",
            runs="complexipy",
            success="none over the limit",
            failure="each function over the limit and its score",
            args="paths and options passed to complexipy",
        ),
    ),
    Step(
        "copy-paste",
        _copy_paste,
        Help(
            summary="duplicate code and text detection",
            runs="jscpd",
            success="no duplicates",
            failure="each duplicated block as file:lines and file:lines",
            args=PATHS_ARGS,
        ),
    ),
    Step(
        "test-python",
        _test_python,
        Help(
            summary="Python unit tests with the 100 % coverage gate",
            runs="pytest over the whole package, or over the test files in ARGS",
            success=(
                "pass count, total coverage, every warning exactly as pytest prints "
                "it and each file below 100 % coverage with its missing lines and "
                "branches"
            ),
            failure=(
                "failing test IDs with short tracebacks, plus the same warnings and "
                "files, and the required threshold when the gate fails"
            ),
            args=(
                "test files, folders and pytest options; a subset run measures and "
                "gates only the modules those test files test"
            ),
        ),
    ),
    Step(
        "test-modules",
        _test_modules,
        Help(
            summary="per-module coverage gate from the unit tests of the module alone",
            runs=(
                "for each module with logic, the unit test files mapped to the "
                "module, run together, with 100 % line and branch coverage required "
                "of that module alone"
            ),
            success="modules covered out of modules gated",
            failure=(
                "per failing module: the module, its coverage with missing lines and "
                "branches, failing tests, or no unit test file"
            ),
            args="module paths that limit the run",
        ),
        combine=check_parsers.combine_modules,
    ),
    Step(
        "test-isolated",
        _test_isolated,
        Help(
            summary="unit tests in an environment without Home Assistant",
            runs=(
                "the tests/saj and tests/mock tests in .venv-isolated, with coverage "
                "scoped as a subset run"
            ),
            success="as test-python",
            failure="as test-python",
            args="test files and folders instead of tests/saj and tests/mock",
        ),
    ),
    Step(
        "test-runner-processes",
        _test_runner_processes,
        Help(
            summary="real-process tests of the check runner",
            runs=(
                "the tests in tests/scripts/test_runner_processes.py, with no "
                "coverage options"
            ),
            success="pass count and warnings",
            failure="failing test IDs with short tracebacks",
            args="test files and pytest options instead of the default test file",
        ),
    ),
    Step(
        "prettier",
        _npm_script(
            "format:check", check_parsers.parse_prettier, ("--log-level", "log")
        ),
        Help(
            summary="formatting of the frontend code",
            runs="prettier --check in frontend",
            success="formatted",
            failure="each unformatted file",
            args=TOOL_ARGS,
        ),
    ),
    Step(
        "tsc",
        _npm_script("typecheck", check_parsers.parse_tsc, ("--pretty", "true")),
        Help(
            summary="type check of the frontend code",
            runs="tsc --noEmit in frontend",
            success="no errors",
            failure="file:line code message for each error",
            args=TOOL_ARGS,
        ),
    ),
    Step(
        "eslint",
        _npm_script("lint", check_parsers.parse_eslint, ("--format", "stylish")),
        Help(
            summary="lint of the frontend code",
            runs="ESLint in frontend",
            success="no findings",
            failure="file:line:column rule message for each finding",
            args=TOOL_ARGS,
        ),
    ),
    Step(
        "test-frontend",
        _npm_script(
            "test",
            check_parsers.parse_vitest,
            ("--reporter=default", "--coverage.reporter=text"),
        ),
        Help(
            summary="frontend unit tests",
            runs="the Vitest unit tests in frontend",
            success="pass count",
            failure=(
                "failing tests with assertion messages, and the coverage table when "
                "the gate fails"
            ),
            args=TOOL_ARGS,
        ),
    ),
    Step(
        "build",
        _npm_script("build", check_parsers.parse_vite_build, ()),
        Help(
            summary="production build of the frontend",
            runs="the Vite production build in frontend",
            success="names of the built assets",
            failure="the build failure",
            args=TOOL_ARGS,
        ),
    ),
    Step(
        "test-browser-controlled",
        _npm_script(
            "test:browser:controlled",
            check_parsers.playwright(CONTROLLED_REPORT),
            ("--reporter=list",),
            timeout=BROWSER_TIMEOUT_SECONDS,
        ),
        Help(
            summary="browser tests against the built bundle with controlled data",
            runs="Playwright against the built bundle, after the build step",
            success="pass count",
            failure=(
                "failing tests with assertion messages, plus the report path "
                f"{CONTROLLED_REPORT}"
            ),
            args=TOOL_ARGS,
        ),
        requires=("build",),
    ),
    Step(
        "release-check",
        _release_check,
        Help(
            summary="contents of the HACS release archive",
            runs="a check of the files the HACS archive holds",
            success="archive complete",
            failure="each missing archive entry",
            args=NO_ARGS,
        ),
    ),
    Step(
        "mock-build",
        _mock_build,
        Help(
            summary="build of the Modbus mock image",
            runs=(
                "docker compose build of the Modbus mock, then a bytecode check of "
                "the image"
            ),
            success="built, no bytecode",
            failure="the raw failure output",
            args=NO_ARGS,
        ),
    ),
    Step(
        "mock-smoke",
        _mock_smoke,
        Help(
            summary="the Modbus mock container answers a client",
            runs=(
                f"{MOCK_SMOKE_SCRIPT}, then the tests in {MOCK_INTEGRATION_DIRECTORY} "
                "with no coverage options"
            ),
            success="scenarios answered",
            failure="the raw failure output, or failing test IDs with short tracebacks",
            args=NO_ARGS,
        ),
    ),
    Step(
        "validate",
        _validate,
        Help(
            summary="hassfest validation of the integration",
            runs="hassfest against the working tree, in Docker",
            success="manifest valid",
            failure="each failed check and its message",
            args=NO_ARGS,
        ),
    ),
    Step(
        "test-browser-home-assistant",
        _browser_home_assistant,
        Help(
            summary="browser tests against a throwaway Home Assistant",
            runs="Playwright against a throwaway Home Assistant in Docker",
            success="pass count",
            failure=(
                "failing tests with assertion messages, plus the report path "
                f"{HOME_ASSISTANT_REPORT}"
            ),
            args="options passed to the Playwright run script",
        ),
    ),
)

CHECK_STEP_NAMES = tuple(step.name for step in STEPS)

SUPPORT_STEPS: tuple[Step, ...] = (
    Step(
        "uv-sync",
        _fixed(("uv", "sync", "--group", "dev", "--group", "lint"), "synced"),
        Help(
            summary="Python dependency install",
            runs="uv sync with the dev and lint groups",
            success="synced",
            failure="the raw failure output",
            args=NO_ARGS,
        ),
    ),
    Step(
        "npm-ci",
        _fixed(
            ("npm", "ci", "--loglevel=error"),
            "installed",
            cwd=FRONTEND_DIRECTORY,
        ),
        Help(
            summary="frontend dependency install",
            runs="npm ci in frontend",
            success="installed",
            failure="the raw failure output",
            args=NO_ARGS,
        ),
    ),
    Step(
        "playwright-install",
        _fixed(
            ("npx", "playwright", "install", "chromium"),
            "installed",
            cwd=FRONTEND_DIRECTORY,
        ),
        Help(
            summary="Chromium install for Playwright",
            runs="npx playwright install chromium in frontend",
            success="installed",
            failure="the raw failure output",
            args=NO_ARGS,
        ),
    ),
    Step(
        "up",
        _fixed(
            (
                "docker",
                "compose",
                "up",
                "--detach",
                "--build",
                "--remove-orphans",
                "--force-recreate",
            ),
            "started",
        ),
        Help(
            summary="start the development Home Assistant instance",
            runs="docker compose up, detached, rebuilt and recreated",
            success="started",
            failure="the raw failure output",
            args=NO_ARGS,
        ),
    ),
    Step(
        "down",
        _fixed(("docker", "compose", "down"), "stopped"),
        Help(
            summary="stop the development Home Assistant instance",
            runs="docker compose down",
            success="stopped",
            failure="the raw failure output",
            args=NO_ARGS,
        ),
    ),
)

STEPS_BY_NAME = {step.name: step for step in (*STEPS, *SUPPORT_STEPS)}


@dataclass(frozen=True)
class Group:
    name: str
    summary: str
    steps: tuple[str, ...]


GROUPS: tuple[Group, ...] = (
    Group(
        "setup",
        "install the Python and frontend dependencies and Chromium",
        ("uv-sync", "npm-ci", "playwright-install"),
    ),
    Group(
        "lint",
        "Python lint and type checks",
        ("ruff", "mypy", "import-lint", "complexipy"),
    ),
    Group(
        "test",
        "every test step",
        (
            "test-python",
            "test-modules",
            "test-frontend",
            "test-isolated",
            "test-runner-processes",
            "test-browser-controlled",
            "test-browser-home-assistant",
            "mock-smoke",
        ),
    ),
    Group(
        "python-ci",
        "every Python check and test step",
        (
            "ruff",
            "mypy",
            "import-lint",
            "complexipy",
            "copy-paste",
            "test-python",
            "test-modules",
            "test-isolated",
            "test-runner-processes",
        ),
    ),
    Group(
        "frontend-check",
        "frontend format, type, lint and unit tests",
        ("prettier", "tsc", "eslint", "test-frontend"),
    ),
    Group(
        "frontend-ci",
        "frontend-check and the controlled browser tests",
        ("prettier", "tsc", "eslint", "test-frontend", "test-browser-controlled"),
    ),
    Group(
        "ci",
        "every check step, the gate after code changes",
        CHECK_STEP_NAMES,
    ),
)

GROUPS_BY_NAME = {group.name: group for group in GROUPS}

LOGS_HELP = Help(
    summary="follow the log of the development Home Assistant instance",
    runs="docker compose logs -f homeassistant, not through the runner",
    success="the log, unchanged",
    failure="the docker compose error, unchanged",
    args=NO_ARGS,
)

HELP_HELP = Help(
    summary="list every make target, or describe one",
    runs="the help of the runner, not a check step",
    success="the list of targets, or the detail of the target named in ARGS",
    failure="a message naming the unknown target, with a non-zero exit",
    args="the name of one target to describe; empty lists every target",
)
