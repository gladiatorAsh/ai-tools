import math

import pytest

from ai_tools.catalog import Tool
from ai_tools.scoring import (
    WEIGHTS,
    adoption_score,
    license_security_score,
    maintenance_score,
    score_all,
    score_tool,
)


def make_tool(**overrides):
    base = dict(
        repo="acme/widget",
        category="agents",
        summary="s",
        use_cases="u",
        mode="library",
        relevance=8.0,
        quality=8.0,
        integration=8.0,
        license_class="permissive",
    )
    base.update(overrides)
    return Tool(**base)


def test_weights_sum_to_one():
    assert math.isclose(sum(WEIGHTS.values()), 1.0)


def test_weights_match_brief():
    assert WEIGHTS == {
        "relevance": 0.30,
        "quality": 0.20,
        "adoption": 0.15,
        "maintenance": 0.15,
        "license_security": 0.10,
        "integration": 0.10,
    }


@pytest.mark.parametrize(
    "stars, expected",
    [(0, 0.0), (1_000, 0.0), (150_000, 10.0), (10_000_000, 10.0)],
)
def test_adoption_bounds(stars, expected):
    assert adoption_score(stars) == pytest.approx(expected)


def test_adoption_is_log_scaled_and_monotonic():
    values = [adoption_score(s) for s in (2_000, 10_000, 50_000, 100_000)]
    assert values == sorted(values)
    # log scale: every 10x in stars adds the same increment, rather than multiplying the score
    step_low = adoption_score(10_000) - adoption_score(1_001)
    step_high = adoption_score(100_000) - adoption_score(10_000)
    assert step_high == pytest.approx(step_low, abs=0.01)


def test_maintenance_fresh_stale_archived():
    assert maintenance_score("2026-10-20", False, "2026-10-22") == 10.0
    assert maintenance_score("2025-01-01", False, "2026-10-22") == 0.0
    assert maintenance_score("2026-10-21", True, "2026-10-22") == 0.0
    mid = maintenance_score("2026-04-22", False, "2026-10-22")
    assert 0 < mid < 10


def test_maintenance_accepts_iso_timestamps():
    assert maintenance_score("2026-10-01", False, "2026-10-22T03:16:00Z") == 10.0


def test_license_security_penalty_and_floor():
    assert license_security_score(make_tool()) == 10.0
    assert license_security_score(make_tool(license_class="copyleft")) == 3.0
    assert license_security_score(make_tool(security_penalty=2)) == 8.0
    assert license_security_score(make_tool(license_class="copyleft", security_penalty=9)) == 0.0


def test_score_tool_is_weighted_sum():
    tool = make_tool(relevance=10, quality=10, integration=10)
    metrics = {"stars": 150_000, "pushed_at": "2026-10-21", "archived": False}
    s = score_tool(tool, metrics, "2026-10-22")
    assert s.total == pytest.approx(10.0)
    assert set(s.factors) == set(WEIGHTS)


def test_archived_tool_scores_lower_than_identical_active_one():
    tool = make_tool()
    active = score_tool(tool, {"stars": 50_000, "pushed_at": "2026-10-21", "archived": False}, "2026-10-22")
    archived = score_tool(tool, {"stars": 50_000, "pushed_at": "2026-10-21", "archived": True}, "2026-10-22")
    assert archived.total < active.total


def test_score_all_sorts_descending_and_skips_missing_metrics():
    good = make_tool(repo="a/good", relevance=10)
    weak = make_tool(repo="a/weak", relevance=1)
    missing = make_tool(repo="a/missing")
    snapshot = {
        "evaluated_at": "2026-10-22",
        "repos": {
            "a/good": {"stars": 5_000, "pushed_at": "2026-10-21", "archived": False},
            "a/weak": {"stars": 5_000, "pushed_at": "2026-10-21", "archived": False},
        },
    }
    result = score_all([weak, missing, good], snapshot)
    assert [s.tool.repo for s in result] == ["a/good", "a/weak"]
