import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ai_tools.__main__ import main
from ai_tools.catalog import ROOT
from ai_tools.skills import (
    MAX_DESCRIPTION,
    SkillError,
    load_lock,
    load_skills,
    split_frontmatter,
    validate_agent,
    validate_pack,
    verify_vendored,
)

GOOD_SKILL = """---
name: demo-skill
description: Does a thing. Use when testing.
---

# Demo

## When to Use
- tests

## Process
See [details](references/details.md).

## Verification
- [ ] done
"""


@pytest.fixture
def pack(tmp_path):
    """A minimal valid pack in a temp dir."""
    (tmp_path / "skills" / "demo-skill" / "references").mkdir(parents=True)
    (tmp_path / "skills" / "demo-skill" / "SKILL.md").write_text(GOOD_SKILL)
    (tmp_path / "skills" / "demo-skill" / "references" / "details.md").write_text("x")
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "helper.agent.md").write_text("---\nname: helper\ndescription: Helps.\n---\nBody\n")
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor" / "skills.lock.json").write_text(json.dumps({"sources": {}, "skills": {}}))
    (tmp_path / "plugin.json").write_text(json.dumps({"name": "x", "version": "1", "description": "d"}))
    return tmp_path


def write_skill(pack, text, name="demo-skill"):
    (pack / "skills" / name).mkdir(parents=True, exist_ok=True)
    (pack / "skills" / name / "SKILL.md").write_text(text)


def test_valid_pack(pack):
    assert validate_pack(pack) == []


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda t: t.replace("name: demo-skill", "name: Demo_Skill"), "lowercase"),
        (lambda t: t.replace("name: demo-skill", "name: other-name"), "must match its directory"),
        (lambda t: t.replace("description: Does a thing. Use when testing.\n", ""), "missing 'description'"),
        (lambda t: t.replace("Use when testing", "Testing"), "Use when"),
        (lambda t: t.replace("---\n\n# Demo", "model: gpt\n---\n\n# Demo"), "unsupported frontmatter"),
        (lambda t: t.replace("## Verification", "## Done"), "'## Verification'"),
        (lambda t: t.replace("references/details.md", "references/missing.md"), "broken link"),
        (lambda t: t + "\n" * 600, "lines"),
        (lambda t: t.replace("Does a thing.", "x" * (MAX_DESCRIPTION + 1)), "max 1024"),
    ],
)
def test_skill_problems_detected(pack, mutation, message):
    write_skill(pack, mutation(GOOD_SKILL))
    problems = validate_pack(pack)
    assert any(message in p for p in problems), problems


def test_links_outside_skill_folder_are_rejected(pack):
    (pack / "README.md").write_text("x")
    write_skill(pack, GOOD_SKILL.replace("references/details.md", "../../README.md"))
    assert any("leaves the skill folder" in p for p in validate_pack(pack))


def test_links_inside_code_are_ignored(pack):
    write_skill(pack, GOOD_SKILL + "\n```python\nf[x](**kwargs)\n```\nand `[a](b)` inline\n")
    assert validate_pack(pack) == []


def test_frontmatter_errors():
    with pytest.raises(SkillError, match="must start"):
        split_frontmatter("# no frontmatter", "x")
    with pytest.raises(SkillError, match="not closed"):
        split_frontmatter("---\nname: a\n", "x")
    with pytest.raises(SkillError, match="invalid frontmatter"):
        split_frontmatter("---\nname: [unclosed\n---\nbody", "x")


def test_agents_must_use_agent_md_suffix(pack):
    bad = pack / "agents" / "reviewer.md"
    bad.write_text("---\ndescription: x\n---\n")
    assert any("*.agent.md" in p for p in validate_pack(pack))
    assert validate_agent(pack / "agents" / "helper.agent.md") == []


def test_plugin_manifest_requires_fields(pack):
    (pack / "plugin.json").write_text(json.dumps({"name": "x"}))
    assert any("plugin.json" in p for p in validate_pack(pack))


