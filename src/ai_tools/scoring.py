"""Weighted scoring. Every factor is normalised to 0-10 before weighting.

Measured factors (adoption, maintenance) come from the GitHub snapshot.
Judged factors (relevance, quality, integration) are estimates from the catalog.
The license/security factor combines the verified license class with an
optional, documented security penalty.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from .catalog import Tool

WEIGHTS = {
    "relevance": 0.30,
    "quality": 0.20,
    "adoption": 0.15,
    "maintenance": 0.15,
    "license_security": 0.10,
    "integration": 0.10,
}

# Stars are log-scaled: 1k stars -> 0, 150k stars -> 10.
STARS_FLOOR = 1_000
STARS_CEILING = 150_000
# Commits within FRESH_DAYS score 10; score reaches 0 at STALE_DAYS.
FRESH_DAYS = 30
STALE_DAYS = 365

LICENSE_SCORES = {
    "permissive": 10.0,
    "open-core": 8.0,
    "model-license": 5.0,
    "source-available": 4.0,
    "copyleft": 3.0,
}


def clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return max(low, min(high, value))


def adoption_score(stars: int) -> float:
    if stars <= STARS_FLOOR:
        return 0.0
    span = math.log10(STARS_CEILING) - math.log10(STARS_FLOOR)
    return clamp(10 * (math.log10(stars) - math.log10(STARS_FLOOR)) / span)


def _as_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date() if "T" in value else date.fromisoformat(value)


def maintenance_score(pushed_at: str | date, archived: bool, as_of: str | date) -> float:
    if archived:
        return 0.0
    days = (_as_date(as_of) - _as_date(pushed_at)).days
    if days <= FRESH_DAYS:
        return 10.0
    return clamp(10 * (1 - (days - FRESH_DAYS) / (STALE_DAYS - FRESH_DAYS)))


def license_security_score(tool: Tool) -> float:
    return clamp(LICENSE_SCORES[tool.license_class] - tool.security_penalty)


@dataclass(frozen=True)
class Score:
    tool: Tool
    factors: dict[str, float]
    total: float
    metrics: dict[str, Any]


def score_tool(tool: Tool, metrics: dict[str, Any], as_of: str | date) -> Score:
    factors = {
        "relevance": tool.relevance,
        "quality": tool.quality,
        "adoption": adoption_score(metrics["stars"]),
        "maintenance": maintenance_score(metrics["pushed_at"], metrics["archived"], as_of),
        "license_security": license_security_score(tool),
        "integration": tool.integration,
    }
    total = sum(WEIGHTS[k] * v for k, v in factors.items())
    return Score(tool=tool, factors=factors, total=round(total, 2), metrics=metrics)


def score_all(tools, metrics_snapshot: dict[str, Any]) -> list[Score]:
    as_of = metrics_snapshot["evaluated_at"]
    repos = metrics_snapshot["repos"]
    scores = [score_tool(t, repos[t.repo], as_of) for t in tools if t.repo in repos]
    return sorted(scores, key=lambda s: (-s.total, s.tool.repo.lower()))
