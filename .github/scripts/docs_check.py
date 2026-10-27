from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_PAGE_LINES = 300
COVERAGE_COLUMNS = 3
COVERAGE_HEADER = "Feature list"
SECTION_LEVEL = 2
DOCS_ROOT = Path("docs")
ENGLISH_CODE = "en-gb"
ENGLISH_TRANSLATION = "en"
IMAGES_DIRECTORY = DOCS_ROOT / "images"
NOT_LANGUAGES = (IMAGES_DIRECTORY.name,)
LIBRARY_DIRECTORY = Path("custom_components/saj_local")
TRANSLATIONS_DIRECTORY = LIBRARY_DIRECTORY / "translations"
TEXT_DIRECTORY = Path(".github/scripts/docs_text")
ENTITIES_PARTS = ("user", "entities")
COVERAGE_PAGE = DOCS_ROOT / ENGLISH_CODE / "developer" / "documentation.md"
ROOT_README = Path("README.md")
README_PARTS = 3  # docs/<code>/README.md
ROOT_DOCUMENTS = (ROOT_README, Path("CONTRIBUTING.md"), Path("SECURITY.md"))
AGENT_DIRECTORIES = (Path(), LIBRARY_DIRECTORY, Path("frontend"), Path("mock"))
INTEGRATION_FEATURES = LIBRARY_DIRECTORY / "docs" / "features.md"
FEATURE_LISTS = {
    "Integration": INTEGRATION_FEATURES,
    "Cards": Path("frontend/docs/features.md"),
    "Simulator": Path("mock/docs/features.md"),
}
ENTITY_PREFIX = "saj"
PREFIX_EXAMPLE = "house"
BINARY_SENSOR = "binary_sensor"
GRID_PREFIX = "grid_"
NO_VALUE = "-"
CONTROL_ALLOWED_KEY = "control_allowed"
POWER_NUMBER_UNIT = "W"
EQUIPMENT_AREAS = {
    "battery": "battery",
    "meter_a": "grid-and-meter-a",
    "meter_b": "meter-b",
    "ev_charger": "ev-charger",
    "parallel": "parallel-system",
}
LANGUAGE_BAR_FOLDERS = (
    ("en", ENGLISH_CODE),
    ("de", "de"),
    ("nl", "nl"),
    ("fr", "fr"),
    ("zh", "zh-hans"),
    ("es", "es"),
    ("it", "it"),
    ("pl", "pl"),
    ("sv", "sv"),
)
BAR_SEPARATOR = " | "
DEVICES_SECTION = "Devices and entities"
EQUIPMENT_SECTION = "Optional equipment"


@dataclass(frozen=True)
class Area:
    slug: str
    sections: tuple[str, ...]


AREAS = (
    Area("inverter-and-pv", (DEVICES_SECTION,)),
    Area("grid-and-meter-a", (DEVICES_SECTION, EQUIPMENT_SECTION)),
    Area("meter-b", (EQUIPMENT_SECTION,)),
    Area("battery", (EQUIPMENT_SECTION,)),
    Area("battery-packs", (EQUIPMENT_SECTION,)),
    Area("ev-charger", (EQUIPMENT_SECTION,)),
    Area("parallel-system", (EQUIPMENT_SECTION,)),
    Area("settings", ("Changing settings",)),
    Area("faults", ("Device faults and repairs",)),
    Area("added-by-the-integration", ("Changing settings", "Power control")),
)

LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_SPAN = re.compile(r"`[^`]*`")
EXTERNAL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
PAGE_NAME = re.compile(r"`([^`]+)`")
ANCHOR_CHARACTERS = re.compile(r"[^\w\s-]")
BAR_ITEM = r"\[?[a-z]{2}\]?(?:\([^)]*\))?"
BAR_LINE = re.compile(rf"^{BAR_ITEM}(?: \| {BAR_ITEM})*$")
Importer = Callable[[str], Any]


@dataclass(frozen=True)
class Link:
    path: str
    fragment: str


@dataclass(frozen=True)
class CoverageRow:
    feature_list: str
    sections: tuple[str, ...]
    pages: tuple[str, ...]


@dataclass(frozen=True)
class Variant:
    key: str
    kind: str
    unit: str | None
    equipment: str | None
    phases: int
    strings: int
    packs: int
    writable: bool
    catalogued: bool


@dataclass(frozen=True)
class Sighting:
    model: str
    variant: Variant
    enabled: bool


