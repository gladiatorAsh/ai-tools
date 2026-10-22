# Evaluation methodology

**Evaluation date:** 2026-10-22 (UTC) · **Tools scored:** 82 across 13 categories

## Starting point

The `gladiatorAsh/ai-tools` repository was empty (no commits) when this work started, so there was no existing
code, test suite or architecture to integrate tools into. The repository was therefore built as a curated catalog:
the deliverable is a ranked, reproducible shortlist and ready-to-use configurations, not new dependencies of an
application. "Adoption mode" in the catalog describes how each tool should be brought into a typical production AI
application (Python/TypeScript/.NET services calling hosted or self-hosted models).

## How candidates were found

1. GitHub repository search sorted by stars across the `llm`, `ai-agents`, `mcp` and `rag` topics, which surfaced
   roughly 250 repositories.
2. A targeted shortlist per category from the task brief (orchestration, agents, MCP, RAG, vector databases,
   local inference, coding agents, evaluation, document processing, security, workflow automation, UI), adding
   well-known projects that topic search misses (e.g. pgvector, Qdrant, guardrail and eval tools).
3. Exact metadata for each shortlisted repo from `GET /repos/{owner}/{repo}`; for every repo where GitHub reports
   the license as `NOASSERTION`, the LICENSE file itself was read.

## What is verified vs. estimated

| Data | Status | Source |
|---|---|---|
| Stars, forks, open issues+PRs, last push, created date, archived flag, primary language | **Verified** on 2026-10-22 | GitHub REST API |
| License | **Verified** — SPDX from the API; `NOASSERTION` cases resolved by reading LICENSE | GitHub API + LICENSE files |
| Archived / unmaintained status | **Verified** — GitHub archived flag, or the project's own README (AutoGen) | GitHub API, README |
| MCP package names and versions in `mcp/` | **Verified** from each repo's `package.json` | Repository files |
| Latest release tag/date | **Not captured in this snapshot** — filled in by `python -m ai_tools refresh` | GitHub API |
| Recent star growth | **Not measured** — GitHub doesn't expose star history in the API | — |
| Relevance, quality, integration effort | **Estimates** (0–10) by the curator, recorded per tool in `tools-catalog/tools.yaml` | Judgment |
| Security notes | Known, public issues only (e.g. Langflow CVE-2025-3248). Not a security audit — check current advisories before deploying | Public advisories |

## Scoring

Each factor is normalised to 0–10, then weighted:

| Factor | Weight | How it's computed |
|---|---:|---|
| Relevance to production AI apps | 30% | Estimate |
| Technical quality & capabilities | 20% | Estimate |
| Community adoption | 15% | `log10(stars)` mapped so 1k stars → 0 and 150k stars → 10 (log scale so 150k isn't 150× better than 1k) |
| Maintenance | 15% | 10 if pushed within 30 days, falling linearly to 0 at 365 days; archived → 0 |
| Security & license | 10% | permissive 10, open-core 8, model license 5, source-available 4, copyleft 3, minus a documented `security_penalty` |
| Integration effort & operating cost | 10% | Estimate; 10 = `pip`/`npm` install, low = multi-service infrastructure |

The code is in [`src/ai_tools/scoring.py`](../src/ai_tools/scoring.py) and is unit-tested. Change the weights there
and re-run `python -m ai_tools render` to see a different ranking.

## Adoption modes

- **Library** — add as a dependency.
- **Service** — run it (or use its hosted API) and connect over the network.
- **MCP server** — plug into MCP-capable agents/IDEs; configs in [`mcp/`](../mcp/README.md).
- **Dev tool** — use during development/CI only; not shipped in the app.
- **PoC first** — promising but heavier or less proven; prototype against your own data before committing.
- **Rejected** — kept in the table with a reason.

## Rejected and flagged

| Tool | Decision | Reason |
|---|---|---|
| microsoft/autogen | Rejected | README declares it archived and unmaintained — no bug or security fixes. Microsoft directs new users to Agent Framework. (GitHub's archived flag is not set.) |
| FlowiseAI/Flowise | Rejected | Archived on GitHub (last push 2026-08-13). |
| Chainlit/chainlit | Rejected | Archived on GitHub. |
| protectai/llm-guard | Rejected | Archived on GitHub. |
| FoundationAgents/MetaGPT | Rejected | No push since 2026-01-21; research-oriented. |
| vibrantlabsai/ragas | Flagged | Moved from explodinggradients/ragas; no push since 2026-02-24. |
| Aider-AI/aider | Flagged | No push since 2026-05-22. |
| langflow-ai/langflow | Flagged | Critical unauthenticated RCE in 2025 (CVE-2025-3248); keep patched, never expose without auth. |
| n8n, Dify, Open WebUI, Phoenix | Flagged (license) | Source-available terms restrict resale/hosting or branding removal — fine for internal use, check before shipping a product. |
| firecrawl | Flagged (license) | AGPL-3.0 for self-hosted modified copies. |

### Seen in discovery but not shortlisted

Topic search also returned many very high-star repositories that are outside this catalog's scope or that could
not be assessed with verifiable track records in this pass:

- **Learning material, prompt collections and awesome-lists** (e.g. LLMs-from-scratch, llm-course, prompts.chat,
  Prompt-Engineering-Guide, awesome-mcp-servers, awesome-llm-apps). Useful, but not tools.
- **End-user applications in a single domain** (e.g. trading agents, video generators, stock analysis).
- **Repositories publishing leaked system prompts** — excluded on licensing and ethics grounds.
- **Very recent agent harnesses and skill packs with six-figure star counts** (e.g. morluto/rea, affaan-m/ECC,
  NousResearch/hermes-agent, DietrichGebert/ponytail, Graphify-Labs/graphify). Not evaluated here. Rapid star
  growth alone isn't evidence of quality; assess maintainers, release history and code before adopting.

## Limitations

- Estimates reflect one curator's judgment of general production value; weight relevance to your own stack.
- A score is a starting point for a shortlist, not a substitute for a proof of concept on your data.
- Metrics drift daily; the weekly refresh workflow keeps the measured factors current.
