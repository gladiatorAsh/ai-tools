"""Load and validate the hand-curated catalog and the GitHub metrics snapshot."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "catalog" / "tools.yaml"
METRICS_PATH = ROOT / "data" / "metrics.json"

MODES = {
    "library": "Integrate directly as a dependency",
    "service": "Run/connect as a service or API",
    "mcp": "Add as an MCP server",
    "dev-tool": "Development-only tool",
    "poc": "Evaluate in a proof of concept first",
    "reject": "Rejected",
}
LICENSE_CLASSES = {"permissive", "open-core", "source-available", "copyleft", "model-license"}
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SCORE_FIELDS = ("relevance", "quality", "integration")


class CatalogError(ValueError):
    """Raised when the catalog or metrics file is malformed."""


@dataclass(frozen=True)
class Tool:
    repo: str
    category: str
    summary: str
    use_cases: str
    mode: str
    relevance: float
    quality: float
    integration: float
    license_class: str
    license_note: str | None = None
    reason: str | None = None
    security_penalty: float = 0.0
    flags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}"

    @property
    def name(self) -> str:
        return self.repo.split("/", 1)[1]


@dataclass(frozen=True)
class Catalog:
    categories: dict[str, str]
    tools: tuple[Tool, ...]


def _require(entry: dict[str, Any], key: str, where: str) -> Any:
    if key not in entry or entry[key] in (None, ""):
        raise CatalogError(f"{where}: missing required field '{key}'")
    return entry[key]


def parse_catalog(raw: dict[str, Any]) -> Catalog:
    """Validate a parsed YAML document and return a Catalog."""
    if not isinstance(raw, dict):
        raise CatalogError("catalog root must be a mapping")
    categories = raw.get("categories")
    if not isinstance(categories, dict) or not categories:
        raise CatalogError("catalog must define a non-empty 'categories' mapping")
    entries = raw.get("tools")
    if not isinstance(entries, list) or not entries:
        raise CatalogError("catalog must define a non-empty 'tools' list")

    tools: list[Tool] = []
    seen: set[str] = set()
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise CatalogError(f"tools[{i}] must be a mapping")
        repo = _require(entry, "repo", f"tools[{i}]")
        where = f"tools[{i}] ({repo})"
        if not REPO_RE.match(repo):
            raise CatalogError(f"{where}: repo must look like 'owner/name'")
        if repo.lower() in seen:
            raise CatalogError(f"{where}: duplicate repo")
        seen.add(repo.lower())

        category = _require(entry, "category", where)
        if category not in categories:
            raise CatalogError(f"{where}: unknown category '{category}'")
        mode = _require(entry, "mode", where)
        if mode not in MODES:
            raise CatalogError(f"{where}: unknown mode '{mode}' (expected one of {sorted(MODES)})")
        license_class = _require(entry, "license_class", where)
        if license_class not in LICENSE_CLASSES:
            raise CatalogError(f"{where}: unknown license_class '{license_class}'")
        if mode == "reject" and not entry.get("reason"):
            raise CatalogError(f"{where}: rejected tools must give a 'reason'")

        scores = {}
        for key in SCORE_FIELDS:
            value = _require(entry, key, where)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 10:
                raise CatalogError(f"{where}: '{key}' must be a number between 0 and 10")
            scores[key] = float(value)

        penalty = entry.get("security_penalty", 0)
        if not isinstance(penalty, (int, float)) or not 0 <= penalty <= 10:
            raise CatalogError(f"{where}: 'security_penalty' must be between 0 and 10")

        flags = entry.get("flags") or []
        if not isinstance(flags, list) or not all(isinstance(f, str) for f in flags):
            raise CatalogError(f"{where}: 'flags' must be a list of strings")

        tools.append(
            Tool(
                repo=repo,
                category=category,
                summary=_require(entry, "summary", where),
                use_cases=_require(entry, "use_cases", where),
                mode=mode,
                license_class=license_class,
                license_note=entry.get("license_note"),
                reason=entry.get("reason"),
                security_penalty=float(penalty),
                flags=tuple(flags),
                **scores,
            )
        )
    return Catalog(categories=dict(categories), tools=tuple(tools))


def load_catalog(path: Path = CATALOG_PATH) -> Catalog:
    with open(path, encoding="utf-8") as fh:
        try:
            raw = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise CatalogError(f"{path}: invalid YAML: {exc}") from exc
    return parse_catalog(raw)


def load_metrics(path: Path = METRICS_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise CatalogError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or "repos" not in data or "evaluated_at" not in data:
        raise CatalogError(f"{path}: expected an object with 'evaluated_at' and 'repos'")
    return data


def check_consistency(catalog: Catalog, metrics: dict[str, Any]) -> list[str]:
    """Return a list of problems linking the catalog to the metrics snapshot."""
    problems = []
    repos = metrics["repos"]
    for tool in catalog.tools:
        m = repos.get(tool.repo)
        if m is None:
            problems.append(f"{tool.repo}: no metrics entry (run `python -m ai_tools refresh`)")
            continue
        for key in ("stars", "pushed_at", "archived", "license_spdx"):
            if key not in m:
                problems.append(f"{tool.repo}: metrics missing '{key}'")
        if m.get("archived") and tool.mode != "reject":
            problems.append(f"{tool.repo}: archived on GitHub but not rejected")
    return problems
