import json
import re
from pathlib import Path

import pytest

from ai_tools.__main__ import main
from ai_tools.catalog import ROOT, load_catalog, load_metrics
from ai_tools.render import BEGIN, END, format_stars, render_tables, splice
from ai_tools.scoring import score_all


def test_format_stars():
    assert format_stars(999) == "999"
    assert format_stars(1500) == "1.5k"
    assert format_stars(184_220) == "184.2k"


def test_splice_replaces_only_generated_block():
    readme = f"intro\n{BEGIN}\nold\n{END}\noutro\n"
    out = splice(readme, f"{BEGIN}\nnew\n{END}")
    assert out == f"intro\n{BEGIN}\nnew\n{END}\noutro\n"


def test_splice_requires_markers():
    with pytest.raises(ValueError):
        splice("no markers here", "x")


def test_rendered_tables_cover_every_tool_and_category():
    catalog, metrics = load_catalog(), load_metrics()
    text = render_tables(catalog, score_all(catalog.tools, metrics), metrics["evaluated_at"])
    for tool in catalog.tools:
        assert f"]({tool.url})" in text, tool.repo
    for label in catalog.categories.values():
        assert f"### {label}" in text
    # rejected tools never appear as a category's top pick
    top_section = text.split("## Ranked catalog")[0]
    for tool in catalog.tools:
        if tool.mode == "reject":
            assert f"]({tool.url})" not in top_section


def test_pipe_characters_are_escaped():
    catalog, metrics = load_catalog(), load_metrics()
    text = render_tables(catalog, score_all(catalog.tools, metrics), metrics["evaluated_at"])
    for line in text.splitlines():
        if line.startswith("| ") and "](https://github.com/" in line:
            unescaped = re.sub(r"\\\|", "", line)
            assert unescaped.count("|") in (6, 9), line


def test_committed_readme_is_up_to_date():
    assert main(["render", "--check"]) == 0


def test_cli_validate_and_score(capsys):
    assert main(["validate"]) == 0
    assert main(["score", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out.split("\n", 1)[1])
    assert payload[0]["total"] >= payload[-1]["total"]


def test_cli_refresh_requires_token(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert main(["refresh"]) == 2
    assert "GITHUB_TOKEN" in capsys.readouterr().err


def test_cli_reports_missing_files_cleanly(tmp_path, capsys):
    assert main(["--catalog", str(tmp_path / "missing.yaml"), "validate"]) == 1
    assert "error:" in capsys.readouterr().err


def test_render_check_detects_stale_readme(tmp_path):
    stale = tmp_path / "README.md"
    stale.write_text(f"x\n{BEGIN}\nstale\n{END}\n")
    assert main(["render", "--readme", str(stale), "--check"]) == 1
    assert main(["render", "--readme", str(stale)]) == 0
    assert main(["render", "--readme", str(stale), "--check"]) == 0


# ---- MCP config hygiene ---------------------------------------------------------

MCP_CONFIG = ROOT / "mcp" / "servers.example.json"
SECRET_PATTERNS = [r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"sk-[A-Za-z0-9]{20,}", r"Bearer\s+\S+"]


def test_mcp_config_has_no_secrets():
    text = MCP_CONFIG.read_text()
    for pattern in SECRET_PATTERNS:
        assert not re.search(pattern, text), pattern


def test_mcp_config_pins_npm_versions():
    servers = json.loads(MCP_CONFIG.read_text())["mcpServers"]
    for name, spec in servers.items():
        if spec["command"] == "npx":
            pkg = next(a for a in spec["args"] if not a.startswith("-"))
            assert re.search(r"@\d+\.\d+\.\d+$", pkg), f"{name}: pin an exact version, got {pkg}"


def test_mcp_servers_are_catalogued_as_mcp():
    catalog = load_catalog()
    mcp_repos = {t.repo for t in catalog.tools if t.mode == "mcp"}
    readme = (ROOT / "mcp" / "README.md").read_text()
    for repo in mcp_repos - {"modelcontextprotocol/servers"}:
        assert f"github.com/{repo}" in readme, repo


def test_env_example_has_no_values():
    for line in Path(ROOT / ".env.example").read_text().splitlines():
        if line and not line.startswith("#"):
            assert line.endswith("="), line
