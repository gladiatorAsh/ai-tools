---
name: azure-openai-client
description: Guides correct, production-ready calls to Azure OpenAI in Microsoft Foundry using the v1 API, keyless Entra ID auth, the Responses API, structured outputs, retries and timeouts. Use when adding or changing any code that calls an Azure OpenAI model, embeddings deployment, or OpenAI-compatible Foundry endpoint.
---

# Azure OpenAI Client

## Overview

Azure OpenAI now exposes a **v1 API** at `https://<resource>.openai.azure.com/openai/v1/`. It works with the
standard `OpenAI` client, needs no dated `api-version`, and refreshes Entra ID tokens automatically. Most older
samples (`AzureOpenAI(api_version="2024-...")`) are legacy. This skill makes model calls keyless, typed,
bounded and observable.

Source (verified 2026-10-22): https://learn.microsoft.com/azure/foundry/openai/api-version-lifecycle

## When to Use

- Creating a client, adding a model call, migrating from `AzureOpenAI(...)` or a dated `api-version`.
- Adding structured output, tool calling, streaming or embeddings.
- NOT for agent orchestration logic — see `agent-orchestration-design`.

## Process

1. **Confirm the target.** Get the resource endpoint and the *deployment* name (not the model family name).
   Check with `microsoft-docs` if the feature (e.g. a preview tool type) is in the v1 surface yet.
2. **Create one client per process**, keyless:

   ```python
   from openai import OpenAI
   from azure.identity import DefaultAzureCredential, get_bearer_token_provider

   token_provider = get_bearer_token_provider(
       DefaultAzureCredential(), "https://ai.azure.com/.default"
   )
   client = OpenAI(
       base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1/",
       api_key=token_provider,   # callable -> token fetched and refreshed per request
       timeout=30.0,
       max_retries=3,
   )
   ```

   The identity needs **Cognitive Services OpenAI User** on the resource (see `managed-identity-and-secrets`).
3. **Prefer the Responses API** for Azure OpenAI models (`client.responses.create(model=<deployment>, input=...)`).
   Use `chat.completions` only for other providers' models on the same endpoint or existing code.
4. **Constrain output.** When code consumes the result, request structured output against a Pydantic/JSON schema
   and validate it; on validation failure retry once with the error, then fail loudly.
5. **Bound every call.** Set `timeout`, `max_retries`, and a `max_output_tokens` appropriate to the use case.
   Handle `429` with the SDK's backoff; surface `400` content-filter errors as a distinct, user-safe error.
6. **Make it observable.** Log deployment, latency, input/output token counts and request ID — never the raw
   prompt if it can contain user PII (see `llm-observability`).
7. **Keep configuration out of code.** Endpoint and deployment names come from settings/env; no keys in code.

### .NET

Use the current Azure/OpenAI .NET packages per Microsoft Learn ("Supported programming languages for the v1
API"). Look the exact package and sample up with `microsoft-docs` before writing code — do not reuse pre-v1
`OpenAIClient` samples from memory.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The `AzureOpenAI` class still works" | It does, but the v1 API removes `api-version` churn and is the documented path forward. New code shouldn't add the debt. |
| "API key from env is fine for now" | "For now" ends up in production. A token provider is three lines. |
| "Free-text output is easy to parse" | Regex over prose breaks on the first rephrase. Structured output with validation doesn't. |
| "Default timeouts are fine" | A hung model call holds a worker and a user. Set explicit timeouts and token caps. |

## Red Flags

- `api_version=` or `AzureOpenAI(` in new code without a stated reason.
- A key literal, or `AZURE_OPENAI_API_KEY` read in a service that could use managed identity.
- A new client constructed per request.
- `json.loads(response_text)` with no schema validation or error path.
- Model *name* used where the *deployment* name is required.

## Verification

- [ ] Client uses `/openai/v1/` and a token provider (or a documented exception).
- [ ] Timeout, retries and output-token cap are set explicitly.
- [ ] Structured outputs are schema-validated, with a test for the invalid-output path.
- [ ] A unit test mocks the client; an integration smoke test (skipped without credentials) hits a real deployment.
- [ ] Token usage and latency are logged without raw user content.
