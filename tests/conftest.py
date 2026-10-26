import gc


def pytest_collection_finish() -> None:
    # The imports of the whole run leave a heap that the first full collection scans
    # for about 100 ms, and that collection falls inside whichever test is running
    # when the allocation count trips it. Sweeping once before any test runs, and
    # freezing the result, keeps the pause out of the tests.
    gc.collect()
    gc.freeze()
