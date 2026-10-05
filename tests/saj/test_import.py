import importlib


def test_library_imports_without_home_assistant():
    assert importlib.import_module("saj")
