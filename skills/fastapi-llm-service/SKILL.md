---
name: fastapi-llm-service
description: Guides building HTTP endpoints for LLM features in FastAPI - request validation and size limits, streaming responses over SSE, timeouts and cancellation, typed responses, rate limiting, error mapping, and testing with a mocked model client. Use when exposing a model, RAG or agent capability as an API in a Python/FastAPI service.
---

# FastAPI LLM Service

## Overview

LLM endpoints fail differently from CRUD endpoints: they are slow, expensive, streaming, rate-limited upstream and
return untrusted content. This skill makes them bounded, cancellable, typed and testable.

## When to Use

- Adding or changing a FastAPI route that calls a model, search or agent.
- Adding streaming, or fixing timeouts, 429s or runaway costs at the API layer.
- NOT for the model call itself (`azure-openai-client`) or retrieval (`azure-ai-search-rag`).

## Process

1. **Validate input at the edge.** Pydantic request models with `max_length` on free text, bounded list sizes,
   and an allowlist for any model/deployment selector. Reject before spending tokens.
2. **Inject dependencies.** Create the model/search clients once (lifespan) and provide them via `Depends`, so
   tests can override them. Never construct clients per request.
3. **Choose response mode.**
   - Short, structured results → regular JSON response with a typed `response_model`.
   - Long generations → `StreamingResponse` with `text/event-stream`; send an explicit terminal event and an error
     event format. Stop generating when the client disconnects (check `await request.is_disconnected()`).
4. **Bound everything.** Per-request timeout around the model call, token caps, and per-user/tenant rate limits.
   Map upstream `429` to `429` with `Retry-After`, timeouts to `504`, content-filter blocks to a safe `4xx` message.
5. **Authenticate and authorize** every route (Entra ID / your auth); pass the caller's identity to retrieval for
   security trimming. Never trust a client-sent user ID.
6. **Don't leak internals.** Error responses carry a correlation ID, not stack traces, prompts or upstream bodies.
7. **Test with fakes.** Unit tests override the model dependency with a fake returning canned (and malformed)
   outputs; one integration test streams end-to-end against a local fake.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Input length doesn't matter, the model truncates" | You pay for every token first, and huge inputs are a cheap DoS. |
| "Streaming is just a generator" | Without disconnect handling you keep paying for output nobody reads. |
| "Return the upstream error, it's more informative" | Upstream bodies can echo prompts, deployment names or keys. |

## Red Flags

- `str` request fields with no `max_length`; unbounded lists of documents/messages.
- Clients created inside the route function.
- `except Exception: return {"error": str(e)}`.
- Streaming endpoint with no terminal/error event and no disconnect check.
- No test that runs without network/credentials.

## Verification

- [ ] Oversized input is rejected with `422` before any model call (test proves no client call happened).
- [ ] Upstream 429/timeout/content-filter each map to a defined status (tests for each).
- [ ] Streaming stops on client disconnect (test or manual evidence).
- [ ] All routes require auth; identity flows into retrieval filters.
- [ ] Test suite passes offline with the model dependency overridden.
