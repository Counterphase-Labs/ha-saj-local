import logging

import pytest

from saj.log import LabelledLogger, mask_serial, system_label

SERIAL = "H1S23456789"


@pytest.mark.parametrize(
    ("serial", "masked"),
    [
        (SERIAL, "xxxxx789"),
        ("ABCD", "xxxxxBCD"),
        ("ABC", "xxxxx"),
        ("AB", "xxxxx"),
        ("A", "xxxxx"),
    ],
)
def test_a_serial_is_masked_to_its_last_three_characters_unless_that_would_reveal_it(
    serial: str, masked: str
):
    assert mask_serial(serial=serial) == masked


@pytest.mark.parametrize(
    ("title", "serial", "label"),
    [
        (f"SAJ {SERIAL}", SERIAL, "SAJ xxxxx789"),
        (f"saj {SERIAL.lower()}", SERIAL, "saj xxxxx789"),
        (f"{SERIAL} and {SERIAL}", SERIAL, "xxxxx789 and xxxxx789"),
        ("Garage", SERIAL, "Garage (xxxxx789)"),
        ("", SERIAL, "xxxxx789"),
        ("Garage", "ABC", "Garage (xxxxx)"),
        ("SAJ ABC", "ABC", "SAJ xxxxx"),
        ("Garage", None, "Garage"),
        ("Garage", "", "Garage"),
    ],
)
def test_the_label_masks_the_serial_in_the_title_or_appends_it_masked(
    title: str, serial: str | None, label: str
):
    assert system_label(title=title, serial=serial) == label


def test_the_label_never_contains_the_full_serial():
    for title in (f"SAJ {SERIAL}", "Garage", f"x{SERIAL}y"):
        assert SERIAL not in system_label(title=title, serial=SERIAL)


def test_a_labelled_logger_prefixes_lines_and_keeps_the_module_logger(caplog):
    module_logger = logging.getLogger("saj.example")
    logger = LabelledLogger(logger=module_logger, label="Garage (xxxxx789)")

    with caplog.at_level(logging.DEBUG, logger="saj.example"):
        logger.debug("polled %s requests", 3)

    (record,) = caplog.records
    assert record.name == "saj.example"
    assert record.getMessage() == "Garage (xxxxx789): polled 3 requests"


@pytest.mark.parametrize(
    ("args", "expected"),
    [((), "100% solar: plain"), ((5,), "100% solar: value 5")],
    ids=["without_arguments", "with_arguments"],
)
def test_a_label_containing_a_percent_sign_appears_verbatim(caplog, args, expected):
    logger = LabelledLogger(logger=logging.getLogger("saj.example"), label="100% solar")
    message = "value %s" if args else "plain"

    with caplog.at_level(logging.INFO, logger="saj.example"):
        logger.info(message, *args)

    assert caplog.records[0].getMessage() == expected


def test_a_labelled_line_is_attributed_to_the_code_that_logged_it(caplog):
    logger = LabelledLogger(logger=logging.getLogger("saj.example"), label="Roof")

    with caplog.at_level(logging.INFO, logger="saj.example"):
        logger.info("here")

    assert caplog.records[0].filename == "test_log.py"


def test_the_debug_switch_of_the_module_logger_governs_a_labelled_logger(caplog):
    logger = LabelledLogger(logger=logging.getLogger("saj.example"), label="Roof")

    with caplog.at_level(logging.INFO, logger="saj.example"):
        logger.debug("hidden")
        logger.info("shown")

    assert [record.getMessage() for record in caplog.records] == ["Roof: shown"]
