"""Command-line entry point: python -m ai_tools {validate,score,render,refresh}."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import catalog as cat
from .github import get_token, refresh, write_json_atomic
from .render import render_tables, splice
from .scoring import score_all

README_PATH = cat.ROOT / "README.md"


def _load(args):
    catalog = cat.load_catalog(Path(args.catalog))
    metrics = cat.load_metrics(Path(args.metrics))
    return catalog, metrics


def cmd_validate(args) -> int:
    catalog, metrics = _load(args)
    problems = cat.check_consistency(catalog, metrics)
    for p in problems:
        print(f"error: {p}", file=sys.stderr)
    if not problems:
        print(f"ok: {len(catalog.tools)} tools, {len(catalog.categories)} categories")
    return 1 if problems else 0


def cmd_score(args) -> int:
    catalog, metrics = _load(args)
    scores = score_all(catalog.tools, metrics)
    if args.json:
        payload = [
            {"repo": s.tool.repo, "category": s.tool.category, "mode": s.tool.mode,
             "total": s.total, "factors": {k: round(v, 2) for k, v in s.factors.items()}}
            for s in scores
        ]
        print(json.dumps(payload, indent=2))
    else:
        for s in scores:
            print(f"{s.total:5.2f}  {s.tool.category:20} {s.tool.mode:9} {s.tool.repo}")
    return 0


def cmd_render(args) -> int:
    catalog, metrics = _load(args)
    problems = cat.check_consistency(catalog, metrics)
    if problems:
        for p in problems:
            print(f"error: {p}", file=sys.stderr)
        return 1
    generated = render_tables(catalog, score_all(catalog.tools, metrics), metrics["evaluated_at"])
    readme_path = Path(args.readme)
    current = readme_path.read_text(encoding="utf-8")
    updated = splice(current, generated)
    if args.check:
        if updated != current:
            print("README.md is out of date: run `python -m ai_tools render`", file=sys.stderr)
            return 1
        print("README.md is up to date")
        return 0
    readme_path.write_text(updated, encoding="utf-8")
    print(f"rendered {readme_path}")
    return 0


def cmd_refresh(args) -> int:
    catalog = cat.load_catalog(Path(args.catalog))
    metrics_path = Path(args.metrics)
    existing = cat.load_metrics(metrics_path) if metrics_path.exists() else {"repos": {}}
    token = get_token()
    if not token and not args.allow_anonymous:
        print(
            "error: set GITHUB_TOKEN (read-only, public repos) - anonymous access is limited to "
            "60 requests/hour, too few for the catalog. Pass --allow-anonymous to try anyway.",
            file=sys.stderr,
        )
        return 2
    repos = [t.repo for t in catalog.tools]
    snapshot, failures = refresh(repos, existing, token, delay=args.delay)
    write_json_atomic(metrics_path, snapshot)
    print(f"refreshed {len(repos) - len(failures)}/{len(repos)} repos -> {metrics_path}")
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai_tools", description=__doc__)
    parser.add_argument("--catalog", default=str(cat.CATALOG_PATH))
    parser.add_argument("--metrics", default=str(cat.METRICS_PATH))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="check catalog schema and metrics consistency").set_defaults(func=cmd_validate)

    p_score = sub.add_parser("score", help="print weighted scores")
    p_score.add_argument("--json", action="store_true")
    p_score.set_defaults(func=cmd_score)

    p_render = sub.add_parser("render", help="regenerate the ranked tables in README.md")
    p_render.add_argument("--readme", default=str(README_PATH))
    p_render.add_argument("--check", action="store_true", help="fail if README.md is stale")
    p_render.set_defaults(func=cmd_render)

    p_refresh = sub.add_parser("refresh", help="fetch fresh metrics from the GitHub API")
    p_refresh.add_argument("--allow-anonymous", action="store_true")
    p_refresh.add_argument("--delay", type=float, default=0.0, help="seconds to wait between repos")
    p_refresh.set_defaults(func=cmd_refresh)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (cat.CatalogError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
