from __future__ import annotations

import importlib
import json
import runpy
import sys
from enum import StrEnum
from pathlib import Path
from types import SimpleNamespace

import docs_check
import pytest
from docs_check import Entity, Sighting, Variant


class Kind(StrEnum):
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    NUMBER = "number"
    SWITCH = "switch"


class Function(StrEnum):
    BATTERY = "battery"
    GRID = "grid"

    @property
    def switch_key(self) -> str:
        return f"{self.value}_power_control"

    @property
    def target_key(self) -> str:
        return f"{self.value}_power_target"


def variant(**changes) -> Variant:
    fields = {
        "key": "pv_power",
        "kind": "sensor",
        "unit": "W",
        "equipment": None,
        "phases": 1,
        "strings": 1,
        "packs": 0,
        "writable": False,
        "catalogued": True,
    }
    return Variant(**{**fields, **changes})


def entity(*, models=("hs3", "h2"), enabled=("hs3", "h2"), **changes) -> Entity:
    return Entity(variant=variant(**changes), models=models, enabled=enabled)


def register(*, key="pv_power", kind=Kind.SENSOR, **changes):
    fields = {
        "key": key,
        "kind": kind,
        "unit": None,
        "equipment": None,
        "definition": SimpleNamespace(phases=1, strings=1),
        "packs": 0,
        "writable": False,
        "exposed": True,
        "core": True,
    }
    return SimpleNamespace(**{**fields, **changes})


def catalogue_returning(*registers):
    def catalogue_of(*, profile):
        del profile
        return SimpleNamespace(registers=registers)

    return catalogue_of


def translations(**names) -> dict:
    entities: dict = {}
    for dotted, name in names.items():
        kind, key = dotted.split("__", 1)
        entities.setdefault(kind, {})[key] = {"name": name}
    return {"entity": entities}


@pytest.mark.parametrize(
    ("changes", "area"),
    [
        ({"catalogued": False}, "added-by-the-integration"),
        ({"kind": "binary_sensor", "equipment": "battery"}, "faults"),
        ({"packs": 2, "equipment": "battery"}, "battery-packs"),
        ({"equipment": "battery"}, "battery"),
        ({"equipment": "meter_a"}, "grid-and-meter-a"),
        ({"equipment": "meter_b", "writable": True}, "meter-b"),
        ({"equipment": "ev_charger"}, "ev-charger"),
        ({"equipment": "parallel"}, "parallel-system"),
        ({"writable": True, "key": "grid_export_limit"}, "settings"),
        ({"key": "grid_power"}, "grid-and-meter-a"),
        ({}, "inverter-and-pv"),
    ],
)
def test_an_entity_lands_on_the_first_area_it_belongs_to(changes, area):
    assert docs_check.area_of(variant(**changes)) == area


def test_every_area_has_a_page_and_an_index_row():
    pages = docs_check.generated_pages(entities=(), translations=translations())

    paths = {path.name for path in pages}
    assert paths == {f"{area.slug}.md" for area in docs_check.AREAS} | {"README.md"}


def test_the_same_entity_on_two_models_is_one_row_listing_both_models():
    merged = docs_check.merge(
        [
            Sighting(model="hs3", variant=variant(), enabled=True),
            Sighting(model="h2", variant=variant(), enabled=False),
            Sighting(model="h2", variant=variant(key="other"), enabled=True),
        ]
    )

    assert merged == (
        Entity(variant=variant(), models=("hs3", "h2"), enabled=("hs3",)),
        Entity(variant=variant(key="other"), models=("h2",), enabled=("h2",)),
    )


def test_the_same_key_with_a_different_unit_stays_two_rows():
    merged = docs_check.merge(
        [
            Sighting(model="hs3", variant=variant(unit="W"), enabled=True),
            Sighting(model="h2", variant=variant(unit="kW"), enabled=True),
        ]
    )

    assert [found.models for found in merged] == [("hs3",), ("h2",)]


