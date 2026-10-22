---
name: using-ai-tools-skills
description: Maps an AI-engineering task to the right skill in this pack and sets the shared operating rules (Azure-first, verify against live docs, evals before claims). Use when starting work on an LLM, RAG, agent or MCP feature, or when unsure which skill applies.
---

# Using the AI Tools Skills

## Overview

This pack covers building production AI applications, defaulting to the Azure stack (Azure OpenAI in Microsoft
Foundry, Azure AI Search, Microsoft Agent Framework) with open-source tools for evaluation, red-teaming,
ingestion and MCP. It complements general engineering packs (spec, TDD, code review); it does not replace them.

## When to Use

- At the start of any AI feature: pick the skill(s) before writing code.
- When a request spans several areas (e.g. "add RAG with evals") and you need an order of operations.
- NOT for general web/backend work with no model, retrieval or agent component.

## Routing Table

| The task involves... | Use |
|---|---|
| Calling a model (chat, Responses API, embeddings, structured output) | `azure-openai-client` |
| Retrieval, indexing, chunk search, grounding answers in documents | `azure-ai-search-rag` (+ `document-ingestion` for the pipeline in) |
| Turning PDFs/Office files into clean text for RAG | `document-ingestion` |
| Agents, tools, multi-step or multi-agent workflows | `agent-orchestration-design`, then `microsoft-agent-framework` for the API |
| Legacy Semantic Kernel code | `semantic-kernel` (and its migration notes) |
| Credentials, keys, RBAC, Key Vault | `managed-identity-and-secrets` |
| Exposing an LLM feature over HTTP | `fastapi-llm-service` |
| Writing or changing a prompt | `prompt-engineering-and-versioning` |
| "Is it good?" — quality measurement, regression tests | `llm-evals` |
| "Is it safe?" — jailbreaks, prompt injection, data leakage | `llm-red-teaming`, `agent-owasp-compliance` |
| Building an MCP server | `mcp-server-development`, then `mcp-implementation-security-review` |
| Tracing, token/cost metrics, dashboards | `llm-observability`, `appinsights-instrumentation` |
| Cost or latency problems | `llm-cost-and-latency` |
| Reviewing a PR that touches prompts, model calls or agents | `code-review-llm-apps` |
| Picking a library/framework/vector DB | `choose-ai-tool` |
| Any Azure/.NET/Microsoft API detail | `microsoft-docs` |
| GitHub Actions workflows or secret leaks | `github-actions-hardening`, `secret-scanning` |

## Typical Order for a New AI Feature

```
choose-ai-tool → (document-ingestion → azure-ai-search-rag) → azure-openai-client
      → prompt-engineering-and-versioning → llm-evals → llm-red-teaming
      → llm-observability → code-review-llm-apps
```

## Shared Operating Rules

1. **Azure-first, single trust boundary.** Default to Azure-hosted models, search and identity. Introduce a
   third-party SaaS or a new framework only when the Azure option can't meet a stated requirement — and say why.
2. **Verify, don't recall.** Azure AI SDKs and preview APIs change monthly. Before writing non-trivial API code,
   check current docs with the `microsoft-docs` skill (Microsoft Learn MCP: `https://learn.microsoft.com/api/mcp`).
   State the doc URL you relied on.
3. **Keyless by default.** Entra ID (managed identity / `DefaultAzureCredential`) over API keys, always.
4. **Evals before claims.** "The answers look better" is not evidence. A prompt, model or retrieval change ships
   with an eval result (`llm-evals`).
5. **Model output is untrusted input.** Never pass it to a shell, SQL, `eval`, file paths or HTML without validation.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I know this SDK, no need to check docs" | Azure OpenAI moved to the v1 API and Agent Framework replaced AutoGen in the last year. Memory is stale by default. |
| "It's a prototype, skip evals" | Prototypes become production. A 20-case eval set takes an hour and catches regressions forever. |
| "An API key is quicker" | Keys leak and don't expire. Managed identity is one role assignment. |

## Red Flags

- Code written against `AzureOpenAI(api_version=...)` with no reason to avoid the v1 API.
- A new vector database, orchestration framework or SaaS added without a one-line justification.
- A prompt change merged with no eval run attached.

## Verification

- [ ] The skill(s) used are named in the plan or PR description.
- [ ] Any non-trivial Azure API usage cites a current doc URL.
- [ ] Credentials are keyless or the exception is documented.
