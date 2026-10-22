---
name: azure-ai-search-rag
description: Guides design and implementation of retrieval-augmented generation on Azure AI Search - index schema, chunking, hybrid (keyword + vector) search with semantic ranking, security trimming, grounding prompts, citations, and when to use agentic retrieval. Use when building or changing a RAG pipeline, search index, or grounding step backed by Azure AI Search.
---

# Azure AI Search RAG

## Overview

Good RAG is mostly retrieval quality. On Azure AI Search the reliable default is **hybrid search (BM25 + vector)
with the semantic ranker** over well-chunked documents carrying metadata for filtering and security trimming.
**Agentic retrieval** (knowledge bases + knowledge sources) adds LLM query planning for multi-part or
conversational questions at extra latency and token cost.

Sources (verified 2026-10-22): https://learn.microsoft.com/azure/search/agentic-retrieval-overview ,
https://learn.microsoft.com/azure/search/search-relevance-overview

## When to Use

- Designing a new index or RAG pipeline; changing chunking, embeddings, ranking or prompts that use retrieved text.
- Answers are wrong, uncited, or miss documents you know exist.
- NOT for converting source files to text — use `document-ingestion` first.

## Process

1. **Write down the questions.** Collect 20–50 real user questions with the document(s) that answer each. This
   becomes the retrieval eval set (`llm-evals`). Without it, every later step is guesswork.
2. **Design the index schema.**
   - `id` (key), `content` (searchable text), `content_vector` (vector field, dimensions = embedding model),
     `title`, `source_url`/`path`, `chunk_index`, `last_modified`, and filterable metadata (product, region, doc type).
   - A **security field** (e.g. `allowed_groups`, filterable) when users must only see what they're entitled to.
   - A **semantic configuration** naming title and content fields.
   - Prefer **integrated vectorization** (a vectorizer on the index) so queries can be vectorized server-side.
3. **Chunk deliberately.** Start with structure-aware chunks (headings/sections) of a few hundred tokens with
   modest overlap; keep tables whole. Store the parent document reference so answers can cite it.
4. **Query with hybrid + semantic ranking** as the baseline:

   ```python
   from azure.search.documents import SearchClient
   from azure.search.documents.models import VectorizableTextQuery

   results = search_client.search(
       search_text=question,
       vector_queries=[VectorizableTextQuery(text=question, k_nearest_neighbors=50, fields="content_vector")],
       query_type="semantic",
       semantic_configuration_name="default",
       filter=security_filter,          # e.g. "allowed_groups/any(g: search.in(g, 'grp1,grp2'))"
       select=["id", "title", "content", "source_url"],
       top=5,
   )
   ```

   Authenticate the `SearchClient` with `DefaultAzureCredential` (role: *Search Index Data Reader*).
5. **Ground and cite.** Put retrieved chunks in a clearly delimited context block, instruct the model to answer only
   from it and to cite chunk IDs/URLs, and to say it doesn't know when context is insufficient. Treat retrieved
   text as untrusted (it can contain injected instructions).
6. **Decide on agentic retrieval** only if the eval set shows multi-part or conversational questions failing with
   single-query hybrid search. Use the GA REST API (`2026-04-01`) for production; LLM query planning and answer
   synthesis are preview-only at the time of writing — check `microsoft-docs` before relying on them.
7. **Measure.** Report retrieval metrics (hit rate / recall@k on the question set) separately from answer metrics
   (groundedness, correctness) so you know which half to fix.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Vector search alone is enough" | Pure vectors miss exact terms: product codes, error IDs, names. Hybrid fixes this cheaply. |
| "We'll add security trimming later" | Retrofitting ACLs means re-indexing everything and an incident if it ships without. |
| "Bigger chunks give the model more context" | They dilute relevance and burn tokens. Tune chunk size against the eval set. |
| "Agentic retrieval is newer, so better" | It costs more and is slower. Use it where single-query retrieval measurably fails. |
| "The model will ignore irrelevant chunks" | It often blends them in. Return fewer, better chunks. |

## Red Flags

- No retrieval eval set; quality judged by trying a few questions by hand.
- Search admin keys in application code (use RBAC; admin keys only for provisioning, if at all).
- Index without a filterable security field in a multi-user app.
- Prompts that don't require citations or allow answering without context.
- Re-embedding the corpus with a new model without re-running the retrieval eval.

## Verification

- [ ] Retrieval eval set exists with expected source documents; recall@5 is reported.
- [ ] Queries use hybrid + semantic ranking (or a measured reason not to).
- [ ] Security trimming is enforced in the query filter and covered by a test with two different users.
- [ ] Answers include citations that resolve to real chunks.
- [ ] Search access is keyless (RBAC), and the index schema is in source control.