@dataclass(frozen=True)
class Entity:
    variant: Variant
    models: tuple[str, ...]
    enabled: tuple[str, ...]


def slug(text: str) -> str:
    return ANCHOR_CHARACTERS.sub("", text.lower()).strip().replace(" ", "-")


def relative_link(page: Path, target: Path) -> str:
    return Path(os.path.relpath(target, page.parent)).as_posix()


def is_readme(page: Path) -> bool:
    return page == ROOT_README or len(page.parts) == README_PARTS


def readme_of(folder: str) -> Path:
    return ROOT_README if folder == ENGLISH_CODE else DOCS_ROOT / folder / "README.md"


def language_bar(page: Path) -> str:
    code = ENGLISH_CODE if page == ROOT_README else page.parts[1]
    inside = Path(*page.parts[2:])
    return BAR_SEPARATOR.join(
        label
        if folder == code
        else "[{}]({})".format(
            label,
            relative_link(
                page,
                readme_of(folder) if is_readme(page) else DOCS_ROOT / folder / inside,
            ),
        )
        for label, folder in LANGUAGE_BAR_FOLDERS
    )


def with_language_bar(*, page: Path, text: str) -> str:
    first, _, rest = text.partition("\n")
    body = rest if BAR_LINE.match(first) else text
    return f"{language_bar(page)}\n\n{body.lstrip(chr(10))}"


def language_codes(root: Path) -> tuple[str, ...]:
    return tuple(
        sorted(
            folder.name
            for folder in (root / DOCS_ROOT).glob("*")
            if folder.is_dir() and folder.name not in NOT_LANGUAGES
        )
    )


def entities_directory(code: str) -> Path:
    return DOCS_ROOT / code / "user" / "entities"


def translation_file(root: Path, code: str) -> Path | None:
    stem = ENGLISH_TRANSLATION if code == ENGLISH_CODE else code
    for path in sorted((root / TRANSLATIONS_DIRECTORY).glob("*.json")):
        if path.stem.lower() == stem:
            return TRANSLATIONS_DIRECTORY / path.name
    return None


def text_file(code: str) -> Path:
    return TEXT_DIRECTORY / f"{code}.json"


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


def area_of(variant: Variant) -> str:
    if not variant.catalogued:
        return "added-by-the-integration"
    if variant.kind == BINARY_SENSOR:
        return "faults"
    if variant.packs:
        return "battery-packs"
    return EQUIPMENT_AREAS.get(variant.equipment or "") or _plain_area(variant)


def _plain_area(variant: Variant) -> str:
    if variant.writable:
        return "settings"
    if variant.key.startswith(GRID_PREFIX):
        return "grid-and-meter-a"
    return "inverter-and-pv"


def merge(sightings: Iterable[Sighting]) -> tuple[Entity, ...]:
    models: dict[Variant, list[str]] = {}
    enabled: dict[Variant, list[str]] = {}
    for sighting in sightings:
        models.setdefault(sighting.variant, []).append(sighting.model)
        enabled.setdefault(sighting.variant, [])
        if sighting.enabled:
            enabled[sighting.variant].append(sighting.model)
    return tuple(
        Entity(variant=variant, models=tuple(found), enabled=tuple(enabled[variant]))
        for variant, found in models.items()
    )


def catalogue_sightings(
    *, profiles: Iterable[Any], catalogue_of: Callable[..., Any]
) -> Iterable[Sighting]:
    for profile in profiles:
        for register in catalogue_of(profile=profile).registers:
            if register.exposed:
                yield Sighting(
                    model=profile.key,
                    variant=Variant(
                        key=register.key,
                        kind=_value(register.kind),
                        unit=None if register.unit is None else _value(register.unit),
                        equipment=_value(register.equipment)
                        if register.equipment is not None
                        else None,
                        phases=register.definition.phases,
                        strings=register.definition.strings,
                        packs=register.packs,
                        writable=register.writable,
                        catalogued=True,
                    ),
                    enabled=register.core,
                )


def _added(*, key: str, kind: str, unit: str | None, equipment: str | None) -> Variant:
    return Variant(
        key=key,
        kind=kind,
        unit=unit,
        equipment=equipment,
        phases=1,
        strings=1,
        packs=0,
        writable=False,
        catalogued=False,
    )


