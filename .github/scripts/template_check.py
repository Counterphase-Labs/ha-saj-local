from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import unquote_plus

import yaml

TEMPLATES_DIRECTORY = Path(".github/ISSUE_TEMPLATE")
LABELS_FILE = Path(".github/labels.yml")
TRANSLATIONS_FILE = Path("custom_components/saj_local/translations/en.json")
BUG_TEMPLATE = "bug.yml"
CONFIG_TEMPLATE = "config.yml"
AUTOMATIC_MODEL = "automatic"
OTHER_OPTION = "Other"
SEARCH_LINK = re.compile(r"issues\?q=([^\s)\"']+)")
LABEL_TERM = re.compile(r'label:(?:"([^"]+)"|(\S+))')


def link_labels(*, text: str) -> list[str]:
    names: list[str] = []
    for link in SEARCH_LINK.findall(text):
        for quoted, bare in LABEL_TERM.findall(unquote_plus(link)):
            names.append(quoted or bare)
    return names


def duplicate_labels(*, labels: list[str]) -> list[str]:
    return [name for name, count in Counter(labels).items() if count > 1]


def _strings(node: Any) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [text for value in node.values() for text in _strings(value)]
    if isinstance(node, list):
        return [text for value in node for text in _strings(value)]
    return []


def _element(template: dict[str, Any], element_id: str) -> Any:
    return next(
        (
            element
            for element in template.get("body", [])
            if element.get("id") == element_id
        ),
        None,
    )


def _bug_findings(*, template: dict[str, Any], model_labels: list[str]) -> list[str]:
    findings: list[str] = []
    diagnostics = _element(template, "diagnostics")
    if (
        diagnostics is None
        or diagnostics.get("type") != "textarea"
        or diagnostics.get("validations", {}).get("required") is not True
    ):
        findings.append("the diagnostics field must be a required textarea")
    model = _element(template, "model")
    if model is None or model.get("type") != "dropdown":
        findings.append("the model dropdown is missing")
    else:
        options = model.get("attributes", {}).get("options", [])
        expected = [*model_labels, OTHER_OPTION]
        if options != expected:
            findings.append(
                f"the model options {options} differ from the translations {expected}"
            )
    return findings


def template_findings(
    *,
    template_name: str,
    template: dict[str, Any],
    label_names: list[str],
    model_labels: list[str],
) -> list[str]:
    findings = (
        _bug_findings(template=template, model_labels=model_labels)
        if template_name == BUG_TEMPLATE
        else []
    )
    for name in template.get("labels", []):
        if name not in label_names:
            findings.append(f"the label {name} is not in {LABELS_FILE}")
    for text in _strings(template):
        for name in link_labels(text=text):
            if name not in label_names:
                findings.append(f"the search link names {name}, not in {LABELS_FILE}")
    return findings


def main() -> int:
    labels = [entry["name"] for entry in yaml.safe_load(LABELS_FILE.read_text("utf-8"))]
    options = json.loads(TRANSLATIONS_FILE.read_text("utf-8"))["selector"]["model"][
        "options"
    ]
    model_labels = [label for key, label in options.items() if key != AUTOMATIC_MODEL]
    findings = [
        f"finding {LABELS_FILE}: the label {name} is named twice"
        for name in duplicate_labels(labels=labels)
    ]
    if not (TEMPLATES_DIRECTORY / BUG_TEMPLATE).is_file():
        findings.append(f"finding {TEMPLATES_DIRECTORY}: {BUG_TEMPLATE} is missing")
    for path in sorted(TEMPLATES_DIRECTORY.glob("*.yml")):
        if path.name == CONFIG_TEMPLATE:
            continue
        template = yaml.safe_load(path.read_text("utf-8"))
        findings.extend(
            f"finding {path.name}: {message}"
            for message in template_findings(
                template_name=path.name,
                template=template,
                label_names=labels,
                model_labels=model_labels,
            )
        )
    for finding in findings:
        sys.stdout.write(f"{finding}\n")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
