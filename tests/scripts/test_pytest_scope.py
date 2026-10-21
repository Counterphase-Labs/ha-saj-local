from __future__ import annotations

import json
from pathlib import Path

import pytest
from pytest_scope import (
    OVERRIDES_FILE,
    ScopeError,
    companion_test_files,
    coverage_configuration,
    gated_modules,
    has_logic,
    module_tests,
    scope_for,
    selected_test_files,
    unit_test_files,
)

INTEGRATION = "custom_components/saj_local"
LIBRARY = f"{INTEGRATION}/saj"
MOCK = "mock/saj_local_mock"


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    for module in (
        f"{LIBRARY}/codec.py",
        f"{LIBRARY}/models/hs3.py",
        f"{INTEGRATION}/coordinator.py",
        f"{INTEGRATION}/config_flow.py",
        f"{MOCK}/machine.py",
        f"{MOCK}/profiles/common.py",
        f"{MOCK}/simulation/battery.py",
        ".github/scripts/check_runner.py",
    ):
        path = tmp_path / module
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    for test in (
        "tests/saj/test_codec.py",
        "tests/saj/test_hs3.py",
        "tests/saj/test_unmapped_thing.py",
        "tests/saj-integration/test_coordinator.py",
        "tests/saj-integration/test_coordinator_write.py",
        "tests/mock/test_machine.py",
        "tests/mock/profiles/test_common.py",
        "tests/mock/simulation/test_battery.py",
        "tests/scripts/test_check_runner.py",
        "tests/scripts/test_runner_processes.py",
        "tests/helpers.py",
    ):
        path = tmp_path / test
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    overrides = tmp_path / OVERRIDES_FILE
    overrides.write_text(
        json.dumps(
            {
                "tests/saj-integration/test_coordinator_write.py": [
                    f"{INTEGRATION}/coordinator.py"
                ],
                "tests/saj/test_unmapped_thing.py": [
                    f"{LIBRARY}/codec.py",
                    f"{LIBRARY}/models/hs3.py",
                ],
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def modules(repository: Path, *args: str) -> tuple[str, ...] | None:
    scope = scope_for(args, repository)
    return None if scope is None else tuple(module.as_posix() for module in scope)


@pytest.mark.parametrize(
    ("test_file", "module"),
    [
        ("tests/saj/test_codec.py", f"{LIBRARY}/codec.py"),
        ("tests/saj/test_hs3.py", f"{LIBRARY}/models/hs3.py"),
        ("tests/saj-integration/test_coordinator.py", f"{INTEGRATION}/coordinator.py"),
        ("tests/mock/test_machine.py", f"{MOCK}/machine.py"),
        ("tests/mock/profiles/test_common.py", f"{MOCK}/profiles/common.py"),
        (
            "tests/mock/simulation/test_battery.py",
            f"{MOCK}/simulation/battery.py",
        ),
        ("tests/scripts/test_check_runner.py", ".github/scripts/check_runner.py"),
    ],
)
def test_a_test_file_gates_the_module_with_the_same_name_in_its_folders_module_folder(
    repository, test_file, module
):
    assert modules(repository, test_file) == (module,)


def test_an_override_names_every_module_a_test_file_tests(repository):
    assert modules(repository, "tests/saj/test_unmapped_thing.py") == (
        f"{LIBRARY}/codec.py",
        f"{LIBRARY}/models/hs3.py",
    )


def test_an_override_wins_over_the_naming_convention(repository):
    assert modules(repository, "tests/saj-integration/test_coordinator_write.py") == (
        f"{INTEGRATION}/coordinator.py",
    )


def test_a_test_file_without_a_module_is_rejected_with_the_way_to_fix_it(repository):
    with pytest.raises(ScopeError, match=r"pytest_scope\.json"):
        scope_for(("tests/scripts/test_runner_processes.py",), repository)


def test_node_ids_and_options_are_reduced_to_their_test_file(repository):
    assert modules(
        repository,
        "tests/saj/test_codec.py::test_one",
        "-x",
        "-s",
        "tests/saj/test_codec.py",
    ) == (f"{LIBRARY}/codec.py",)


def test_several_files_gate_the_union_of_their_modules(repository):
    assert modules(
        repository, "tests/saj/test_codec.py", "tests/mock/test_machine.py"
    ) == (f"{LIBRARY}/codec.py", f"{MOCK}/machine.py")


def test_a_directory_selects_every_test_file_in_it(repository):
    files = selected_test_files(("tests/mock/simulation",), repository)

    assert files == (Path("tests/mock/simulation/test_battery.py"),)


def test_a_path_that_is_not_a_test_file_selects_nothing(repository):
    assert selected_test_files(("tests/helpers.py", "tests/missing"), repository) == ()


def test_the_whole_tests_directory_is_a_full_run(repository):
    assert modules(repository, "tests") is None
    assert modules(repository, "tests/") is None


def test_no_test_file_is_a_full_run(repository):
    assert modules(repository) is None
    assert modules(repository, "-x") is None


def test_the_value_of_a_selection_option_is_not_mistaken_for_a_test_file(repository):
    assert modules(repository, "tests/saj/test_codec.py", "-k", "ramp") == (
        f"{LIBRARY}/codec.py",
    )


@pytest.mark.parametrize("option", ["-k", "-m", "--lf", "--last-failed"])
def test_selecting_tests_without_a_test_file_cannot_be_gated(repository, option):
    with pytest.raises(ScopeError, match="needs a test file"):
        scope_for((option, "ramp"), repository)


def test_the_coverage_configuration_reports_only_the_given_modules():
    configuration = coverage_configuration(
        (Path(f"{INTEGRATION}/coordinator.py"), Path(f"{INTEGRATION}/config_flow.py"))
    )

    assert configuration.endswith(
        "include =\n"
        f"    {INTEGRATION}/coordinator.py\n"
        f"    {INTEGRATION}/config_flow.py\n"
    )


def test_the_unit_test_files_are_the_test_folders_files_but_the_process_tests(
    repository,
):
    assert {path.as_posix() for path in unit_test_files(repository)} == {
        "tests/saj/test_codec.py",
        "tests/saj/test_hs3.py",
        "tests/saj/test_unmapped_thing.py",
        "tests/saj-integration/test_coordinator.py",
        "tests/saj-integration/test_coordinator_write.py",
        "tests/mock/test_machine.py",
        "tests/mock/profiles/test_common.py",
        "tests/mock/simulation/test_battery.py",
        "tests/scripts/test_check_runner.py",
    }


def test_each_module_maps_to_every_test_file_that_tests_it(repository):
    mapping = {
        module.as_posix(): tuple(path.as_posix() for path in files)
        for module, files in module_tests(repository).items()
    }

    assert mapping[f"{INTEGRATION}/coordinator.py"] == (
        "tests/saj-integration/test_coordinator.py",
        "tests/saj-integration/test_coordinator_write.py",
    )
    assert mapping[f"{LIBRARY}/codec.py"] == (
        "tests/saj/test_codec.py",
        "tests/saj/test_unmapped_thing.py",
    )


@pytest.mark.parametrize(
    "source",
    [
        "def run():\n    return 1\n",
        "async def run():\n    return 1\n",
        "class Thing:\n    def run(self):\n        return 1\n",
        "VALUE = lambda: 1\n",
        "if FLAG:\n    VALUE = 1\n",
        "VALUE = 1 if FLAG else 2\n",
        "for item in ITEMS:\n    pass\n",
        "async def run():\n    async for item in ITEMS:\n        pass\n",
        "while FLAG:\n    pass\n",
        "try:\n    pass\nexcept ValueError:\n    pass\n",
        "try:\n    pass\nexcept* ValueError:\n    pass\n",
        "match FLAG:\n    case 1:\n        pass\n",
        "with OPEN:\n    pass\n",
        "async def run():\n    async with OPEN:\n        pass\n",
        "VALUE = FIRST or SECOND\n",
        "VALUE = [item for item in ITEMS]\n",
        "VALUE = {item for item in ITEMS}\n",
        "VALUE = {item: 1 for item in ITEMS}\n",
        "VALUE = (item for item in ITEMS)\n",
    ],
)
def test_a_module_with_a_function_or_a_branch_has_logic(source):
    assert has_logic(source)


@pytest.mark.parametrize(
    "source",
    [
        "",
        "\n",
        "VALUE = 1\n",
        "from x import y\n\nTABLE = {'a': (1, 2)}\n",
        "class Thing:\n    FIELD = 1\n",
    ],
)
def test_a_module_with_no_function_and_no_branch_has_no_logic(source):
    assert not has_logic(source)


def test_only_modules_with_logic_are_gated(repository):
    (repository / f"{LIBRARY}/codec.py").write_text(
        "def run():\n    return 1\n", encoding="utf-8"
    )
    (repository / f"{LIBRARY}/models/hs3.py").write_text(
        "TABLE = {'a': 1}\n", encoding="utf-8"
    )
    (repository / f"{MOCK}/machine.py").write_text(
        "VALUE = 1 if FLAG else 2\n", encoding="utf-8"
    )

    assert [path.as_posix() for path in gated_modules(repository)] == [
        f"{LIBRARY}/codec.py",
        f"{MOCK}/machine.py",
    ]


def test_a_subset_run_brings_the_other_test_files_of_its_modules(repository):
    args = ("tests/saj-integration/test_coordinator_write.py::test_one", "-x")
    scope = scope_for(args, repository)
    assert scope is not None

    companions = companion_test_files(args, scope, repository)

    assert [path.as_posix() for path in companions] == [
        "tests/saj-integration/test_coordinator.py"
    ]


def test_a_module_without_a_mapped_test_file_brings_no_companions(repository):
    companions = companion_test_files(
        (), (Path(f"{INTEGRATION}/config_flow.py"),), repository
    )

    assert companions == ()


def test_a_directory_leaves_out_the_process_tests_the_unit_run_ignores(repository):
    files = selected_test_files(("tests/scripts",), repository)

    assert files == (Path("tests/scripts/test_check_runner.py"),)
