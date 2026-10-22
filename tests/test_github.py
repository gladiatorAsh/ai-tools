import json
from datetime import datetime, timezone

import pytest

from ai_tools.github import GitHubError, _urllib_fetch, fetch_repo, get_token, refresh, write_json_atomic

REPO_PAYLOAD = {
    "full_name": "acme/widget",
    "stargazers_count": 1234,
    "forks_count": 56,
    "license": {"spdx_id": "MIT"},
    "pushed_at": "2026-10-20T12:00:00Z",
    "archived": False,
    "language": "Python",
    "open_issues_count": 7,
    "created_at": "2024-01-01T00:00:00Z",
}


def fake_fetch(routes, calls=None):
    def fetch(url, headers):
        if calls is not None:
            calls.append((url, headers))
        return routes.get(url, (404, None))
    return fetch


def test_fetch_repo_normalises_fields_and_release():
    routes = {
        "https://api.github.com/repos/acme/widget": (200, REPO_PAYLOAD),
        "https://api.github.com/repos/acme/widget/releases/latest": (
            200,
            {"tag_name": "v1.2.3", "published_at": "2026-10-01T00:00:00Z"},
        ),
    }
    m = fetch_repo("acme/widget", "t0k3n", fake_fetch(routes))
    assert m == {
        "stars": 1234,
        "forks": 56,
        "license_spdx": "MIT",
        "pushed_at": "2026-10-20",
        "archived": False,
        "language": "Python",
        "open_issues_and_prs": 7,
        "created_at": "2024-01-01",
        "latest_release": "v1.2.3",
        "latest_release_date": "2026-10-01",
    }


def test_no_releases_is_not_an_error():
    routes = {"https://api.github.com/repos/acme/widget": (200, REPO_PAYLOAD)}
    m = fetch_repo("acme/widget", None, fake_fetch(routes))
    assert m["latest_release"] is None


def test_missing_license_and_rename_detected():
    payload = dict(REPO_PAYLOAD, license=None, full_name="newowner/widget")
    routes = {"https://api.github.com/repos/acme/widget": (200, payload)}
    m = fetch_repo("acme/widget", None, fake_fetch(routes))
    assert m["license_spdx"] == "none"
    assert m["renamed_to"] == "newowner/widget"


def test_token_sent_as_bearer_header_only_when_present():
    calls = []
    routes = {"https://api.github.com/repos/acme/widget": (200, REPO_PAYLOAD)}
    fetch_repo("acme/widget", "secret", fake_fetch(routes, calls))
    assert calls[0][1]["Authorization"] == "Bearer secret"
    calls.clear()
    fetch_repo("acme/widget", None, fake_fetch(routes, calls))
    assert "Authorization" not in calls[0][1]


@pytest.mark.parametrize(
    "status, match",
    [(404, "not found"), (403, "rate limited"), (429, "rate limited"), (500, "HTTP 500")],
)
def test_http_errors_raise(status, match):
    routes = {"https://api.github.com/repos/acme/widget": (status, {})}
    with pytest.raises(GitHubError, match=match):
        fetch_repo("acme/widget", None, fake_fetch(routes))


def test_rate_limit_on_release_endpoint_raises():
    routes = {
        "https://api.github.com/repos/acme/widget": (200, REPO_PAYLOAD),
        "https://api.github.com/repos/acme/widget/releases/latest": (403, {}),
    }
    with pytest.raises(GitHubError, match="releases"):
        fetch_repo("acme/widget", None, fake_fetch(routes))


@pytest.mark.parametrize("bad", ["", "no-slash", "a/b/c", "../etc/passwd", "a/b?x=1"])
def test_invalid_repo_names_rejected_before_any_request(bad):
    calls = []
    with pytest.raises(GitHubError, match="invalid repo"):
        fetch_repo(bad, None, fake_fetch({}, calls))
    assert calls == []


def test_real_fetcher_refuses_non_github_urls():
    with pytest.raises(GitHubError, match="non-GitHub"):
        _urllib_fetch("https://example.com/repos/x/y", {})


def test_refresh_keeps_previous_data_on_failure_and_reports_it():
    routes = {"https://api.github.com/repos/acme/widget": (200, REPO_PAYLOAD)}
    gone = {"stars": 9, "pushed_at": "2025-01-01", "archived": False, "license_spdx": "MIT"}
    existing = {"repos": {"acme/gone": gone}}
    logs = []
    snapshot, failures = refresh(
        ["acme/widget", "acme/gone"],
        existing,
        token=None,
        fetch=fake_fetch(routes),
        now=lambda: datetime(2026, 10, 22, 3, 16, tzinfo=timezone.utc),
        log=logs.append,
    )
    assert snapshot["evaluated_at"] == "2026-10-22T03:16:00Z"
    assert snapshot["repos"]["acme/widget"]["stars"] == 1234
    assert snapshot["repos"]["acme/gone"]["stars"] == 9  # previous value kept
    assert len(failures) == 1 and "acme/gone" in failures[0]
    assert any("warning" in line for line in logs)


def test_get_token_prefers_github_token():
    assert get_token({"GITHUB_TOKEN": "a", "GH_TOKEN": "b"}) == "a"
    assert get_token({"GH_TOKEN": "b"}) == "b"
    assert get_token({}) is None


def test_write_json_atomic(tmp_path):
    target = tmp_path / "sub" / "metrics.json"
    write_json_atomic(target, {"a": 1})
    assert json.loads(target.read_text()) == {"a": 1}
    assert [p.name for p in target.parent.iterdir()] == ["metrics.json"]
