---
name: llm-cost-and-latency
description: Guides measuring and reducing LLM cost and latency without losing quality - per-feature token accounting, model right-sizing and routing, prompt and context trimming, caching, streaming, batching, and capacity choices on Azure (pay-as-you-go vs provisioned). Use when AI costs or response times are too high, before scaling a feature, or when choosing a deployment type.
---

# LLM Cost and Latency

## Overview

Cost and latency are mostly tokens and model choice. Measure per feature first, then cut tokens, right-size the
model, and cache — verifying each change against the eval suite so quality doesn't silently drop.

## When to Use

- The bill or p95 latency is above target, or a feature is about to scale.
- Choosing between models/deployment types or adding caching.
- NOT before you have per-feature measurements — set those up with `llm-observability` first.

## Process

1. **Measure.** Per feature: requests, input/output tokens, cache hits, p50/p95 latency, cost. Find the top two
   contributors; optimize those only.
2. **Cut input tokens.** Trim system prompts, send fewer/shorter retrieved chunks (tune top-k against the eval
   set), summarize long conversation history, remove unused tool definitions.
3. **Cap output tokens** to what the UI uses; ask for concise structured output.
4. **Right-size the model.** Run the eval suite on a smaller/cheaper deployment; route easy or classified requests
   to it and keep the larger model for hard cases. Keep the routing rule testable.
5. **Cache.** Use provider prompt caching for long stable prefixes (stable content first). Add an application cache
   for repeated deterministic requests (embeddings of identical text, FAQ-style answers) keyed on normalized input
   + prompt version + model; respect tenant isolation in cache keys.
6. **Hide latency.** Stream responses; run independent retrieval/tool calls concurrently; batch offline work
   (ingestion, embeddings, evals) via batch APIs where available.
7. **Capacity.** Compare pay-as-you-go vs provisioned throughput using your measured steady-state tokens per
   minute and latency needs; check current Azure pricing and quota docs with `microsoft-docs` before deciding.
8. **Re-run evals** after every change; reject savings that cost quality on critical cases.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Use the biggest model to be safe" | Many tasks score the same on a smaller model at a fraction of the cost. The eval suite decides. |
| "Caching LLM responses is risky" | Cache deterministic, tenant-scoped requests keyed on prompt version; leave the rest uncached. |
| "We'll optimize after launch" | Launch traffic sets the bill. Measure before scaling. |

## Red Flags

- No per-feature cost attribution.
- Top-k of 20+ chunks "for safety" with no recall measurement.
- Cache keys missing tenant or prompt version.
- Model downgrades shipped without an eval comparison.

## Verification

- [ ] Before/after cost and latency per feature are reported from telemetry.
- [ ] Eval suite shows no regression on critical cases for each optimization.
- [ ] Cache keys include tenant, prompt version and model; a test proves tenant isolation.
- [ ] Output-token caps and streaming are in place for user-facing endpoints.