def test_vendored_skill_edits_are_detected(pack):
    from ai_tools.skills import skill_files

    vendored = (GOOD_SKILL.replace("demo-skill", "vendored-one").replace("Use when testing", "Imported")
                .replace("See [details](references/details.md).", "Steps."))
    write_skill(pack, vendored, name="vendored-one")
    lock = {
        "sources": {"up/stream": {"url": "https://github.com/up/stream", "commit": "a" * 40}},
        "skills": {"vendored-one": {"source": "up/stream", "path": "skills/vendored-one",
                                     "files": skill_files(pack / "skills" / "vendored-one")}},
    }
    (pack / "vendor" / "skills.lock.json").write_text(json.dumps(lock))
    # vendored skills are exempt from the "Use when" house-style rule
    assert validate_pack(pack) == []
    (pack / "skills" / "vendored-one" / "SKILL.md").write_text("---\nname: vendored-one\ndescription: edited\n---\n")
    problems = validate_pack(pack)
    assert any("differs from up/stream" in p for p in problems), problems


# ---- the real pack -------------------------------------------------------------------

def test_real_pack_is_valid():
    assert validate_pack(ROOT) == []


def test_cli_validate_skills():
    assert main(["validate-skills"]) == 0


def test_every_original_skill_is_listed_in_readme_and_router():
    readme = (ROOT / "README.md").read_text()
    router = (ROOT / "skills" / "using-ai-tools-skills" / "SKILL.md").read_text()
    for skill in load_skills():
        assert f"skills/{skill.name}/SKILL.md" in readme, skill.name
        if skill.name != "using-ai-tools-skills":
            assert f"`{skill.name}`" in router, f"{skill.name} missing from router table"


def test_skills_referenced_by_name_exist():
    names = {s.name for s in load_skills()}
    allowed_external = {"dotnet-mcp-builder"}  # mentioned as an optional awesome-copilot skill
    for skill in load_skills():
        if skill.vendored:
            continue
        for ref in set(__import__("re").findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)` skill", skill.body)):
            assert ref in names | allowed_external, f"{skill.name} references unknown skill {ref}"


def test_lock_file_covers_vendored_skills_and_license_present():
    lock = load_lock()
    assert lock["skills"], "expected vendored skills"
    assert verify_vendored(lock) == []
    assert (ROOT / "vendor" / "LICENSE-awesome-copilot.txt").read_text().startswith("MIT License")
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
    for name in lock["skills"]:
        assert f"skills/{name}" in notices, name


@pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")
def test_install_script_personal_and_project(tmp_path):
    env = {"HOME": str(tmp_path / "home"), "PATH": "/usr/bin:/bin"}
    run = lambda *a: subprocess.run(["bash", str(ROOT / "scripts" / "install.sh"), *a],  # noqa: E731
                                    capture_output=True, text=True, env=env)
    r = run("--skill", "llm-evals")
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "home" / ".copilot" / "skills" / "llm-evals" / "SKILL.md").is_file()
    assert not (tmp_path / "home" / ".copilot" / "skills" / "llm-red-teaming").exists()

    project = tmp_path / "proj"
    project.mkdir()
    r = run("--project", str(project))
    assert r.returncode == 0, r.stderr
    installed = {p.name for p in (project / ".github" / "skills").iterdir()}
    assert installed == {s.name for s in load_skills()}
    assert (project / ".github" / "agents" / "ai-solution-architect.agent.md").is_file()

    assert run("--skill", "../../etc").returncode == 2
    assert run("--skill", "does-not-exist").returncode == 1
    assert run("--bogus").returncode == 2


def test_vendor_sync_rejects_unsafe_refs(tmp_path):
    from ai_tools.skills import vendor_sync

    lock = tmp_path / "lock.json"
    lock.write_text(json.dumps({"sources": {"s": {"url": "https://example.invalid/x", "commit": "abc"}},
                                "skills": {"k": {"source": "s", "path": "skills/k", "files": {}}}}))
    with pytest.raises(SkillError, match="unsafe git ref"):
        vendor_sync(lock_path=lock, skills_dir=tmp_path, ref="main; rm -rf /")
    assert json.loads(lock.read_text())["sources"]["s"]["commit"] == "abc"  # untouched
    _ = Path  # keep import used
