from __future__ import annotations

import json
import runpy

import pytest
import template_check

LABELS = ["fix", "triage"]
MODELS = ["HS3", "H2"]


def bug_template(**changes):
    template = {
        "labels": ["fix"],
        "body": [
            {"type": "markdown", "attributes": {"value": "plain"}},
            {
                "type": "dropdown",
                "id": "model",
                "attributes": {"options": [*MODELS, "Other"]},
            },
            {
                "type": "textarea",
                "id": "diagnostics",
                "validations": {"required": True},
            },
        ],
    }
    template.update(changes)
    return template


def findings(template, name="bug.yml", labels=LABELS):
    return template_check.template_findings(
        template_name=name,
        template=template,
        label_names=labels,
        model_labels=MODELS,
    )


def test_a_clean_bug_template_has_no_findings():
    assert findings(bug_template()) == []


@pytest.mark.parametrize(
    "diagnostics",
    [
        {"type": "textarea", "id": "diagnostics"},
        {"type": "textarea", "id": "diagnostics", "validations": {"required": False}},
        {"type": "input", "id": "diagnostics", "validations": {"required": True}},
    ],
)
def test_a_diagnostics_field_that_is_not_a_required_textarea_is_a_finding(diagnostics):
    template = bug_template()
    template["body"][2] = diagnostics

    assert findings(template) == ["the diagnostics field must be a required textarea"]


def test_a_missing_diagnostics_field_is_a_finding():
    template = bug_template()
    del template["body"][2]

    assert findings(template) == ["the diagnostics field must be a required textarea"]


def test_a_missing_model_dropdown_is_a_finding():
    template = bug_template()
    del template["body"][1]

    assert findings(template) == ["the model dropdown is missing"]


def test_a_model_field_that_is_not_a_dropdown_is_a_finding():
    template = bug_template()
    template["body"][1] = {"type": "input", "id": "model"}

    assert findings(template) == ["the model dropdown is missing"]


@pytest.mark.parametrize(
    "options",
    [
        ["HS3", "Other"],
        ["H2", "HS3", "Other"],
        ["HS3", "H2"],
        ["HS3", "H2", "X", "Other"],
    ],
)
def test_model_options_that_differ_from_the_translations_are_a_finding(options):
    template = bug_template()
    template["body"][1]["attributes"]["options"] = options

    (finding,) = findings(template)

    assert finding.startswith("the model options")


def test_the_bug_rules_apply_only_to_the_bug_template():
    assert findings({"body": []}, name="other.yml") == []


def test_a_label_missing_from_the_label_file_is_a_finding():
    template = bug_template(labels=["fix", "ghost"])

    assert findings(template) == ["the label ghost is not in .github/labels.yml"]


def test_a_template_without_labels_has_no_label_finding():
    assert findings({"body": []}, name="other.yml") == []


def test_a_search_link_naming_a_missing_label_is_a_finding():
    template = bug_template()
    template["body"][0]["attributes"]["value"] = (
        "[search](../../issues?q=label%3A%22ghost+label%22)"
    )

    assert findings(template) == [
        "the search link names ghost label, not in .github/labels.yml"
    ]


def test_a_search_link_naming_a_known_label_is_clean():
    template = bug_template()
    template["body"][0]["attributes"]["value"] = "[a](../../issues?q=label%3Afix)"

    assert findings(template) == []


def test_link_labels_reads_quoted_and_bare_labels_from_every_link():
    text = (
        "[a](../../issues?q=is%3Aissue+label%3A%22%F0%9F%9B%A0+goal%3A+fix%22+) "
        "and ../../issues?q=label%3Abare"
    )

    assert template_check.link_labels(text=text) == ["🛠 goal: fix", "bare"]


def test_link_labels_ignores_text_without_a_search_link():
    assert template_check.link_labels(text="label:fix and no link") == []


def test_a_label_named_twice_is_reported_once():
    labels = ["a", "b", "a", "a"]

    assert template_check.duplicate_labels(labels=labels) == ["a"]


def test_unique_labels_have_no_duplicates():
    assert template_check.duplicate_labels(labels=["a", "b"]) == []


def write_repository(root, *, labels, bug):
    templates = root / ".github" / "ISSUE_TEMPLATE"
    templates.mkdir(parents=True)
    (templates / "config.yml").write_text("blank_issues_enabled: false\n", "utf-8")
    (templates / "bug.yml").write_text(json.dumps(bug), "utf-8")
    (root / ".github" / "labels.yml").write_text(
        json.dumps([{"name": name} for name in labels]), "utf-8"
    )
    translations = root / "custom_components" / "saj_local" / "translations"
    translations.mkdir(parents=True)
    options = {"automatic": "Automatic", "hs3": "HS3", "h2": "H2"}
    (translations / "en.json").write_text(
        json.dumps({"selector": {"model": {"options": options}}}), "utf-8"
    )


def test_main_succeeds_for_consistent_files(tmp_path, monkeypatch, capsys):
    write_repository(tmp_path, labels=LABELS, bug=bug_template())
    monkeypatch.chdir(tmp_path)

    assert template_check.main() == 0
    assert capsys.readouterr().out == ""


def test_main_reports_every_kind_of_finding_and_fails(tmp_path, monkeypatch, capsys):
    write_repository(
        tmp_path, labels=["fix", "fix"], bug=bug_template(labels=["ghost"])
    )
    monkeypatch.chdir(tmp_path)

    assert template_check.main() == 1
    assert capsys.readouterr().out == (
        "finding .github/labels.yml: the label fix is named twice\n"
        "finding bug.yml: the label ghost is not in .github/labels.yml\n"
    )


def test_main_reports_a_missing_bug_template(tmp_path, monkeypatch, capsys):
    write_repository(tmp_path, labels=LABELS, bug=bug_template())
    (tmp_path / ".github" / "ISSUE_TEMPLATE" / "bug.yml").unlink()
    monkeypatch.chdir(tmp_path)

    assert template_check.main() == 1
    assert capsys.readouterr().out == (
        "finding .github/ISSUE_TEMPLATE: bug.yml is missing\n"
    )


def test_running_the_check_as_a_script_exits_with_the_status_of_main(
    tmp_path, monkeypatch
):
    write_repository(tmp_path, labels=LABELS, bug=bug_template())
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("template_check", run_name="__main__")

    assert stopped.value.code == 0
