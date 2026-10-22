---
name: llm-observability
description: Guides instrumenting LLM, RAG and agent applications with OpenTelemetry - traces spanning request, retrieval, model and tool calls, GenAI semantic-convention attributes, token and cost metrics, redaction of prompts and PII, export to Azure Monitor / Application Insights, and alerts. Use when adding telemetry to an AI feature, debugging a bad answer in production, or tracking AI cost and latency.
---

# LLM Observability

## Overview

When an AI answer is wrong in production you need to see the whole chain: the request, what was retrieved, the
exact prompt version, the model response, every tool call, tokens and latency. Instrument with **OpenTelemetry**
using the **GenAI semantic conventions**, export to **Azure Monitor/Application Insights** (stays in Azure), and
redact content by default. Note: the GenAI conventions are still not marked stable — pin instrumentation versions
and expect attribute renames.

## When to Use

- Shipping any AI feature to users; adding retrieval, tools or agents to an existing one.
- Debugging "why did it say that?" or unexplained cost/latency spikes.
- For base App Insights setup on an app, use the `appinsights-instrumentation` skill first.

## Process

1. **Base setup.** Configure the Azure Monitor OpenTelemetry distro for your runtime (see
   `appinsights-instrumentation`); connection string from config, auth via managed identity where supported.
2. **One trace per user request** with child spans: retrieval (query, top-k, latency, returned doc IDs),
   each model call, each tool call, post-processing. Agent Framework and the OpenAI SDK have OpenTelemetry
   instrumentation — enable it rather than hand-rolling spans where available (check current docs).
3. **Record GenAI attributes** on model spans: provider/system, request model (deployment), response model,
   input/output token counts, finish reason, and your own `prompt.version` and feature name.
4. **Redact by default.** Do not record prompt/completion text in production unless a documented need exists; if
   you must, sample, mask PII, restrict access, and set short retention. Never log credentials or full retrieved
   documents.
5. **Metrics that matter:** latency p50/p95 per feature, tokens and estimated cost per request/tenant/feature,
   error rate by type (429, timeout, content filter), tool-call failure rate, "I don't know" rate for RAG.
6. **Alert on symptoms**, not causes: p95 latency, error rate, cost per hour above budget, sudden drop in
   retrieval hits.
7. **Close the loop.** Make it possible to turn a trace into an eval case (capture inputs + expected outcome),
   feeding `llm-evals`.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We log the prompt and response, that's enough" | Logs without retrieval/tool spans can't explain *why*; full-text logs also create a PII store. |
| "Token counts are on the Azure bill" | The bill can't tell you which feature or tenant spent it. |
| "Semantic conventions will change, so skip them" | Pin versions and use them; renaming attributes later is cheap compared to having none. |

## Red Flags

- Raw prompts/completions in logs by default; no retention policy.
- No token or cost metrics per feature.
- Model and tool calls not linked under one trace ID.
- Alerts only on infrastructure metrics (CPU), none on AI-specific failures.

## Verification

- [ ] A single request shows retrieval, model and tool spans under one trace in Application Insights.
- [ ] Token counts and deployment name are recorded per model call; prompt version is tagged.
- [ ] Content capture is off (or sampled, masked and justified); a test asserts no PII field is emitted.
- [ ] Dashboards/alerts exist for latency, errors and cost.
