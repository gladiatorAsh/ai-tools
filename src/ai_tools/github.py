"""Refresh repository metrics from the GitHub REST API.

Uses only the standard library. A token is read from GITHUB_TOKEN (or GH_TOKEN);
it is never logged or written to disk. Without a token GitHub allows 60
requests/hour, which is not enough for the full catalog, so anonymous runs
must be opted into explicitly.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .catalog import REPO_RE

API = "https://api.github.com"
USER_AGENT = "ai-tools-catalog-refresher"

Fetcher = Callable[[str, dict[str, str]], tuple[int, Any]]


class GitHubError(RuntimeError):
    pass


def get_token(env: dict[str, str] | None = None) -> str | None:
    env = os.environ if env is None else env
    return env.get("GITHUB_TOKEN") or env.get("GH_TOKEN") or None


def _urllib_fetch(url: str, headers: dict[str, str], timeout: float = 20.0) -> tuple[int, Any]:
    if not url.startswith(API + "/"):
        raise GitHubError(f"refusing to fetch non-GitHub URL: {url}")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - URL is checked above
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body: Any
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:  # pragma: no cover - body is informational only
            body = None
        return exc.code, body


def _headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_repo(repo: str, token: str | None, fetch: Fetcher = _urllib_fetch) -> dict[str, Any]:
    """Return normalised metrics for one repository."""
    if not REPO_RE.match(repo):
        raise GitHubError(f"invalid repo name: {repo!r}")
    headers = _headers(token)
    status, data = fetch(f"{API}/repos/{repo}", headers)
    if status == 404:
        raise GitHubError(f"{repo}: not found (renamed, deleted or private)")
    if status in (403, 429):
        raise GitHubError(f"{repo}: rate limited or forbidden (HTTP {status})")
    if status != 200 or not isinstance(data, dict):
        raise GitHubError(f"{repo}: unexpected HTTP {status}")

    license_info = data.get("license") or {}
    metrics = {
        "stars": int(data["stargazers_count"]),
        "forks": data.get("forks_count"),
        "license_spdx": license_info.get("spdx_id") or "none",
        "pushed_at": (data.get("pushed_at") or "")[:10] or None,
        "archived": bool(data.get("archived")),
        "language": data.get("language"),
        "open_issues_and_prs": data.get("open_issues_count"),
        "created_at": (data.get("created_at") or "")[:10] or None,
        "latest_release": None,
        "latest_release_date": None,
    }
    if data.get("full_name") and data["full_name"].lower() != repo.lower():
        metrics["renamed_to"] = data["full_name"]

    status, release = fetch(f"{API}/repos/{repo}/releases/latest", headers)
    if status == 200 and isinstance(release, dict):
        metrics["latest_release"] = release.get("tag_name")
        metrics["latest_release_date"] = (release.get("published_at") or "")[:10] or None
    elif status in (403, 429):
        raise GitHubError(f"{repo}: rate limited while reading releases (HTTP {status})")
    # 404 simply means the project publishes no GitHub releases.
    return metrics


def refresh(
    repos: Iterable[str],
    existing: dict[str, Any],
    token: str | None,
    fetch: Fetcher = _urllib_fetch,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    delay: float = 0.0,
    log: Callable[[str], None] = lambda msg: print(msg, file=sys.stderr),
) -> tuple[dict[str, Any], list[str]]:
    """Fetch fresh metrics. Failed repos keep their previous values and are reported."""
    previous = dict(existing.get("repos", {}))
    updated: dict[str, Any] = {}
    failures: list[str] = []
    for repo in repos:
        try:
            updated[repo] = fetch_repo(repo, token, fetch)
            if "renamed_to" in updated[repo]:
                log(f"note: {repo} now redirects to {updated[repo]['renamed_to']} - update catalog/tools.yaml")
        except GitHubError as exc:
            failures.append(str(exc))
            log(f"warning: {exc}")
            if repo in previous:
                updated[repo] = previous[repo]
        if delay:
            time.sleep(delay)
    snapshot = {
        "evaluated_at": now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "GitHub REST API (GET /repos/{owner}/{repo}, /releases/latest)",
        "repos": dict(sorted(updated.items(), key=lambda kv: kv[0].lower())),
    }
    return snapshot, failures


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".metrics-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
