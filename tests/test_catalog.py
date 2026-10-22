import copy
import json
import re

import pytest

from ai_tools.catalog import (
    MODES,
    CatalogError,
    check_consistency,
    load_catalog,
    load_metrics,
    parse_catalog,
)

VALID = {
    "categories": {"agents": "Agents"},
    "tools": [
        {
            "repo": "acme/widget",
            "category": "agents",
            "summary": "A widget.",
            "use_cases": "Testing.",
            "mode": "library",
            "relevance": 7,
            "quality": 7,
            "integration": 7,
            "license_class": "permissive",
        }
    ],
}


def variant(**changes):
    raw = copy.deepcopy(VALID)
    raw["tools"][0].update(changes)
    return raw


def test_valid_catalog_parses():
    catalog = parse_catalog(VALID)
    assert catalog.tools[0].url == "https://github.com/acme/widget"
    assert catalog.tools[0].name == "widget"


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"category": "nope"}, "unknown category"),
        ({"mode": "maybe"}, "unknown mode"),
        ({"license_class": "beerware"}, "unknown license_class"),
        ({"relevance": 11}, "between 0 and 10"),
        ({"quality": "high"}, "between 0 and 10"),
        ({"integration": True}, "between 0 and 10"),
        ({"repo": "not a repo"}, "owner/name"),
        ({"mode": "reject"}, "reason"),
        ({"flags": "single string"}, "list of strings"),
        ({"security_penalty": -1}, "security_penalty"),
        ({"summary": ""}, "summary"),
    ],
)
def test_invalid_entries_are_rejected(changes, message):
    with pytest.raises(CatalogError, match=message):
        parse_catalog(variant(**changes))


def test_duplicate_repos_rejected_case_insensitively():
    raw = copy.deepcopy(VALID)
    raw["tools"].append(dict(raw["tools"][0], repo="ACME/Widget"))
    with pytest.raises(CatalogError, match="duplicate"):
        parse_catalog(raw)


def test_missing_sections_rejected():
    with pytest.raises(CatalogError):
        parse_catalog({"tools": VALID["tools"]})
    with pytest.raises(CatalogError):
        parse_catalog({"categories": VALID["categories"], "tools": []})
    with pytest.raises(CatalogError):
        parse_catalog(["not", "a", "mapping"])


def test_invalid_yaml_and_json_raise_catalog_error(tmp_path):
    bad_yaml = tmp_path / "tools.yaml"
    bad_yaml.write_text("tools: [unclosed\n")
    with pytest.raises(CatalogError, match="invalid YAML"):
        load_catalog(bad_yaml)
    bad_json = tmp_path / "metrics.json"
    bad_json.write_text("{nope")
    with pytest.raises(CatalogError, match="invalid JSON"):
        load_metrics(bad_json)
    wrong_shape = tmp_path / "metrics2.json"
    wrong_shape.write_text(json.dumps({"repos": {}}))
    with pytest.raises(CatalogError, match="evaluated_at"):
        load_metrics(wrong_shape)


def test_consistency_flags_missing_metrics_and_unrejected_archives():
    catalog = parse_catalog(VALID)
    assert check_consistency(catalog, {"repos": {}})[0].startswith("acme/widget: no metrics")
    entry = {"stars": 1, "pushed_at": "2026-01-01", "archived": True, "license_spdx": "MIT"}
    archived = {"repos": {"acme/widget": entry}}
    assert any("archived" in p for p in check_consistency(catalog, archived))


# ---- the real, committed data -------------------------------------------------

@pytest.fixture(scope="module")
def real():
    return load_catalog(), load_metrics()


def test_real_catalog_is_consistent(real):
    catalog, metrics = real
    assert check_consistency(catalog, metrics) == []


def test_real_catalog_covers_every_category_and_mode(real):
    catalog, _ = real
    used_categories = {t.category for t in catalog.tools}
    assert used_categories == set(catalog.categories)
    assert {t.mode for t in catalog.tools} == set(MODES)


def test_real_metrics_have_valid_shapes(real):
    _, metrics = real
    assert re.match(r"^\d{4}-\d{2}-\d{2}T", metrics["evaluated_at"])
    for repo, m in metrics["repos"].items():
        assert isinstance(m["stars"], int) and m["stars"] >= 0, repo
        assert isinstance(m["archived"], bool), repo
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", m["pushed_at"]), repo


def test_noassertion_licenses_are_explained(real):
    """If GitHub can't identify the license, the catalog must say what it actually is."""
    catalog, metrics = real
    for tool in catalog.tools:
        if metrics["repos"][tool.repo]["license_spdx"] in ("NOASSERTION", "none"):
            assert tool.license_note, f"{tool.repo} needs a license_note"