def test_catalogue_sightings_read_each_exposed_register_of_each_profile():
    registers = (
        register(
            key="battery_power",
            kind=Kind.SENSOR,
            unit=SimpleNamespace(value="W"),
            equipment=SimpleNamespace(value="battery"),
            definition=SimpleNamespace(phases=3, strings=2),
            packs=4,
            writable=True,
            core=False,
        ),
        register(key="hidden", exposed=False),
        register(key="plain"),
    )
    profile = SimpleNamespace(key="hs3")

    def catalogue_of(*, profile):
        del profile
        return SimpleNamespace(registers=registers)

    found = list(
        docs_check.catalogue_sightings(profiles=[profile], catalogue_of=catalogue_of)
    )

    assert found == [
        Sighting(
            model="hs3",
            variant=variant(
                key="battery_power",
                unit="W",
                equipment="battery",
                phases=3,
                strings=2,
                packs=4,
                writable=True,
            ),
            enabled=False,
        ),
        Sighting(model="hs3", variant=variant(key="plain", unit=None), enabled=True),
    ]


def test_added_sightings_name_control_allowed_and_each_power_control_function():
    profile = SimpleNamespace(
        key="hs3", power_control={Function.BATTERY: object(), Function.GRID: object()}
    )

    found = list(
        docs_check.added_sightings(
            profiles=[profile],
            function_equipment={Function.GRID: SimpleNamespace(value="meter_a")},
        )
    )

    summary = [
        (s.variant.kind, s.variant.key, s.variant.unit, s.variant.equipment, s.enabled)
        for s in found
    ]
    assert summary == [
        ("binary_sensor", "control_allowed", None, None, True),
        ("switch", "battery_power_control", None, None, False),
        ("number", "battery_power_target", "W", None, False),
        ("switch", "grid_power_control", None, "meter_a", False),
        ("number", "grid_power_target", "W", "meter_a", False),
    ]
    assert not any(s.variant.catalogued for s in found)


def test_shipped_entities_combine_the_catalogue_and_the_added_entities():
    profile = SimpleNamespace(key="h2", power_control={Function.BATTERY: object()})
    modules = {
        "saj.catalogue": SimpleNamespace(catalogue_of=catalogue_returning(register())),
        "saj.profiles": SimpleNamespace(PROFILES=(profile,)),
        "saj.power_control": SimpleNamespace(FUNCTION_EQUIPMENT={}),
    }

    keys = [
        found.variant.key
        for found in docs_check.shipped_entities(import_module=modules.get)
    ]

    assert keys == [
        "pv_power",
        "control_allowed",
        "battery_power_control",
        "battery_power_target",
    ]


def test_a_row_shows_name_id_type_unit_models_needs_and_default():
    page = docs_check.render_area(
        area=docs_check.AREAS[3],
        entities=[
            entity(
                key="battery_power",
                equipment="battery",
                strings=3,
                phases=2,
                packs=2,
                enabled=("h2",),
            ),
            entity(key="unknown", kind="binary_sensor", unit=None, enabled=()),
        ],
        translations=translations(sensor__battery_power="Battery power"),
    )

    assert (
        "| Battery power | `sensor.saj_battery_power` | Sensor | W | HS3, H2 | "
        "Battery; Phase 2 and above; PV string 3 and above; Battery pack 2 and above"
        " | H2 only |" in page
    )
    unknown_row = (
        "| unknown | `binary_sensor.saj_unknown` | Binary sensor | - | HS3, H2 | - "
        "| No |"
    )
    assert unknown_row in page


def test_an_unlisted_equipment_is_shown_by_its_own_name():
    page = docs_check.render_area(
        area=docs_check.AREAS[0],
        entities=[entity(equipment="heat_pump")],
        translations=translations(),
    )

    assert "| heat_pump | Yes |" in page


def test_an_area_page_links_its_feature_list_sections_and_explains_the_prefix():
    page = docs_check.render_area(
        area=docs_check.AREAS[-1], entities=[], translations=translations()
    )

    assert page.splitlines()[0] == "# Added by the integration"
    assert (
        "[Changing settings](../../../../custom_components/saj_local/docs/features.md"
        "#changing-settings) and [Power control]" in page
    )
    assert "A prefix set in Configure" not in page
    assert docs_check.GENERATED_NOTICE in page


def test_the_prefix_example_is_built_from_the_first_row_of_the_area():
    page = docs_check.render_area(
        area=docs_check.AREAS[-1],
        entities=[entity(key="control_allowed", kind="binary_sensor"), entity()],
        translations=translations(),
    )

    assert (
        "for example `binary_sensor.saj_house_control_allowed` with the prefix "
        "`house`." in page
    )


