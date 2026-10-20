from types import SimpleNamespace

from custom_components.saj_local import label


def test_the_entry_label_names_the_entry_by_its_title_and_serial(monkeypatch):
    calls = []

    def system_label(*, title, serial):
        calls.append((title, serial))
        return "the label"

    monkeypatch.setattr(label, "system_label", system_label)
    entry = SimpleNamespace(title="Roof inverter", unique_id="S2303J4567")

    assert label.entry_label(entry=entry) == "the label"
    assert calls == [("Roof inverter", "S2303J4567")]


def test_the_entry_logger_wraps_the_logger_with_the_label_of_the_entry(monkeypatch):
    monkeypatch.setattr(label, "entry_label", lambda *, entry: f"label of {entry}")
    monkeypatch.setattr(
        label,
        "LabelledLogger",
        lambda *, logger, label: SimpleNamespace(logger=logger, label=label),
    )

    wrapped = label.entry_logger(logger="the logger", entry="the entry")

    assert (wrapped.logger, wrapped.label) == ("the logger", "label of the entry")
