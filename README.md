# AI Tools — Agent Skills for GitHub Copilot

**AI-engineering skills for GitHub Copilot, Azure-first.** Workflows, quality gates and tool know-how for
building LLM, RAG, agent and MCP features — packaged as [Agent Skills](https://agentskills.io) that Copilot loads
on demand in VS Code agent mode, Copilot CLI, the cloud agent and code review.

Modeled on [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), and designed to sit **alongside**
it: Addy's pack covers the general lifecycle (spec, plan, TDD, review, ship); this pack covers what's specific to AI
applications on the Azure stack.

```
  CHOOSE         INGEST          RETRIEVE        CALL / ORCHESTRATE      PROVE            SECURE            OPERATE
 ┌────────┐    ┌─────────┐     ┌──────────┐     ┌──────────────────┐   ┌────────┐      ┌───────────┐     ┌───────────┐
 │ choose │──▶ │document │ ──▶ │ ai-search│ ──▶ │ azure-openai /   │──▶│  llm-  │ ──▶  │ red-team, │ ──▶ │ observe,  │
 │ -ai-   │    │-ingest- │     │   -rag   │     │ agent-orchestra- │   │ evals  │      │ code-     │     │ cost &    │
 │ tool   │    │  ion    │     │          │     │ tion-design      │   │        │      │ review    │     │ latency   │
 └────────┘    └─────────┘     └──────────┘     └──────────────────┘   └────────┘      └───────────┘     └───────────┘
```

## Quick Start

**Copilot CLI — install the whole pack as a plugin:**

```bash
copilot plugin install gladiatorAsh/ai-tools
copilot skill list          # confirm the skills were discovered
```

**VS Code / any Copilot surface — copy skills into a discovery folder:**

```bash
git clone https://github.com/gladiatorAsh/ai-tools.git
ai-tools/scripts/install.sh                       # personal: ~/.copilot/skills (all projects)
ai-tools/scripts/install.sh --project ~/src/app   # project: .github/skills + .github/agents
ai-tools/scripts/install.sh --skill llm-evals     # just one skill
```

**Skill installers:** `gh skill install gladiatorAsh/ai-tools <skill>` (GitHub CLI 2.90+, preview) or
`npx skills add gladiatorAsh/ai-tools`.

Then ask naturally ("add RAG over our policy PDFs") and Copilot picks the skill from its description, or invoke one
by name: `/azure-ai-search-rag`, `/llm-evals`. In VS Code, `/skills` shows what's loaded.

## Skills

### Meta

| Skill | What it does | Use when |
|---|---|---|
| [using-ai-tools-skills](skills/using-ai-tools-skills/SKILL.md) | Routes a task to the right skill; shared rules (Azure-first, verify docs, evals before claims) | Starting any AI feature |
| [choose-ai-tool](skills/choose-ai-tool/SKILL.md) | Recommends tools from a scored catalog of 82 OSS AI tools with verified metrics, licenses and flags | Picking a library, framework, vector DB or eval tool |

### Build on Azure

| Skill | What it does | Use when |
|---|---|---|
| [azure-openai-client](skills/azure-openai-client/SKILL.md) | v1 API, keyless Entra ID auth, Responses API, structured output, bounded calls | Any code that calls Azure OpenAI |
| [azure-ai-search-rag](skills/azure-ai-search-rag/SKILL.md) | Index design, hybrid + semantic ranking, security trimming, citations, when to use agentic retrieval | Building or fixing RAG on Azure AI Search |
| [agent-orchestration-design](skills/agent-orchestration-design/SKILL.md) | Least-autonomy design, tool contracts, approvals, limits, Agent Framework implementation | Designing agents or multi-agent systems |
| [managed-identity-and-secrets](skills/managed-identity-and-secrets/SKILL.md) | Managed identity, data-plane RBAC roles, Key Vault, secrets out of prompts | Connecting a service to Azure resources |
| [fastapi-llm-service](skills/fastapi-llm-service/SKILL.md) | Validated, streamed, cancellable, rate-limited LLM endpoints with offline tests | Exposing an AI feature over HTTP |

### Tool-backed workflows

| Skill | What it does | Use when |
|---|---|---|
| [document-ingestion](skills/document-ingestion/SKILL.md) | Docling / MarkItDown / OCR selection, structure-aware chunking, provenance + ACL metadata | Feeding documents into RAG |
| [llm-evals](skills/llm-evals/SKILL.md) | Golden sets, deterministic checks before LLM judges, promptfoo/DeepEval on Azure, CI regression gates | Changing a prompt, model or retrieval |
| [llm-red-teaming](skills/llm-red-teaming/SKILL.md) | Threat model, garak + promptfoo red team against *your endpoint*, indirect injection, regression cases | Before release or after security-relevant changes |
| [mcp-server-development](skills/mcp-server-development/SKILL.md) | FastMCP / SDK servers with narrow typed tools, auth, least privilege, client tests | Exposing internal tools to agents |
| [llm-observability](skills/llm-observability/SKILL.md) | OpenTelemetry GenAI traces to Azure Monitor, token/cost metrics, redaction, alerts | Shipping or debugging an AI feature |
| [prompt-engineering-and-versioning](skills/prompt-engineering-and-versioning/SKILL.md) | Prompts as versioned files, delimited untrusted input, output contracts, eval-backed edits | Writing or changing a prompt |
| [llm-cost-and-latency](skills/llm-cost-and-latency/SKILL.md) | Per-feature token accounting, trimming, routing, caching, capacity choices | Costs or latency too high |

### Review

| Skill | What it does | Use when |
|---|---|---|
| [code-review-llm-apps](skills/code-review-llm-apps/SKILL.md) | Seven-axis review for injection paths, output sinks, tool authz, data exposure, limits, evidence | Reviewing any AI-feature PR (also used by Copilot code review) |

### Community skills (vendored from [github/awesome-copilot](https://github.com/github/awesome-copilot), MIT)

Reviewed and pinned at commit `26f4f45` — see [vendor/skills.lock.json](vendor/skills.lock.json).

| Skill | Use when |
|---|---|
| [microsoft-agent-framework](skills/microsoft-agent-framework/SKILL.md) | Writing Agent Framework code (.NET or Python) |
| [semantic-kernel](skills/semantic-kernel/SKILL.md) | Maintaining or migrating Semantic Kernel code |
| [microsoft-docs](skills/microsoft-docs/SKILL.md) | Looking up current Azure/.NET/Microsoft APIs via the Learn MCP server |
| [appinsights-instrumentation](skills/appinsights-instrumentation/SKILL.md) | Base Application Insights / OpenTelemetry setup |
| [agent-owasp-compliance](skills/agent-owasp-compliance/SKILL.md) | Checking an agent against the OWASP Agentic Top 10 |
| [mcp-implementation-security-review](skills/mcp-implementation-security-review/SKILL.md) | Security-reviewing MCP server/client code |
| [github-actions-hardening](skills/github-actions-hardening/SKILL.md) | Reviewing workflow files for injection and privilege issues |
| [secret-scanning](skills/secret-scanning/SKILL.md) | Secret scanning, push protection, leaked-secret remediation |

## Agent Personas

Copy into `.github/agents/` (the installer's `--project` mode does this). Copilot only loads `*.agent.md` files.

| Agent | Perspective |
|---|---|
| [ai-solution-architect](agents/ai-solution-architect.agent.md) | Designs AI features: autonomy level, retrieval, identity, eval/red-team/telemetry plan |
| [rag-quality-reviewer](agents/rag-quality-reviewer.agent.md) | Separates ingestion, retrieval and generation failures with evidence |
| [llm-security-reviewer](agents/llm-security-reviewer.agent.md) | Trust boundaries, injection-to-action paths, excessive agency, data leakage |

## Repository Layout

| Path | Purpose |
|---|---|
| `skills/` | One folder per skill (`SKILL.md` + optional `references/`, `scripts/`) |
| `agents/` | Copilot custom agent personas (`*.agent.md`) |
| `plugin.json` | Copilot CLI plugin manifest (skills discovered from `skills/` by convention) |
| `templates/copilot-instructions.md` | Always-on repo instructions that point Copilot at these skills |
| `mcp/` | Pinned MCP server configs that several skills rely on (Microsoft Learn, GitHub, Playwright, ...) |
| `tools-catalog/` | Source data for the `choose-ai-tool` skill: curated catalog, GitHub metrics, methodology |
| `vendor/` | Lock file and license for vendored community skills |
| `src/ai_tools/`, `tests/` | Validator, catalog scorer/renderer, GitHub refresher, vendoring |

## How Skills Are Written

Every original skill follows the same anatomy (from Addy Osmani's
[skill anatomy](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md)):
**Overview → When to Use → Process → Common Rationalizations → Red Flags → Verification**. Skills are workflows with
exit criteria, not reference docs; each is under 500 lines and self-contained, so single-skill installs work.

Facts that change quickly (API shapes, package names, CLI flags) were verified against official docs or source on
2026-10-22 and are marked as such in the skill. Everything else tells Copilot to check current docs via
`microsoft-docs` before writing code.

## Contributing / Maintaining

```bash
pip install -e ".[dev]"
python -m ai_tools validate-skills     # frontmatter, names, links, sections, vendored hashes, agents, plugin.json
pytest -q && ruff check .

python -m ai_tools vendor-sync --ref main   # pull newer community skills, then review `git diff skills/`
python -m ai_tools refresh && python -m ai_tools render   # refresh tool metrics (needs GITHUB_TOKEN)
```

Never edit a vendored skill in place — CI compares it to the pinned upstream hashes. To customize one, copy it to a
new name and drop it from the lock file.
