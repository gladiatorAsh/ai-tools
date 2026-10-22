"""Render the ranked catalog into the generated section of README.md."""

from __future__ import annotations

from collections import defaultdict

from .catalog import MODES, Catalog
from .scoring import WEIGHTS, Score

BEGIN = "<!-- BEGIN GENERATED: do not edit by hand, run `python -m ai_tools render` -->"
END = "<!-- END GENERATED -->"

MODE_LABELS = {
    "library": "Library",
    "service": "Service",
    "mcp": "MCP server",
    "dev-tool": "Dev tool",
    "poc": "PoC first",
    "reject": "Rejected",
}


def format_stars(stars: int) -> str:
    if stars >= 1000:
        return f"{stars / 1000:.1f}k"
    return str(stars)


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _license(score: Score) -> str:
    spdx = score.metrics.get("license_spdx") or "none"
    label = spdx
    if spdx in ("NOASSERTION", "none") or score.tool.license_class != "permissive":
        label = f"{spdx} ({score.tool.license_class})"
    if score.tool.license_note:
        label += " †"
    return label


def render_tables(catalog: Catalog, scores: list[Score], evaluated_at: str) -> str:
    by_category: dict[str, list[Score]] = defaultdict(list)
    for s in scores:
        by_category[s.tool.category].append(s)

    weights = ", ".join(f"{k.replace('_', ' ')} {int(v * 100)}%" for k, v in WEIGHTS.items())
    out = [
        BEGIN,
        "",
        f"_Metrics snapshot: **{evaluated_at}** (UTC). {len(scores)} tools scored. Weights: {weights}._",
        "",
        "## Top pick per category",
        "",
        "| Category | Pick | Score | Stars | Adopt as |",
        "|---|---|---:|---:|---|",
    ]
    for key, label in catalog.categories.items():
        candidates = [s for s in by_category.get(key, []) if s.tool.mode != "reject"]
        if not candidates:
            continue
        top = candidates[0]
        out.append(
            f"| {label} | [{top.tool.name}]({top.tool.url}) | {top.total:.2f} | "
            f"{format_stars(top.metrics['stars'])} | {MODE_LABELS[top.tool.mode]} |"
        )

    out += ["", "## Ranked catalog", ""]
    for key, label in catalog.categories.items():
        rows = by_category.get(key, [])
        if not rows:
            continue
        out += [
            f"### {label}",
            "",
            "| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |",
            "|---:|---|---:|---:|---|---|---|---|",
        ]
        for rank, s in enumerate(rows, 1):
            note = s.tool.summary
            if s.tool.mode == "reject" and s.tool.reason:
                note += f" **Rejected:** {s.tool.reason}"
            if s.tool.license_note:
                note += f" † License: {s.tool.license_note}"
            if s.tool.flags:
                note += " ⚠️ " + "; ".join(s.tool.flags)
            out.append(
                f"| {rank} | [{s.tool.name}]({s.tool.url}) | {s.total:.2f} | "
                f"{format_stars(s.metrics['stars'])} | {s.metrics.get('pushed_at') or '—'} | "
                f"{_cell(_license(s))} | {MODE_LABELS[s.tool.mode]} | {_cell(note)} |"
            )
        out.append("")

    out += [
        "† GitHub's license label is incomplete or misleading here; the note says what the LICENSE file says.",
        "",
        "## Adoption modes",
        "",
        *[f"- **{MODE_LABELS[m]}** — {desc}" for m, desc in MODES.items()],
        "",
        END,
    ]
    return "\n".join(out)


def splice(readme: str, generated: str) -> str:
    """Replace the generated block in README text, keeping everything else."""
    if BEGIN not in readme or END not in readme:
        raise ValueError("README.md is missing the generated-section markers")
    head, rest = readme.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + generated + tail
