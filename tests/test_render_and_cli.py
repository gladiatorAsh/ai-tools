import json
import re
from pathlib import Path

from ai_tools.__main__ import main
from ai_tools.catalog import ROOT, load_catalog, load_metrics
from ai_tools.render import format_stars, render_document, render_tables
from ai_tools.scoring import score_all


def test_format_stars():
    assert format_stars(999) == "999"
    assert format_stars(1500) == "1.5k"
    assert format_stars(184_220) == "184.2k"


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


def test_committed_catalog_reference_is_up_to_date():
    assert main(["render", "--check"]) == 0


def test_rendered_document_is_standalone():
    catalog, metrics = load_catalog(), load_metrics()
    doc = render_document(catalog, score_all(catalog.tools, metrics), metrics["evaluated_at"])
    assert doc.startswith("<!-- Generated")
    assert "# AI Tools Catalog" in doc
    assert "BEGIN GENERATED" not in doc


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


def test_render_check_detects_stale_output(tmp_path):
    out = tmp_path / "catalog.md"
    assert main(["render", "--output", str(out), "--check"]) == 1   # missing
    out.write_text("stale")
    assert main(["render", "--output", str(out), "--check"]) == 1
    assert main(["render", "--output", str(out)]) == 0
    assert main(["render", "--output", str(out), "--check"]) == 0


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
        if spec.get("command") == "npx":
            pkg = next(a for a in spec["args"] if not a.startswith("-"))
            assert re.search(r"@\d+\.\d+\.\d+$", pkg), f"{name}: pin an exact version, got {pkg}"


def test_mcp_servers_are_catalogued_as_mcp():
    catalog = load_catalog()
    mcp_repos = {t.repo for t in catalog.tools if t.mode == "mcp"}
    readme = (ROOT / "mcp" / "README.md").read_text()
    for name, spec in json.loads(MCP_CONFIG.read_text())["mcpServers"].items():
        if "url" in spec:
            assert spec["url"].startswith("https://"), name
    for repo in mcp_repos - {"modelcontextprotocol/servers"}:
        assert f"github.com/{repo}" in readme, repo


def test_env_example_has_no_values():
    for line in Path(ROOT / ".env.example").read_text().splitlines():
        if line and not line.startswith("#"):
            assert line.endswith("="), line
