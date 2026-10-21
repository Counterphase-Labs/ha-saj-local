from __future__ import annotations

import ast
import json
from pathlib import Path

LIBRARY_DIRECTORY = Path("custom_components/saj_local/saj")
INTEGRATION_DIRECTORY = Path("custom_components/saj_local")
MOCK_DIRECTORY = Path("mock/saj_local_mock")
SCRIPTS_DIRECTORY = Path(".github/scripts")
TESTS_DIRECTORY = Path("tests")
MODULE_DIRECTORIES: dict[Path, tuple[Path, ...]] = {
    TESTS_DIRECTORY / "saj": (LIBRARY_DIRECTORY, LIBRARY_DIRECTORY / "models"),
    TESTS_DIRECTORY / "saj-integration": (INTEGRATION_DIRECTORY,),
    TESTS_DIRECTORY / "mock": (MOCK_DIRECTORY,),
    TESTS_DIRECTORY / "mock" / "profiles": (MOCK_DIRECTORY / "profiles",),
    TESTS_DIRECTORY / "mock" / "simulation": (MOCK_DIRECTORY / "simulation",),
    TESTS_DIRECTORY / "scripts": (SCRIPTS_DIRECTORY,),
}
OVERRIDES_FILE = SCRIPTS_DIRECTORY / "pytest_scope.json"
SOURCE_DIRECTORIES = (INTEGRATION_DIRECTORY, MOCK_DIRECTORY, SCRIPTS_DIRECTORY)
RUNNER_PROCESSES_TESTS = TESTS_DIRECTORY / "scripts" / "test_runner_processes.py"
LOGIC_NODES = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Lambda,
    ast.If,
    ast.IfExp,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.TryStar,
    ast.Match,
    ast.With,
    ast.AsyncWith,
    ast.BoolOp,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)
SELECTION_OPTIONS = frozenset({"-k", "-m", "--lf", "--last-failed"})


class ScopeError(Exception):
    pass


def selected_test_files(args: tuple[str, ...], root: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for argument in args:
        if argument.startswith("-"):
            continue
        target = Path(argument.split("::", 1)[0])
        absolute = root / target
        if absolute.is_dir():
            if absolute.resolve() == (root / TESTS_DIRECTORY).resolve():
                return ()
            files.extend(
                path.relative_to(root)
                for path in sorted(absolute.rglob("test_*.py"))
                if path.relative_to(root) != RUNNER_PROCESSES_TESTS
            )
        elif absolute.is_file() and target.name.startswith("test_"):
            files.append(target)
    return tuple(dict.fromkeys(files))


def candidate_directories(test_file: Path) -> tuple[Path, ...]:
    return MODULE_DIRECTORIES.get(test_file.parent, ())


def load_overrides(root: Path) -> dict[str, list[str]]:
    return json.loads((root / OVERRIDES_FILE).read_text(encoding="utf-8"))


def modules_for(
    test_file: Path, root: Path, overrides: dict[str, list[str]]
) -> tuple[Path, ...]:
    explicit = overrides.get(test_file.as_posix())
    if explicit is not None:
        return tuple(Path(module) for module in explicit)
    stem = test_file.stem.removeprefix("test_")
    for directory in candidate_directories(test_file):
        candidate = directory / f"{stem}.py"
        if (root / candidate).is_file():
            return (candidate,)
    message = (
        f"no module is known for {test_file.as_posix()}: "
        f"add it to {OVERRIDES_FILE.as_posix()}"
    )
    raise ScopeError(message)


def unit_test_files(root: Path) -> tuple[Path, ...]:
    return tuple(
        path.relative_to(root)
        for directory in MODULE_DIRECTORIES
        for path in sorted((root / directory).glob("test_*.py"))
        if path.relative_to(root) != RUNNER_PROCESSES_TESTS
    )


def module_tests(root: Path) -> dict[Path, tuple[Path, ...]]:
    overrides = load_overrides(root)
    mapping: dict[Path, list[Path]] = {}
    for test_file in unit_test_files(root):
        for module in modules_for(test_file, root, overrides):
            mapping.setdefault(module, []).append(test_file)
    return {module: tuple(files) for module, files in mapping.items()}


def has_logic(source: str) -> bool:
    return any(isinstance(node, LOGIC_NODES) for node in ast.walk(ast.parse(source)))


def gated_modules(root: Path) -> tuple[Path, ...]:
    return tuple(
        path.relative_to(root)
        for directory in SOURCE_DIRECTORIES
        for path in sorted((root / directory).rglob("*.py"))
        if has_logic(path.read_text(encoding="utf-8"))
    )


def companion_test_files(
    args: tuple[str, ...], modules: tuple[Path, ...], root: Path
) -> tuple[Path, ...]:
    selected = set(selected_test_files(args, root))
    mapping = module_tests(root)
    companions = (
        test_file
        for module in modules
        for test_file in mapping.get(module, ())
        if test_file not in selected
    )
    return tuple(dict.fromkeys(companions))


def scope_for(args: tuple[str, ...], root: Path) -> tuple[Path, ...] | None:
    files = selected_test_files(args, root)
    if not files:
        if SELECTION_OPTIONS.intersection(args):
            message = (
                "selecting tests with -k, -m or --lf needs a test file in ARGS "
                "so coverage can be gated on the module it tests"
            )
            raise ScopeError(message)
        return None
    overrides = load_overrides(root)
    modules: list[Path] = []
    for test_file in files:
        modules.extend(modules_for(test_file, root, overrides))
    return tuple(dict.fromkeys(modules))


def coverage_configuration(modules: tuple[Path, ...]) -> str:
    included = "\n".join(f"    {module.as_posix()}" for module in modules)
    return f"[report]\ninclude =\n{included}\n"