def added_sightings(
    *, profiles: Iterable[Any], function_equipment: dict[Any, Any]
) -> Iterable[Sighting]:
    for profile in profiles:
        yield Sighting(
            model=profile.key,
            variant=_added(
                key=CONTROL_ALLOWED_KEY,
                kind=BINARY_SENSOR,
                unit=None,
                equipment=None,
            ),
            enabled=True,
        )
        for function in profile.power_control:
            equipment = function_equipment.get(function)
            equipment_name = None if equipment is None else _value(equipment)
            yield Sighting(
                model=profile.key,
                variant=_added(
                    key=function.switch_key,
                    kind="switch",
                    unit=None,
                    equipment=equipment_name,
                ),
                enabled=False,
            )
            yield Sighting(
                model=profile.key,
                variant=_added(
                    key=function.target_key,
                    kind="number",
                    unit=POWER_NUMBER_UNIT,
                    equipment=equipment_name,
                ),
                enabled=False,
            )


def shipped_entities(*, import_module: Importer) -> tuple[Entity, ...]:
    catalogue_of = import_module("saj.catalogue").catalogue_of
    profiles = import_module("saj.profiles").PROFILES
    function_equipment = import_module("saj.power_control").FUNCTION_EQUIPMENT
    return merge(
        [
            *catalogue_sightings(profiles=profiles, catalogue_of=catalogue_of),
            *added_sightings(profiles=profiles, function_equipment=function_equipment),
        ]
    )


