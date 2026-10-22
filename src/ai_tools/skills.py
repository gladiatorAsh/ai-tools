"""Validate the skills pack and manage vendored (third-party) skills.

Checks follow the Agent Skills spec as used by GitHub Copilot:
  - every skill is skills/<name>/SKILL.md with YAML frontmatter
  - `name` is lowercase-hyphenated and matches the directory
  - `description` is present, <= 1024 chars, and (for original skills) says "Use when"
  - only spec-defined top-level frontmatter keys are used
  - SKILL.md stays under 500 lines and its relative links resolve
Vendored skills are pinned in vendor/skills.lock.json by source commit and
per-file SHA-256, so local edits or partial copies are caught.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .catalog import ROOT

SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"
LOCK_PATH = ROOT / "vendor" / "skills.lock.json"

ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_DESCRIPTION = 1024
MAX_LINES = 500
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
ORIGINAL_SECTIONS = ("## When to Use", "## Verification")


class SkillError(ValueError):
    pass


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    frontmatter: dict[str, Any]
    body: str
    vendored: bool

    @property
    def description(self) -> str:
        return str(self.frontmatter.get("description", "")).strip()


def split_frontmatter(text: str, where: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise SkillError(f"{where}: must start with YAML frontmatter ('---')")
    parts = text.split("\n---", 1)
    if len(parts) != 2:
        raise SkillError(f"{where}: frontmatter is not closed with '---'")
    try:
        data = yaml.safe_load(parts[0].lstrip("-\n")) or {}
    except yaml.YAMLError as exc:
        raise SkillError(f"{where}: invalid frontmatter YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise SkillError(f"{where}: frontmatter must be a mapping")
    body = parts[1].split("\n", 1)[1] if "\n" in parts[1] else ""
    return data, body


def load_lock(path: Path = LOCK_PATH) -> dict[str, Any]:
    if not path.exists():
        return {"sources": {}, "skills": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def load_skills(skills_dir: Path = SKILLS_DIR, lock: dict[str, Any] | None = None) -> list[Skill]:
    lock = load_lock() if lock is None else lock
    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        fm, body = split_frontmatter(skill_md.read_text(encoding="utf-8"), str(skill_md.relative_to(skills_dir.parent)))
        skills.append(Skill(skill_md.parent.name, skill_md, fm, body, skill_md.parent.name in lock["skills"]))
    return skills


def validate_skill(skill: Skill) -> list[str]:
    where = f"skills/{skill.name}/SKILL.md"
    problems = []
    fm = skill.frontmatter
    extra = set(fm) - ALLOWED_KEYS
    if extra:
        problems.append(f"{where}: unsupported frontmatter keys {sorted(extra)} (move them under 'metadata')")
    name = fm.get("name")
    if not name:
        problems.append(f"{where}: missing 'name'")
    elif not NAME_RE.match(str(name)):
        problems.append(f"{where}: name '{name}' must be lowercase and hyphen-separated")
    elif name != skill.name:
        problems.append(f"{where}: name '{name}' must match its directory '{skill.name}'")
    desc = skill.description
    if not desc:
        problems.append(f"{where}: missing 'description'")
    elif len(desc) > MAX_DESCRIPTION:
        problems.append(f"{where}: description is {len(desc)} chars (max {MAX_DESCRIPTION})")
    lines = skill.path.read_text(encoding="utf-8").count("\n") + 1
    if lines > MAX_LINES:
        problems.append(f"{where}: {lines} lines (keep SKILL.md under {MAX_LINES}; move detail to references/)")
    prose = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", skill.body, flags=re.S))
    for target in LINK_RE.findall(prose):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        resolved = (skill.path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            problems.append(f"{where}: broken link '{target}'")
        elif skill.path.parent.resolve() not in resolved.parents and resolved != skill.path.parent.resolve():
            problems.append(f"{where}: link '{target}' leaves the skill folder (breaks single-skill installs)")
    if not skill.vendored:
        if desc and "use when" not in desc.lower():
            problems.append(f"{where}: description should include a 'Use when ...' trigger")
        for section in ORIGINAL_SECTIONS:
            if section not in skill.body:
                problems.append(f"{where}: missing '{section}' section")
    return problems


def validate_agent(path: Path) -> list[str]:
    where = f"agents/{path.name}"
    if not path.name.endswith(".agent.md"):
        return [f"{where}: Copilot only loads files named *.agent.md"]
    try:
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"), where)
    except SkillError as exc:
        return [str(exc)]
    problems = []
    if not str(fm.get("description", "")).strip():
        problems.append(f"{where}: missing 'description'")
    if fm.get("name") and fm["name"] != path.name.removesuffix(".agent.md"):
        problems.append(f"{where}: name must match the file name")
    return problems


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_files(skill_dir: Path) -> dict[str, str]:
    return {
        str(p.relative_to(skill_dir)).replace("\\", "/"): sha256(p)
        for p in sorted(skill_dir.rglob("*"))
        if p.is_file()
    }


def verify_vendored(lock: dict[str, Any], skills_dir: Path = SKILLS_DIR) -> list[str]:
    problems = []
    for name, entry in lock["skills"].items():
        skill_dir = skills_dir / name
        if not skill_dir.is_dir():
            problems.append(f"vendored skill '{name}' is in the lock file but missing from skills/")
            continue
        if entry["source"] not in lock["sources"]:
            problems.append(f"vendored skill '{name}' references unknown source '{entry['source']}'")
        actual = skill_files(skill_dir)
        if actual != entry["files"]:
            changed = sorted(set(actual.items()) ^ set(entry["files"].items()))
            files = sorted({f for f, _ in changed})
            commit = lock["sources"].get(entry["source"], {}).get("commit", "?")[:7]
            problems.append(
                f"vendored skill '{name}' differs from {entry['source']}@{commit} ({', '.join(files)}). "
                "Re-sync with `python -m ai_tools vendor-sync` instead of editing in place."
            )
    return problems


def validate_pack(root: Path = ROOT) -> list[str]:
    lock = load_lock(root / "vendor" / "skills.lock.json")
    problems: list[str] = []
    try:
        skills = load_skills(root / "skills", lock)
    except SkillError as exc:
        return [str(exc)]
    if not skills:
        problems.append("no skills found under skills/")
    for skill in skills:
        problems.extend(validate_skill(skill))
    problems.extend(verify_vendored(lock, root / "skills"))
    for agent in sorted((root / "agents").glob("*.md")):
        problems.extend(validate_agent(agent))
    manifest = root / "plugin.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for key in ("name", "version", "description"):
            if not data.get(key):
                problems.append(f"plugin.json: missing '{key}'")
    return problems


# ---- vendoring --------------------------------------------------------------------

def _safe_ref(ref: str) -> str:
    if not re.match(r"^[A-Za-z0-9._/-]+$", ref):
        raise SkillError(f"unsafe git ref: {ref!r}")
    return ref


def vendor_sync(lock_path: Path = LOCK_PATH, skills_dir: Path = SKILLS_DIR, ref: str | None = None,
                source: str | None = None) -> list[str]:
    """Re-fetch vendored skills from their pinned (or a new) commit and rewrite the lock.

    Uses a sparse, blob-filtered git clone into a temporary directory. Nothing from the
    clone is executed; only files under each skill's path are copied.
    """
    lock = load_lock(lock_path)
    messages = []
    for src_name, src in lock["sources"].items():
        if source and src_name != source:
            continue
        names = [n for n, e in lock["skills"].items() if e["source"] == src_name]
        target_ref = _safe_ref(ref or src["commit"])
        with tempfile.TemporaryDirectory(prefix="skills-vendor-") as tmp:
            clone = Path(tmp) / "repo"
            run = lambda *args: subprocess.run(args, check=True, capture_output=True, text=True)  # noqa: E731
            run("git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", src["url"], str(clone))
            run("git", "-C", str(clone), "sparse-checkout", "set", *[lock["skills"][n]["path"] for n in names])
            run("git", "-C", str(clone), "checkout", "--quiet", target_ref)
            commit = run("git", "-C", str(clone), "rev-parse", "HEAD").stdout.strip()
            for name in names:
                upstream = clone / lock["skills"][name]["path"]
                if not (upstream / "SKILL.md").is_file():
                    raise SkillError(f"{src_name}@{commit[:7]} has no {lock['skills'][name]['path']}/SKILL.md")
                dest = skills_dir / name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(upstream, dest)
                lock["skills"][name]["files"] = skill_files(dest)
            if commit != src["commit"]:
                messages.append(f"{src_name}: {src['commit'][:7]} -> {commit[:7]}")
            src["commit"] = commit
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return messages
