from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path
from typing import ClassVar

import module_gate
import pytest
import pytest_scope

MODULE = Path("custom_components/saj_local/saj/codec.py")
OTHER = Path("custom_components/saj_local/saj/client.py")
CODEC_TESTS = (Path("tests/saj/test_codec.py"), Path("tests/saj/test_models.py"))
COVERED = {
    "missing_lines": [],
    "missing_branches": [],
    "summary": {"percent_covered": 100.0},
}


class FakeCoverage:
    reports: ClassVar[dict[str, dict[str, object]]] = {}
    loaded: ClassVar[list[tuple[str, object]]] = []
    queried: ClassVar[list[list[str]]] = []

    def __init__(self, *, data_file: str, config_file: object) -> None:
        self.data_file = data_file
        self.config_file = config_file

    def load(self) -> None:
        self.loaded.append((self.data_file, self.config_file))

    def json_report(
        self, *, morfs: list[str], outfile: str, contexts: list[str]
    ) -> float:
        assert outfile == "-"
        self.queried.append(contexts)
        sys.stdout.write(json.dumps({"files": {morfs[0]: self.reports[morfs[0]]}}))
        return 0.0


@pytest.fixture(autouse=True)
def coverage_data(monkeypatch):
    monkeypatch.setattr(module_gate.coverage, "Coverage", FakeCoverage)
    mapping = {MODULE: CODEC_TESTS, OTHER: (Path("tests/saj/test_client.py"),)}
    for owner in (module_gate, pytest_scope):
        monkeypatch.setattr(owner, "module_tests", lambda _root: mapping)
    monkeypatch.setattr(FakeCoverage, "reports", {})
    monkeypatch.setattr(FakeCoverage, "loaded", [])
    monkeypatch.setattr(FakeCoverage, "queried", [])
    return FakeCoverage


def test_the_contexts_are_the_import_time_code_and_the_mapped_test_files_only():
    first, second = module_gate.contexts_of(CODEC_TESTS)

    assert re.search(first, "")
    assert not re.search(first, "tests/saj/test_codec.py::test_a|run")
    assert re.search(second, "tests/saj/test_codec.py::test_a[1-x]|run")
    assert re.search(second, "tests/saj/test_models.py::test_b|setup")
    assert not re.search(second, "tests/saj/test_client.py::test_c|run")
    assert not re.search(second, "tests/saj/test_codecXpy::test_a|run")


def test_a_fully_covered_module_has_no_gap(coverage_data):
    coverage_data.reports[MODULE.as_posix()] = COVERED

    gap = module_gate.module_gap(
        FakeCoverage(data_file="d", config_file=False),
        module=MODULE,
        test_files=CODEC_TESTS,
    )

    assert gap is None
    assert coverage_data.queried == [module_gate.contexts_of(CODEC_TESTS)]


def test_a_module_with_missing_lines_and_branches_names_each_of_them(coverage_data):
    coverage_data.reports[MODULE.as_posix()] = {
        "missing_lines": [12, 30],
        "missing_branches": [[40, 42], [50, -3]],
        "summary": {"percent_covered": 96.25},
    }

    gap = module_gate.module_gap(
        FakeCoverage(data_file="d", config_file=False),
        module=MODULE,
        test_files=CODEC_TESTS,
    )

    assert gap == f"{MODULE.as_posix()}: 96.2% missing 12, 30, 40->42, 50->exit"


def test_a_module_without_a_unit_test_file_is_a_gap_without_reading_coverage(
    coverage_data,
):
    gap = module_gate.module_gap(
        FakeCoverage(data_file="d", config_file=False), module=MODULE, test_files=()
    )

    assert gap == f"{MODULE.as_posix()}: no unit test file"
    assert coverage_data.queried == []


def test_the_gate_passes_when_every_module_is_covered(coverage_data, capsys):
    coverage_data.reports[MODULE.as_posix()] = COVERED
    coverage_data.reports[OTHER.as_posix()] = COVERED

    status = module_gate.main(["data", MODULE.as_posix(), OTHER.as_posix()])

    assert status == 0
    assert capsys.readouterr().out == "2 of 2 modules covered\n"
    assert coverage_data.loaded == [("data", False)]


def test_the_gate_fails_each_module_with_a_gap_and_counts_the_covered_ones(
    coverage_data, capsys
):
    coverage_data.reports[MODULE.as_posix()] = {
        "missing_lines": [7],
        "missing_branches": [],
        "summary": {"percent_covered": 90.0},
    }
    coverage_data.reports[OTHER.as_posix()] = COVERED
    untested = "custom_components/saj_local/saj/untested.py"

    status = module_gate.main(["data", MODULE.as_posix(), OTHER.as_posix(), untested])

    assert status == 1
    assert capsys.readouterr().out == (
        f"finding {MODULE.as_posix()}: 90.0% missing 7\n"
        f"finding {untested}: no unit test file\n"
        "1 of 3 modules covered\n"
    )


def test_running_the_gate_as_a_script_exits_with_its_status(
    coverage_data, monkeypatch, capsys
):
    coverage_data.reports[MODULE.as_posix()] = COVERED
    monkeypatch.setattr("sys.argv", ["module_gate.py", "data", MODULE.as_posix()])

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("module_gate", run_name="__main__")

    assert stopped.value.code == 0
    assert capsys.readouterr().out == "1 of 1 modules covered\n"