def test_the_index_counts_the_entities_of_each_area_and_links_the_page():
    pages = docs_check.generated_pages(
        entities=[entity(), entity(key="battery_power", equipment="battery")],
        translations=translations(),
    )

    index = pages[docs_check.ENTITIES_INDEX]
    assert "| [Inverter and PV](inverter-and-pv.md) | 1 |" in index
    assert "| [Battery](battery.md) | 1 |" in index
    assert "| [Faults](faults.md) | 0 |" in index


def test_a_translated_entity_with_no_catalogue_row_is_reported_missing():
    findings = docs_check.missing_entity_findings(
        entities=[entity()],
        translations=translations(sensor__pv_power="PV power", sensor__orphan="Orphan"),
    )

    assert findings == [
        (
            f"{docs_check.TRANSLATIONS_FILE.as_posix()}: entity sensor.orphan is on "
            "no area page"
        )
    ]


def test_an_entity_with_no_translated_name_is_reported():
    findings = docs_check.missing_entity_findings(
        entities=[entity(), entity(key="nameless", kind="number")],
        translations=translations(sensor__pv_power="PV power"),
    )

    assert findings == [
        f"{docs_check.TRANSLATIONS_FILE.as_posix()}: entity number.nameless has no name"
    ]


def test_a_missing_or_changed_generated_page_is_stale_and_a_current_one_is_not(
    tmp_path,
):
    current = Path("current.md")
    changed = Path("changed.md")
    (tmp_path / current).write_text("same", encoding="utf-8")
    (tmp_path / changed).write_text("old", encoding="utf-8")

    findings = docs_check.stale_findings(
        root=tmp_path,
        pages={
            current: "same",
            changed: "new",
            Path("absent.md"): "text",
        },
    )

    assert findings == [
        "changed.md: stale, run make docs",
        "absent.md: stale, run make docs",
    ]


def test_writing_the_generated_pages_creates_folders_and_makes_them_current(tmp_path):
    pages = {Path("a/b/page.md"): "text"}

    docs_check.write_generated(root=tmp_path, pages=pages)

    assert docs_check.stale_findings(root=tmp_path, pages=pages) == []


FEATURE_LIST = "# Features\n\n## Alpha\n\ntext\n\n## Beta\n\ntext\n"
TABLE_HEADER = "| Feature list | Section | Pages |\n| --- | --- | --- |\n"


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    for path in docs_check.FEATURE_LISTS.values():
        write(tmp_path, path.as_posix(), FEATURE_LIST)
    return tmp_path


def feature_link(page: str, section: str, list_name: str = "Integration") -> str:
    target = docs_check.FEATURE_LISTS[list_name]
    relative = docs_check.relative_link(Path("docs/en-gb") / page, target)
    return f"[{section}]({relative}#{docs_check.slug(section)})"


def cover(tree: Path, rows: str) -> None:
    write(tree, docs_check.COVERAGE_PAGE.as_posix(), TABLE_HEADER + rows)


def test_the_anchor_of_a_heading_follows_github_and_numbers_repeats():
    text = "# A\n\n## What's new?\n\n## Same\n\n## Same\n\n```\n## Fenced\n```\n"

    assert docs_check.anchors(text) == {"a", "whats-new", "same", "same-1"}


def test_a_link_to_a_missing_file_or_heading_is_reported_and_valid_ones_are_not(
    tree,
):
    write(tree, "docs/en-gb/user/real.md", "# Real\n")
    write(
        tree,
        "docs/en-gb/user/page.md",
        "# Page\n\n[ok](real.md#real) [self](#page) [web](https://example.com/x)\n"
        "[file](gone.md) [anchor](real.md#gone) `[code](skipped.md)`\n"
        "```\n[fenced](skipped.md)\n```\n",
    )

    assert docs_check.link_findings(tree) == [
        "docs/en-gb/user/page.md: missing target docs/en-gb/user/gone.md",
        "docs/en-gb/user/page.md: missing anchor docs/en-gb/user/real.md#gone",
    ]


