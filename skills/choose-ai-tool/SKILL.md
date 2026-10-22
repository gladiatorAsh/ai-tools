---
name: choose-ai-tool
description: Recommends open-source AI libraries, frameworks, MCP servers, vector stores, eval and guardrail tools using a scored catalog of 82 tools with verified GitHub metrics, licenses and risk flags, filtered for an Azure-first stack. Use when deciding which library, framework or service to adopt for an AI feature, comparing alternatives, or checking whether a tool is maintained and safely licensed.
---

# Choose an AI Tool

## Overview

Picking tools by GitHub stars leads to archived projects, restrictive licenses and duplicate frameworks. This
skill answers "what should we use for X?" from [references/ai-tools-catalog.md](references/ai-tools-catalog.md):
82 tools across 13 categories, scored on relevance (30%), quality (20%), adoption (15%), maintenance (15%),
license/security (10%) and integration effort (10%), with archived and unmaintained projects explicitly rejected.

## When to Use

- "Which vector DB / eval tool / agent framework / document parser should we use?"
- Before adding any new AI dependency.
- When someone proposes a tool you haven't vetted (check its row and flags).
- NOT for Microsoft-specific API details — use `microsoft-docs`.

## Process

1. **Restate the need** in one line: capability, language, hosting constraint (Azure-only? self-hosted?),
   license constraint (commercial product? internal only?).
2. **Check whether the Azure stack already covers it.** Azure OpenAI, Azure AI Search, Agent Framework, Document
   Intelligence and Azure Monitor cover many needs inside one trust boundary. A new tool needs a reason the Azure
   option doesn't meet.
3. **Open the catalog** at [references/ai-tools-catalog.md](references/ai-tools-catalog.md) and read the category
   table. Note score, last push, license and flags (⚠️) for the top 2–3 options.
4. **Apply hard filters:** reject archived/unmaintained (`Rejected` rows); for a product you will distribute or
   host for others, avoid `source-available` and `copyleft` licenses unless legal approves; respect `security`
   flags.
5. **Recommend one option plus one alternative**, with: why it fits, adoption mode (library / service / MCP /
   dev tool / PoC first), license note, and the first integration step. If a PoC is required, define the success
   metric (usually an eval from `llm-evals`).
6. **Mind the snapshot date.** Metrics in the catalog are from the date at its top. For a decision that matters,
   re-check the repository's last commit, latest release and open security advisories.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It has the most stars" | AutoGen and Flowise have tens of thousands of stars and are archived. Check maintenance. |
| "It's open source, so we can use it" | n8n, Dify, Open WebUI and Phoenix carry source-available terms that restrict hosting or resale. |
| "Let's add LangChain just in case" | A framework you don't need is permanent surface area. Start with the SDK. |

## Red Flags

- Recommending a `Rejected` or archived tool.
- Adding a second framework that duplicates one already in the codebase.
- A license check skipped for a tool that will ship in a product.

## Verification

- [ ] Recommendation cites the catalog row (score, license, last push) and any flags.
- [ ] The Azure-native alternative was considered and the reason for a third-party tool is stated.
- [ ] For decisions that matter, current maintenance and advisories were re-checked.
