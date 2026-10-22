---
name: code-review-llm-apps
description: Reviews pull requests that touch prompts, model calls, retrieval, agents, tools or MCP servers for LLM-specific risks - prompt injection paths, untrusted model output reaching sinks, missing authorization in tools, secrets or PII in context, unbounded cost, missing evals and telemetry. Use when reviewing or self-reviewing any change to an AI feature, including in Copilot code review.
---

# Code Review for LLM Applications

## Overview

General code review misses the failure modes unique to AI features: text from users, documents and tools that
can steer the model, model output that flows into code paths, and quality changes that only evals reveal. Review
each change along the axes below; findings carry a severity and a concrete fix.

## When to Use

- Any PR changing prompts, model/deployment config, retrieval, agent logic, tools or MCP servers.
- Before merging AI-generated code that calls models.
- Pair with a general code-review skill for correctness, style and tests.

## Process

Walk the change along these axes, in order:

1. **Trust boundaries.** Where does untrusted text enter (user input, retrieved docs, web pages, tool outputs,
   file uploads)? Is it delimited and treated as data in prompts? Can it reach a tool with side effects without
   authorization in code?
2. **Output handling.** Does model output reach SQL, shell, `eval`, file paths, URLs (SSRF), HTML (XSS) or
   another model's instructions without validation/encoding? Is structured output schema-validated?
3. **Tool and agent permissions.** Least-privilege identity? Authorization checked inside each tool against the
   *end user*, not the agent? Approval for irreversible actions? Turn/token/time limits?
4. **Data exposure.** Secrets, internal URLs, other tenants' data or unnecessary PII in prompts, context, logs
   or traces? Security trimming on retrieval?
5. **Credentials and config.** Keyless auth (`managed-identity-and-secrets`)? v1 Azure OpenAI client
   (`azure-openai-client`)? Deployment names and limits from config?
6. **Cost and resilience.** Input size limits, output token caps, timeouts, retries with backoff, rate limits,
   streaming disconnect handling.
7. **Evidence.** For prompt/model/retrieval changes: eval results attached (`llm-evals`)? New behavior covered by
   eval cases? Telemetry for new calls (`llm-observability`)?

### Severity

| Label | Meaning |
|---|---|
| **Blocker** | Exploitable injection-to-action path, data/tenant leak, secret exposure, or unvalidated output into a dangerous sink |
| **Major** | Missing authorization/limits, no eval evidence for a behavior change, keys where identity is possible |
| **Minor** | Telemetry gaps, prompt structure, maintainability |
| **Nit** | Style |

Report as: `[Severity] file:line — problem — impact — fix`.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The prompt tells the model not to do that" | Prompts are bypassable. Require a code-level control. |
| "It's only reading data" | Read paths leak data across users and feed injection into later steps. |
| "Evals are a separate task" | Without them the reviewer can't know whether the change helped or hurt. Ask for them. |

## Red Flags

- Model output concatenated into a query, command or HTML.
- Tool functions with no reference to the caller's identity.
- `temperature`, model or prompt changes with no eval link.
- Broad `try/except` that returns upstream error text to users.

## Verification

- [ ] Every axis above was checked; findings list severity, location and fix.
- [ ] No Blocker remains open at merge.
- [ ] Behavior changes have linked eval results or an explicit, justified waiver.