def _count_notes(variant: Variant, text: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    if variant.phases > 1:
        notes.append(text["phase_note"].format(n=variant.phases))
    if variant.strings > 1:
        notes.append(text["string_note"].format(n=variant.strings))
    if variant.packs > 1:
        notes.append(text["pack_note"].format(n=variant.packs))
    return notes


def _needs(
    *, variant: Variant, translations: dict[str, Any], text: dict[str, Any]
) -> str:
    names = translations["selector"]["equipment"]["options"]
    equipment = (
        []
        if variant.equipment is None
        else [names.get(variant.equipment, variant.equipment)]
    )
    return "; ".join([*equipment, *_count_notes(variant, text)]) or NO_VALUE


def _enabled_by_default(*, entity: Entity, text: dict[str, Any]) -> str:
    if entity.enabled == entity.models:
        return str(text["yes"])
    if not entity.enabled:
        return str(text["no"])
    return str(
        text["only"].format(models=", ".join(model.upper() for model in entity.enabled))
    )


def entity_name(*, translations: dict[str, Any], variant: Variant) -> str | None:
    definition = translations["entity"].get(variant.kind, {}).get(variant.key)
    return None if definition is None else definition["name"]


def _row(*, entity: Entity, translations: dict[str, Any], text: dict[str, Any]) -> str:
    variant = entity.variant
    name = entity_name(translations=translations, variant=variant) or variant.key
    cells = (
        name,
        f"`{variant.kind}.{ENTITY_PREFIX}_{variant.key}`",
        text["kinds"][variant.kind],
        variant.unit or NO_VALUE,
        ", ".join(model.upper() for model in entity.models),
        _needs(variant=variant, translations=translations, text=text),
        _enabled_by_default(entity=entity, text=text),
    )
    return _table_row(cells)


def _table_row(cells: Iterable[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _table_head(header: Sequence[str]) -> list[str]:
    return [_table_row(header), _table_row("---" for _ in header)]


def _section_links(*, area: Area, page: Path, text: dict[str, Any]) -> str:
    feature_link = relative_link(page, INTEGRATION_FEATURES)
    return str(text["link_join"]).join(
        f"[{text['sections'][section]}]({feature_link}#{slug(section)})"
        for section in area.sections
    )


def _prefix_lines(
    *, title: str, entities: Sequence[Entity], text: dict[str, Any]
) -> list[str]:
    if not entities:
        return []
    first = entities[0].variant
    example = f"{first.kind}.{ENTITY_PREFIX}_{PREFIX_EXAMPLE}_{first.key}"
    note = text["prefix_note"].format(
        entity_prefix=ENTITY_PREFIX, title=title, example=example, prefix=PREFIX_EXAMPLE
    )
    return [note, ""]


def render_area(
    *,
    code: str,
    area: Area,
    entities: Sequence[Entity],
    translations: dict[str, Any],
    text: dict[str, Any],
) -> str:
    page = entities_directory(code) / f"{area.slug}.md"
    title = text["areas"][area.slug]["title"]
    links = _section_links(area=area, page=page, text=text)
    lines = [
        f"# {title}",
        "",
        text["summary_line"].format(summary=text["areas"][area.slug]["summary"]),
        "",
        text["area_intro"].format(title=title, links=links),
        "",
        text["count_line"].format(count=len(entities), notice=text["generated_notice"]),
        "",
        *_prefix_lines(title=title, entities=entities, text=text),
        *_table_head(text["area_header"]),
        *(
            _row(entity=entity, translations=translations, text=text)
            for entity in entities
        ),
        "",
    ]
    return "\n".join(lines)


def render_index(
    *, code: str, grouped: dict[str, list[Entity]], text: dict[str, Any]
) -> str:
    index = entities_directory(code) / "README.md"
    feature_link = relative_link(index, INTEGRATION_FEATURES)
    lines = [
        f"# {text['index_title']}",
        "",
        text["index_intro"].format(
            section=text["sections"][DEVICES_SECTION],
            link=f"{feature_link}#{slug(DEVICES_SECTION)}",
        ),
        "",
        text["index_fit"],
        "",
        text["generated_notice"],
        "",
        *_table_head(text["index_header"]),
        *(
            _table_row(
                (
                    f"[{text['areas'][area.slug]['title']}]({area.slug}.md)",
                    str(len(grouped[area.slug])),
                    text["areas"][area.slug]["summary"],
                )
            )
            for area in AREAS
        ),
        "",
    ]
    return "\n".join(lines)


def generated_pages(
    *,
    code: str,
    entities: Sequence[Entity],
    translations: dict[str, Any],
    text: dict[str, Any],
) -> dict[Path, str]:
    grouped: dict[str, list[Entity]] = {area.slug: [] for area in AREAS}
    for entity in entities:
        grouped[area_of(entity.variant)].append(entity)
    pages = {
        entities_directory(code) / f"{area.slug}.md": render_area(
            code=code,
            area=area,
            entities=grouped[area.slug],
            translations=translations,
            text=text,
        )
        for area in AREAS
    }
    pages[entities_directory(code) / "README.md"] = render_index(
        code=code, grouped=grouped, text=text
    )
    return {
        page: with_language_bar(page=page, text=content)
        for page, content in pages.items()
    }


def _missing_inputs(*, root: Path, code: str, source: Path | None) -> list[str]:
    findings: list[str] = []
    if source is None:
        findings.append(
            f"{DOCS_ROOT.as_posix()}/{code}: no translation file for the language "
            f"in {TRANSLATIONS_DIRECTORY.as_posix()}"
        )
    if not (root / text_file(code)).is_file():
        findings.append(
            f"{text_file(code).as_posix()}: missing, the generator needs the "
            f"texts of {code}"
        )
    return findings


def language_generation(
    *, root: Path, code: str, entities: Sequence[Entity]
) -> tuple[dict[Path, str], list[str]]:
    source = translation_file(root, code)
    missing = _missing_inputs(root=root, code=code, source=source)
    if source is None or missing:
        return {}, missing
    translations = json.loads((root / source).read_text(encoding="utf-8"))
    text = json.loads((root / text_file(code)).read_text(encoding="utf-8"))
    pages = generated_pages(
        code=code, entities=entities, translations=translations, text=text
    )
    return pages, missing_entity_findings(
        file=source, entities=entities, translations=translations
    )


def all_generation(
    *, root: Path, entities: Sequence[Entity]
) -> tuple[dict[Path, str], list[str]]:
    pages: dict[Path, str] = {}
    findings: list[str] = []
    for code in language_codes(root):
        language_pages, language_findings = language_generation(
            root=root, code=code, entities=entities
        )
        pages.update(language_pages)
        findings.extend(language_findings)
    return pages, findings


def stale_findings(*, root: Path, pages: dict[Path, str]) -> list[str]:
    findings: list[str] = []
    for path, text in pages.items():
        target = root / path
        if not target.is_file() or target.read_text(encoding="utf-8") != text:
            findings.append(f"{path.as_posix()}: stale, run make docs")
    return findings


def missing_entity_findings(
    *, file: Path, entities: Sequence[Entity], translations: dict[str, Any]
) -> list[str]:
    listed = {(entity.variant.kind, entity.variant.key) for entity in entities}
    findings = [
        f"{file.as_posix()}: entity {kind}.{key} is on no area page"
        for kind, definitions in translations["entity"].items()
        for key in definitions
        if (kind, key) not in listed
    ]
    findings.extend(
        f"{file.as_posix()}: entity {entity.variant.kind}."
        f"{entity.variant.key} has no name"
        for entity in entities
        if entity_name(translations=translations, variant=entity.variant) is None
    )
    return findings


def write_generated(*, root: Path, pages: dict[Path, str]) -> None:
    for path, text in pages.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")


def language_pages(root: Path) -> tuple[Path, ...]:
    return (
        *((ROOT_README,) if (root / ROOT_README).is_file() else ()),
        *(
            page.relative_to(root)
            for code in language_codes(root)
            for page in sorted((root / DOCS_ROOT / code).rglob("*.md"))
        ),
    )


def readme_findings(root: Path) -> list[str]:
    return [
        f"{readme_of(folder).as_posix()}: translated README is missing"
        for _, folder in LANGUAGE_BAR_FOLDERS
        if folder != ENGLISH_CODE and not (root / readme_of(folder)).is_file()
    ]


def write_language_bars(root: Path) -> None:
    for page in language_pages(root):
        text = (root / page).read_text(encoding="utf-8")
        barred = with_language_bar(page=page, text=text)
        if barred != text:
            (root / page).write_text(barred, encoding="utf-8")


def bar_findings(root: Path) -> list[str]:
    return [
        f"{page.as_posix()}: first line is not the language bar, run make docs"
        for page in language_pages(root)
        if (root / page).read_text(encoding="utf-8").split("\n", 1)[0]
        != language_bar(page)
    ]


def _outside_fences(text: str) -> list[str]:
    lines: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            lines.append(line)
    return lines


def headings(text: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for line in _outside_fences(text):
        match = HEADING.match(line)
        if match:
            found.append((len(match.group(1)), match.group(2)))
    return found


def anchors(text: str) -> set[str]:
    seen: dict[str, int] = {}
    result: set[str] = set()
    for _, title in headings(text):
        base = slug(title)
        count = seen.get(base, 0)
        result.add(base if count == 0 else f"{base}-{count}")
        seen[base] = count + 1
    return result


def links(*, root: Path, document: Path) -> tuple[Link, ...]:
    text = (root / document).read_text(encoding="utf-8")
    found: list[Link] = []
    for line in _outside_fences(text):
        for match in LINK.finditer(CODE_SPAN.sub("", line)):
            target = match.group(1)
            if EXTERNAL.match(target):
                continue
            path, _, fragment = target.partition("#")
            resolved = (
                Path(os.path.normpath(document.parent / path)) if path else document
            )
            found.append(Link(resolved.as_posix(), fragment))
    return tuple(found)


def documents(root: Path) -> tuple[Path, ...]:
    pages = sorted(
        page
        for code in language_codes(root)
        for page in (root / DOCS_ROOT / code).rglob("*.md")
    )
    present = [
        path
        for path in (
            *ROOT_DOCUMENTS,
            *(directory / "AGENTS.md" for directory in AGENT_DIRECTORIES),
        )
        if (root / path).is_file()
    ]
    return (*present, *(page.relative_to(root) for page in pages))


def _link_findings(*, root: Path, document: Path) -> list[str]:
    findings: list[str] = []
    for link in links(root=root, document=document):
        target = root / link.path
        if not target.exists():
            findings.append(f"{document.as_posix()}: missing target {link.path}")
        elif link.fragment and target.suffix == ".md":
            text = target.read_text(encoding="utf-8")
            if link.fragment not in anchors(text):
                findings.append(
                    f"{document.as_posix()}: missing anchor {link.path}#{link.fragment}"
                )
    return findings


def link_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for document in documents(root):
        findings.extend(_link_findings(root=root, document=document))
    return findings


def _linked_paths(*, root: Path, pages: Iterable[Path]) -> set[str]:
    return {link.path for page in pages for link in links(root=root, document=page)}


def orphan_findings(root: Path) -> list[str]:
    referenced = {
        code: _linked_paths(
            root=root,
            pages=(
                document
                for document in documents(root)
                if document.is_relative_to(DOCS_ROOT / code)
            ),
        )
        for code in language_codes(root)
    }
    return [
        f"{path.relative_to(root).as_posix()}: image is referenced by no page of "
        "its language"
        for path in sorted((root / IMAGES_DIRECTORY).rglob("*"))
        if path.is_file()
        and path.relative_to(root).as_posix()
        not in referenced.get(path.relative_to(root / IMAGES_DIRECTORY).parts[0], ())
    ]


def length_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for document in documents(root):
        if (
            not document.is_relative_to(DOCS_ROOT)
            or document.parts[2:4] == ENTITIES_PARTS
        ):
            continue
        count = len((root / document).read_text(encoding="utf-8").splitlines())
        if count > MAX_PAGE_LINES:
            findings.append(
                f"{document.as_posix()}: {count} lines, limit is {MAX_PAGE_LINES}"
            )
    return findings


def coverage_rows(text: str) -> tuple[CoverageRow, ...]:
    rows: list[CoverageRow] = []
    inside = False
    for line in _outside_fences(text):
        if not line.lstrip().startswith("|"):
            inside = False
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == COVERAGE_HEADER:
            inside = True
        elif inside and len(cells) == COVERAGE_COLUMNS and set(cells[0]) - {"-", " "}:
            rows.append(
                CoverageRow(
                    cells[0],
                    tuple(section.strip() for section in cells[1].split(",")),
                    tuple(PAGE_NAME.findall(cells[2])),
                )
            )
    return tuple(rows)


def _feature_sections(*, root: Path, feature_list: Path) -> list[str]:
    text = (root / feature_list).read_text(encoding="utf-8")
    return [title for level, title in headings(text) if level == SECTION_LEVEL]


def _row_findings(*, root: Path, row: CoverageRow) -> list[str]:
    feature_list = FEATURE_LISTS.get(row.feature_list)
    if feature_list is None:
        return [f"{COVERAGE_PAGE.as_posix()}: unknown feature list {row.feature_list}"]
    known = _feature_sections(root=root, feature_list=feature_list)
    findings = [
        f"{COVERAGE_PAGE.as_posix()}: {row.feature_list} has no section {section}"
        for section in row.sections
        if section not in known
    ]
    for code in language_codes(root):
        for page in row.pages:
            findings.extend(
                _page_findings(
                    root=root, row=row, feature_list=feature_list, page=(code, page)
                )
            )
    return findings


def _page_findings(
    *, root: Path, row: CoverageRow, feature_list: Path, page: tuple[str, str]
) -> list[str]:
    path = DOCS_ROOT / page[0] / page[1]
    if not (root / path).is_file():
        return [
            f"{path.as_posix()}: page named in the Feature Coverage Table is missing"
        ]
    present = {(link.path, link.fragment) for link in links(root=root, document=path)}
    return [
        f"{path.as_posix()}: no link to {row.feature_list} section {section} "
        f"({feature_list.as_posix()}#{slug(section)})"
        for section in row.sections
        if (feature_list.as_posix(), slug(section)) not in present
    ]


def coverage_findings(root: Path) -> list[str]:
    coverage_page = root / COVERAGE_PAGE
    if not coverage_page.is_file():
        return [f"{COVERAGE_PAGE.as_posix()}: Feature Coverage Table page is missing"]
    rows = coverage_rows(coverage_page.read_text(encoding="utf-8"))
    findings: list[str] = []
    for row in rows:
        findings.extend(_row_findings(root=root, row=row))
    covered = {(row.feature_list, section) for row in rows for section in row.sections}
    for name, feature_list in FEATURE_LISTS.items():
        findings.extend(
            f"{feature_list.as_posix()}: section {section} has no row in "
            f"{COVERAGE_PAGE.as_posix()}"
            for section in _feature_sections(root=root, feature_list=feature_list)
            if (name, section) not in covered
        )
    return findings


def check(*, root: Path, entities: Sequence[Entity]) -> list[str]:
    pages, findings = all_generation(root=root, entities=entities)
    return [
        *stale_findings(root=root, pages=pages),
        *findings,
        *readme_findings(root),
        *bar_findings(root),
        *link_findings(root),
        *orphan_findings(root),
        *length_findings(root),
        *coverage_findings(root),
    ]


def main(
    argv: Sequence[str],
    *,
    root: Path | None = None,
    import_module: Importer = importlib.import_module,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    options = parser.parse_args(argv)
    base = Path.cwd() if root is None else root
    sys.path.insert(0, str(base / LIBRARY_DIRECTORY))
    entities = shipped_entities(import_module=import_module)
    if options.write:
        pages, findings = all_generation(root=base, entities=entities)
        write_generated(root=base, pages=pages)
        write_language_bars(base)
    else:
        findings = check(root=base, entities=entities)
    for finding in findings:
        sys.stdout.write(f"finding {finding}\n")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