def test_the_readme_the_contributing_guide_and_each_agents_file_are_checked(tree):
    for path in ("README.md", "CONTRIBUTING.md", "AGENTS.md", "mock/AGENTS.md"):
        write(tree, path, "[gone](nowhere.md)\n")

    findings = docs_check.link_findings(tree)

    assert [finding.split(":")[0] for finding in findings] == [
        "README.md",
        "CONTRIBUTING.md",
        "AGENTS.md",
        "mock/AGENTS.md",
    ]


def test_an_image_no_document_references_is_reported_and_a_used_one_is_not(tree):
    write(tree, "docs/images/en-gb/used.png", "x")
    write(tree, "docs/images/en-gb/unused.png", "x")
    write(tree, "docs/en-gb/user/page.md", "![shot](../../images/en-gb/used.png)\n")

    assert docs_check.orphan_findings(tree) == [
        "docs/images/en-gb/unused.png: image is referenced by no document"
    ]


def test_there_is_no_orphan_finding_before_any_image_exists(tree):
    assert docs_check.orphan_findings(tree) == []


def test_a_written_page_over_the_limit_is_reported_and_generated_pages_are_exempt(
    tree,
):
    long_text = "line\n" * (docs_check.MAX_PAGE_LINES + 1)
    write(tree, "docs/en-gb/user/long.md", long_text)
    write(tree, "docs/en-gb/user/fits.md", "line\n" * docs_check.MAX_PAGE_LINES)
    write(tree, "docs/en-gb/user/entities/battery.md", long_text)

    assert docs_check.length_findings(tree) == [
        (
            f"docs/en-gb/user/long.md: {docs_check.MAX_PAGE_LINES + 1} lines, "
            f"limit is {docs_check.MAX_PAGE_LINES}"
        )
    ]


def test_a_page_outside_the_docs_folder_may_be_long(tree):
    write(tree, "README.md", "line\n" * (docs_check.MAX_PAGE_LINES + 1))

    assert docs_check.length_findings(tree) == []


def test_the_coverage_table_is_read_as_feature_list_sections_and_pages():
    rows = docs_check.coverage_rows(
        TABLE_HEADER
        + "| Cards | Power flow card, Status card | [`user/a.md`](../user/a.md), "
        "`user/b.md` |\n"
        "```\n| Cards | Fenced | `x.md` |\n```\n"
        "| not | a table row |\n"
        "\n| Source | Code | Entities |\n| --- | --- | --- |\n"
        "| Elsewhere | `code.py` | Other |\n"
    )

    assert rows == (
        docs_check.CoverageRow(
            "Cards", ("Power flow card", "Status card"), ("user/a.md", "user/b.md")
        ),
    )


def test_a_feature_list_section_with_no_row_is_reported(tree):
    write(tree, "docs/en-gb/user/a.md", feature_link("user/a.md", "Alpha") + "\n")
    cover(tree, "| Integration | Alpha | `user/a.md` |\n")

    findings = docs_check.coverage_findings(tree)

    uncovered = {
        "custom_components/saj_local/docs/features.md": ("Beta",),
        "frontend/docs/features.md": ("Alpha", "Beta"),
        "mock/docs/features.md": ("Alpha", "Beta"),
    }
    assert findings == [
        f"{path}: section {section} has no row in {docs_check.COVERAGE_PAGE.as_posix()}"
        for path, sections in uncovered.items()
        for section in sections
    ]


def covered_everywhere(tree: Path, page_text: str) -> None:
    write(tree, "docs/en-gb/user/a.md", page_text)
    cover(
        tree,
        "".join(
            f"| {name} | Alpha, Beta | `user/a.md` |\n"
            for name in docs_check.FEATURE_LISTS
        ),
    )


def test_a_named_page_must_link_to_each_section_of_its_row(tree):
    covered_everywhere(tree, feature_link("user/a.md", "Alpha") + "\n")

    findings = docs_check.coverage_findings(tree)

    missing = {
        f"docs/en-gb/user/a.md: no link to {name} section {section} "
        f"({docs_check.FEATURE_LISTS[name].as_posix()}#{section.lower()})"
        for name, section in (
            ("Integration", "Beta"),
            ("Cards", "Alpha"),
            ("Cards", "Beta"),
            ("Simulator", "Alpha"),
            ("Simulator", "Beta"),
        )
    }
    assert set(findings) == missing


