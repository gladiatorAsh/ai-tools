# Tools catalog (source data for `choose-ai-tool`)

- [`tools.yaml`](tools.yaml) — hand-curated entries: category, adoption mode, estimates, license notes, risk flags.
- [`metrics.json`](metrics.json) — GitHub API snapshot (stars, last push, archived, license, latest release).
- [`EVALUATION.md`](EVALUATION.md) — scoring method, what is verified vs estimated, rejections.

The rendered, ranked catalog lives inside the skill so it ships with single-skill installs:
[`skills/choose-ai-tool/references/ai-tools-catalog.md`](../skills/choose-ai-tool/references/ai-tools-catalog.md).

```bash
export GITHUB_TOKEN=...            # read-only token; see .env.example
python -m ai_tools refresh         # update metrics.json from the GitHub API
python -m ai_tools render          # regenerate the skill's catalog reference
python -m ai_tools validate        # catalog <-> metrics consistency
```

A [weekly workflow](../.github/workflows/refresh.yml) runs the refresh and opens a PR. It needs *Settings →
Actions → General → Allow GitHub Actions to create and approve pull requests* enabled.
