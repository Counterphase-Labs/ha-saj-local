from __future__ import annotations

import json
from typing import TYPE_CHECKING

import check_steps
import pytest
from check_steps import Invocation, pytest_verbose_addopts

if TYPE_CHECKING:
    from pathlib import Path

ADDOPTS = ["-q", "--tb=short", "--cov=pkg", "--cov-report=term-missing:skip-covered"]


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\n"
        'addopts = ["-q", "--tb=short", "--ignore=tests/mock-integration", '
        '"--cov=pkg", '
        '"--cov-report=term-missing:skip-covered", "--cov-fail-under=100"]\n',
        encoding="utf-8",
    )
    module = tmp_path / "custom_components" / "saj_local" / "saj" / "codec.py"
    module.parent.mkdir(parents=True)
    module.write_text("", encoding="utf-8")
    for test in ("tests/saj/test_codec.py", "tests/saj/test_models.py"):
        path = tmp_path / test
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    overrides = tmp_path / ".github" / "scripts" / "pytest_scope.json"
    overrides.parent.mkdir(parents=True)
    overrides.write_text(
        json.dumps(
            {"tests/saj/test_models.py": ["custom_components/saj_local/saj/codec.py"]}
        ),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def scratch(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("scratch")


def build(
    name: str, root: Path, scratch: Path, *args: str, verbose: bool = False
) -> tuple[check_steps.Command, ...]:
    invocation = Invocation(args=args, verbose=verbose, root=root, scratch=scratch)
    return check_steps.STEPS_BY_NAME[name].build(invocation)


def test_verbose_pytest_options_drop_the_quiet_ones_and_restore_the_raw_reports():
    assert pytest_verbose_addopts(ADDOPTS).split() == [
        "--cov=pkg",
        "--cov-report=term-missing",
    ]


def test_a_full_python_test_run_keeps_the_configured_coverage_scope(root, scratch):
    (command,) = build("test-python", root, scratch)

    assert command.argv == ("uv", "run", "pytest")
    assert command.timeout == check_steps.PYTEST_TIMEOUT_SECONDS


def test_a_python_test_run_of_one_test_file_reports_coverage_for_its_module_only(
    root, scratch
):
    (command,) = build("test-python", root, scratch, "tests/saj/test_codec.py", "-x")

    configuration = scratch / "coverage-scope.ini"
    assert command.argv == (
        "uv",
        "run",
        "pytest",
        "--cov=custom_components/saj_local/saj",
        "--cov-config",
        str(configuration),
        "tests/saj/test_models.py",
        "tests/saj/test_codec.py",
        "-x",
    )
    assert "custom_components/saj_local/saj/codec.py" in configuration.read_text(
        encoding="utf-8"
    )


def test_a_verbose_python_test_run_restores_the_raw_options(root, scratch):
    (command,) = build("test-python", root, scratch, verbose=True)

    assert command.argv[:4] == ("uv", "run", "pytest", "-o")
    assert command.argv[4].removeprefix("addopts=").split() == [
        "--ignore=tests/mock-integration",
        "--cov=pkg",
        "--cov-fail-under=100",
        "--cov-report=term-missing",
    ]


def test_the_isolated_run_uses_the_test_group_in_its_own_environment_with_a_scope(
    root, scratch
):
    (command,) = build("test-isolated", root, scratch)

    assert command.argv == (
        "uv",
        "run",
        "--only-group",
        "test",
        "pytest",
        "--cov=custom_components/saj_local/saj",
        "--cov-config",
        str(scratch / "coverage-scope.ini"),
        "tests/saj",
        "tests/mock",
    )
    assert command.environment == {"UV_PROJECT_ENVIRONMENT": ".venv-isolated"}


def test_the_isolated_run_takes_the_given_test_files_instead_of_the_folders(
    root, scratch
):
    (command,) = build("test-isolated", root, scratch, "tests/saj/test_codec.py")

    assert command.argv[-1] == "tests/saj/test_codec.py"
    assert "tests/saj" not in command.argv


def test_the_runner_processes_run_has_no_coverage_options(root, scratch):
    (default,) = build("test-runner-processes", root, scratch)
    (selected,) = build(
        "test-runner-processes", root, scratch, "tests/scripts/test_a.py"
    )

    assert default.argv == (
        "uv",
        "run",
        "pytest",
        "-o",
        "addopts=-q --tb=short",
        "tests/scripts/test_runner_processes.py",
    )
    assert selected.argv[-1] == "tests/scripts/test_a.py"


def test_ruff_checks_formatting_and_lint_of_the_given_paths(root, scratch):
    format_command, check_command = build("ruff", root, scratch, "a.py")

    assert format_command.argv == ("uv", "run", "ruff", "format", "--check", "a.py")
    assert check_command.argv == ("uv", "run", "ruff", "check", "a.py")


def test_ruff_defaults_to_the_whole_repository_and_verbose_restores_full_findings(
    root, scratch
):
    format_command, check_command = build("ruff", root, scratch, verbose=True)

    assert format_command.argv[-1] == "."
    assert "--output-format=full" in check_command.argv
    assert "--output-format=full" not in format_command.argv


def test_import_lint_runs_with_the_library_and_mock_on_the_python_path(root, scratch):
    (command,) = build("import-lint", root, scratch)

    assert command.argv == ("uv", "run", "lint-imports")
    assert command.environment == {"PYTHONPATH": ".:mock"}


def test_complexipy_is_plain_unless_verbose(root, scratch):
    (quiet,) = build("complexipy", root, scratch)
    (verbose,) = build("complexipy", root, scratch, verbose=True)

    assert "--plain" in quiet.argv
    assert "--plain" not in verbose.argv


def test_copy_paste_scans_the_given_paths_and_verbose_restores_the_console_report(
    root, scratch
):
    (quiet,) = build("copy-paste", root, scratch, "src")
    (verbose,) = build("copy-paste", root, scratch, verbose=True)

    assert quiet.argv == ("uv", "run", "jscpd", "src")
    assert verbose.argv == ("uv", "run", "jscpd", "--reporters", "console", ".")


def test_mypy_runs_the_configured_files_and_verbose_restores_the_decoration(
    root, scratch
):
    (quiet,) = build("mypy", root, scratch, "a.py")
    (verbose,) = build("mypy", root, scratch, verbose=True)

    assert quiet.argv == ("uv", "run", "mypy", "a.py")
    assert verbose.argv == ("uv", "run", "mypy", "--pretty", "--error-summary")


def test_npm_scripts_run_in_the_frontend_and_pass_args_after_a_separator(root, scratch):
    (bare,) = build("tsc", root, scratch)
    (with_args,) = build("eslint", root, scratch, "src/a.ts")

    assert bare.argv == ("npm", "run", "typecheck")
    assert bare.cwd == "frontend"
    assert with_args.argv == ("npm", "run", "lint", "--", "src/a.ts")


def test_verbose_npm_scripts_put_the_restoring_options_before_the_args(root, scratch):
    (command,) = build("test-frontend", root, scratch, "tests/a.test.ts", verbose=True)

    assert command.argv == (
        "npm",
        "run",
        "test",
        "--",
        "--reporter=default",
        "--coverage.reporter=text",
        "tests/a.test.ts",
    )


def test_the_controlled_browser_tests_need_a_fresh_frontend_build():
    assert check_steps.STEPS_BY_NAME["test-browser-controlled"].requires == ("build",)


def test_the_home_assistant_browser_tests_forward_args_and_verbose_reporter(
    root, scratch
):
    (quiet,) = build("test-browser-home-assistant", root, scratch, "-g", "panel")
    (verbose,) = build("test-browser-home-assistant", root, scratch, verbose=True)

    assert quiet.argv == ("tests/playwright/run-home-assistant.sh", "-g", "panel")
    assert verbose.argv == ("tests/playwright/run-home-assistant.sh", "--reporter=list")


def test_release_check_runs_the_archive_script_with_the_current_interpreter(
    root, scratch
):
    (command,) = build("release-check", root, scratch)

    assert command.argv[1].endswith("release_check.py")


def test_the_mock_build_builds_the_image_then_checks_it_for_bytecode(root, scratch):
    build_command, bytecode_command = build("mock-build", root, scratch)

    assert build_command.argv == ("docker", "compose", "build", "mock")
    assert bytecode_command.argv[:8] == (
        "docker",
        "compose",
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "python",
        "mock",
    )
    assert "__pycache__" in bytecode_command.argv[-1]


def test_the_mock_smoke_runs_the_smoke_script_then_the_integration_tests(root, scratch):
    script, tests = build("mock-smoke", root, scratch)

    assert script.argv == ("tests/mock-integration/smoke.sh",)
    assert tests.argv == (
        "uv",
        "run",
        "pytest",
        "-o",
        "addopts=-q --tb=short",
        "tests/mock-integration",
    )


def test_validation_runs_hassfest_quietly_against_the_working_tree(root, scratch):
    (hassfest,) = build("validate", root, scratch)

    assert f"{root}:/github/workspace" in hassfest.argv
    assert "--quiet" in hassfest.argv


def test_the_up_action_builds_and_recreates_the_containers(root, scratch):
    (up,) = build("up", root, scratch)
    (down,) = build("down", root, scratch)

    assert up.argv == (
        "docker",
        "compose",
        "up",
        "--detach",
        "--build",
        "--remove-orphans",
        "--force-recreate",
    )
    assert down.argv == ("docker", "compose", "down")


def test_the_setup_actions_install_python_and_frontend_dependencies(root, scratch):
    (sync,) = build("uv-sync", root, scratch)
    (install,) = build("npm-ci", root, scratch)
    (browser,) = build("playwright-install", root, scratch)

    assert sync.argv == ("uv", "sync", "--group", "dev", "--group", "lint")
    assert install.cwd == browser.cwd == "frontend"


def test_every_check_step_has_a_unique_name_and_the_checks_run_in_order():
    assert check_steps.CHECK_STEP_NAMES == (
        "ruff",
        "mypy",
        "import-lint",
        "complexipy",
        "copy-paste",
        "test-python",
        "test-modules",
        "test-isolated",
        "test-runner-processes",
        "prettier",
        "tsc",
        "eslint",
        "test-frontend",
        "build",
        "test-browser-controlled",
        "release-check",
        "mock-build",
        "mock-smoke",
        "validate",
        "test-browser-home-assistant",
    )


def test_the_module_gate_runs_every_test_file_of_each_module_for_that_module_only(
    root, scratch
):
    (root / "custom_components/saj_local/saj/codec.py").write_text(
        "def run():\n    return 1\n", encoding="utf-8"
    )

    (command,) = build("test-modules", root, scratch)

    configuration = scratch / "coverage-module-0.ini"
    assert command.argv == (
        "uv",
        "run",
        "pytest",
        "--cov=custom_components/saj_local/saj",
        "--cov-config",
        str(configuration),
        "tests/saj/test_codec.py",
        "tests/saj/test_models.py",
    )
    assert "    custom_components/saj_local/saj/codec.py\n" in (
        configuration.read_text(encoding="utf-8")
    )
    assert command.timeout == check_steps.SHORT_TIMEOUT_SECONDS
    assert command.parser("", 0).summary == "covered"
    assert check_steps.STEPS_BY_NAME["test-modules"].combine is not None


def test_a_verbose_module_gate_restores_the_raw_options(root, scratch):
    (root / "custom_components/saj_local/saj/codec.py").write_text(
        "def run():\n    return 1\n", encoding="utf-8"
    )

    (command,) = build("test-modules", root, scratch, verbose=True)

    assert command.argv[3] == "-o"


def test_the_module_gate_runs_only_the_modules_named_in_args(root, scratch):
    for name in ("codec", "client"):
        (root / f"custom_components/saj_local/saj/{name}.py").write_text(
            "def run():\n    return 1\n", encoding="utf-8"
        )

    (command,) = build(
        "test-modules", root, scratch, "custom_components/saj_local/saj/codec.py"
    )

    assert command.argv[-2:] == ("tests/saj/test_codec.py", "tests/saj/test_models.py")


def test_the_module_gate_rejects_a_name_that_is_not_a_module_with_code(root, scratch):
    with pytest.raises(check_steps.StepUnavailableError, match="not a module"):
        build("test-modules", root, scratch, "custom_components/saj_local/saj/codec.py")


def test_the_module_gate_fails_for_a_module_without_a_unit_test_file(root, scratch):
    (root / "custom_components/saj_local/saj/client.py").write_text(
        "def run():\n    return 1\n", encoding="utf-8"
    )

    with pytest.raises(check_steps.ScopeError, match=r"saj/client\.py"):
        build("test-modules", root, scratch)