def test_a_page_linking_every_section_of_its_rows_passes(tree):
    links = " ".join(
        feature_link("user/a.md", section, name)
        for name in docs_check.FEATURE_LISTS
        for section in ("Alpha", "Beta")
    )
    covered_everywhere(tree, links + "\n")

    assert docs_check.coverage_findings(tree) == []


def test_a_row_naming_an_unknown_list_section_or_page_is_reported(tree):
    cover(
        tree,
        "| Nowhere | Alpha | `user/a.md` |\n| Cards | Gamma | `user/missing.md` |\n",
    )

    findings = docs_check.coverage_findings(tree)

    assert (
        "docs/en-gb/developer/documentation.md: unknown feature list Nowhere"
        in findings
    )
    assert (
        "docs/en-gb/developer/documentation.md: Cards has no section Gamma" in findings
    )
    assert (
        "docs/en-gb/user/missing.md: page named in the Feature Coverage Table is "
        "missing" in findings
    )


def test_a_missing_coverage_page_is_reported(tree):
    assert docs_check.coverage_findings(tree) == [
        "docs/en-gb/developer/documentation.md: Feature Coverage Table page is missing"
    ]


def minimal_modules():
    profile = SimpleNamespace(key="hs3", power_control={})
    return {
        "saj.catalogue": SimpleNamespace(
            catalogue_of=catalogue_returning(register(key="pv_power"))
        ),
        "saj.profiles": SimpleNamespace(PROFILES=(profile,)),
        "saj.power_control": SimpleNamespace(FUNCTION_EQUIPMENT={}),
    }


AREA_SECTIONS = sorted(
    {section for area in docs_check.AREAS for section in area.sections}
)


def finished_tree(tree: Path) -> Path:
    names = {
        "sensor": {"pv_power": {"name": "PV power"}},
        "binary_sensor": {"control_allowed": {"name": "Control allowed"}},
    }
    write(
        tree,
        docs_check.TRANSLATIONS_FILE.as_posix(),
        json.dumps({"entity": names}),
    )
    write(
        tree,
        docs_check.INTEGRATION_FEATURES.as_posix(),
        "".join(f"## {section}\n\n" for section in ("Alpha", *AREA_SECTIONS)),
    )
    sections = ("Alpha", *AREA_SECTIONS)
    write(
        tree,
        "docs/en-gb/user/a.md",
        " ".join(feature_link("user/a.md", section) for section in sections)
        + " "
        + " ".join(
            feature_link("user/a.md", section, name)
            for name in ("Cards", "Simulator")
            for section in ("Alpha", "Beta")
        )
        + "\n",
    )
    cover(
        tree,
        f"| Integration | {', '.join(sections)} | `user/a.md` |\n"
        "| Cards | Alpha, Beta | `user/a.md` |\n"
        "| Simulator | Alpha, Beta | `user/a.md` |\n",
    )
    return tree


def test_the_write_option_regenerates_pages_the_check_then_accepts(
    tree, monkeypatch, capsys
):
    finished_tree(tree)
    monkeypatch.setattr(sys, "path", list(sys.path))
    modules = minimal_modules()

    assert docs_check.main(["--write"], root=tree, import_module=modules.get) == 0
    assert docs_check.main([], root=tree, import_module=modules.get) == 0
    assert capsys.readouterr().out == ""


def test_the_check_prints_each_finding_and_fails(tree, monkeypatch, capsys):
    finished_tree(tree)
    monkeypatch.setattr(sys, "path", list(sys.path))

    status = docs_check.main([], root=tree, import_module=minimal_modules().get)

    assert status == 1
    assert "finding docs/en-gb/user/entities/README.md: stale, run make docs\n" in (
        capsys.readouterr().out
    )


def test_running_the_check_as_a_script_exits_with_the_status_of_main(tree, monkeypatch):
    finished_tree(tree)
    modules = minimal_modules()
    monkeypatch.chdir(tree)
    monkeypatch.setattr(sys, "argv", ["docs_check.py", "--write"])
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(importlib, "import_module", modules.get)

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("docs_check", run_name="__main__")

    assert stopped.value.code == 0
