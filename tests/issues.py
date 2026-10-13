from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import ModuleType

    import pytest


class IssueRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.finding = None
        self.errors: list[Exception] = []

    def install(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        module: ModuleType,
        names: Iterable[str],
    ) -> None:
        for name in names:
            monkeypatch.setattr(module, name, self._record(name))
        monkeypatch.setattr(module, "model_finding", self._found)

    def called(self, name: str) -> list[dict]:
        return [arguments for called, arguments in self.calls if called == name]

    def _record(self, name: str):
        def call(**arguments) -> None:
            self.calls.append((name, arguments))

        return call

    def _found(self, *, error: Exception):
        self.errors.append(error)
        return self.finding
