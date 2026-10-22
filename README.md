# ai-tools

A curated, scored catalog of the most useful open-source AI tools for building production AI applications —
frameworks, agents, MCP servers, RAG, vector stores, inference, evaluation, document processing, guardrails and UI.

Stars alone don't make the list. Each tool is scored on six weighted factors; two are measured from the GitHub API
(adoption, maintenance), one combines the verified license with known security concerns, and three are documented
judgment calls (relevance, quality, integration effort). Archived or declared-unmaintained projects are kept in the
table, scored, and explicitly rejected, so you can see *why* a popular name isn't recommended.

- **Catalog (hand-curated):** [`catalog/tools.yaml`](catalog/tools.yaml)
- **Metrics snapshot (from the GitHub API):** [`data/metrics.json`](data/metrics.json)
- **Methodology, sources and rejections:** [`docs/EVALUATION.md`](docs/EVALUATION.md)
- **Ready-to-use MCP server configs:** [`mcp/`](mcp/README.md)

## Usage

```bash
pip install -e ".[dev]"

python -m ai_tools validate          # schema + metrics consistency checks
python -m ai_tools score             # ranked list in the terminal (--json for machine-readable)
python -m ai_tools render            # regenerate the tables below from the catalog + metrics

export GITHUB_TOKEN=...              # read-only token; see .env.example
python -m ai_tools refresh           # pull fresh stars / last push / archived / latest release
```

A [weekly workflow](.github/workflows/refresh.yml) refreshes the metrics and opens a pull request. For it to open PRs,
enable *Settings → Actions → General → Allow GitHub Actions to create and approve pull requests*.

### Adding a tool

1. Add an entry to `catalog/tools.yaml` (the header documents every field; a rejection needs a `reason`).
2. Run `python -m ai_tools refresh` to fetch its metrics.
3. Run `python -m ai_tools render`, then `pytest`.

<!-- BEGIN GENERATED: do not edit by hand, run `python -m ai_tools render` -->

_Metrics snapshot: **2026-10-22T03:16:00Z** (UTC). 82 tools scored. Weights: relevance 30%, quality 20%, adoption 15%, maintenance 15%, license security 10%, integration 10%._

## Top pick per category

| Category | Pick | Score | Stars | Adopt as |
|---|---|---:|---:|---|
| LLM frameworks & orchestration | [llama_index](https://github.com/run-llama/llama_index) | 8.39 | 52.6k | Library |
| Agents & multi-agent systems | [langgraph](https://github.com/langchain-ai/langgraph) | 8.83 | 43.7k | Library |
| Agent memory & knowledge graphs | [mem0](https://github.com/mem0ai/mem0) | 8.06 | 67.6k | PoC first |
| Model Context Protocol (servers, SDKs) | [python-sdk](https://github.com/modelcontextprotocol/python-sdk) | 8.86 | 24.6k | Library |
| RAG, hybrid search & reranking | [ragflow](https://github.com/infiniflow/ragflow) | 7.96 | 92.6k | PoC first |
| Vector databases & retrieval stores | [pgvector](https://github.com/pgvector/pgvector) | 8.54 | 23.4k | Service |
| Local & self-hosted inference | [ollama](https://github.com/ollama/ollama) | 9.20 | 184.2k | Dev tool |
| Coding agents & AI dev tools | [codex](https://github.com/openai/codex) | 8.86 | 130.3k | Dev tool |
| Evaluation, observability & tracing | [promptfoo](https://github.com/promptfoo/promptfoo) | 8.68 | 26.2k | Dev tool |
| Document processing & extraction | [markitdown](https://github.com/microsoft/markitdown) | 9.10 | 191.5k | Library |
| Security, guardrails & red teaming | [garak](https://github.com/NVIDIA/garak) | 7.98 | 9.6k | Dev tool |
| Workflow automation, browsing & crawling | [crawl4ai](https://github.com/unclecode/crawl4ai) | 8.63 | 86.0k | Library |
| UI & AI application frameworks | [ai](https://github.com/vercel/ai) | 8.49 | 27.4k | Library |

## Ranked catalog

### LLM frameworks & orchestration

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [llama_index](https://github.com/run-llama/llama_index) | 8.39 | 52.6k | 2026-10-21 | MIT | Library | Data framework for ingesting, indexing and querying documents with LLMs. |
| 2 | [pydantic-ai](https://github.com/pydantic/pydantic-ai) | 8.31 | 20.8k | 2026-10-22 | MIT | Library | Type-safe agent framework from the Pydantic team with structured outputs end to end. |
| 3 | [semantic-kernel](https://github.com/microsoft/semantic-kernel) | 8.30 | 28.7k | 2026-10-21 | MIT | Library | Microsoft SDK for LLM orchestration with first-class C#/.NET, Python and Java. |
| 4 | [langchain](https://github.com/langchain-ai/langchain) | 8.20 | 148.2k | 2026-10-22 | MIT | Library | Broad LLM framework - model/tool abstractions, hundreds of integrations, agent building blocks. ⚠️ Large API surface - pin versions and isolate behind your own interfaces |
| 5 | [litellm](https://github.com/BerriAI/litellm) | 8.13 | 61.8k | 2026-10-22 | NOASSERTION (open-core) † | Service | OpenAI-format SDK and gateway for 100+ LLM APIs with cost tracking, fallbacks and rate limits. † License: MIT outside enterprise/; enterprise/ is under a separate commercial license. ⚠️ Very high open issue+PR count (5.5k) - review release notes before upgrades |
| 6 | [dspy](https://github.com/stanfordnlp/dspy) | 7.89 | 38.7k | 2026-10-21 | MIT | PoC first | Programming (not prompting) LMs - declarative modules with automatic prompt/weight optimization. |
| 7 | [haystack](https://github.com/deepset-ai/haystack) | 7.88 | 26.8k | 2026-10-21 | Apache-2.0 | Library | Pipeline-based orchestration for RAG, search and agents with explicit components. |

### Agents & multi-agent systems

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [langgraph](https://github.com/langchain-ai/langgraph) | 8.83 | 43.7k | 2026-10-22 | MIT | Library | Stateful, graph-based agent runtime with checkpointing, streaming and human-in-the-loop. |
| 2 | [openai-agents-python](https://github.com/openai/openai-agents-python) | 8.42 | 30.2k | 2026-10-22 | MIT | Library | Lightweight multi-agent SDK with handoffs, guardrails and built-in tracing. |
| 3 | [agent-framework](https://github.com/microsoft/agent-framework) | 8.40 | 14.3k | 2026-10-21 | MIT | Library | Microsoft's agent and multi-agent workflow framework for Python and .NET (successor to AutoGen). |
| 4 | [crewAI](https://github.com/crewAIInc/crewAI) | 8.03 | 60.0k | 2026-10-21 | MIT | Library | Role-based multi-agent orchestration (crews of agents with tasks and processes). |
| 5 | [adk-python](https://github.com/google/adk-python) | 7.82 | 22.0k | 2026-10-22 | Apache-2.0 | Library | Google's code-first Agent Development Kit with built-in evaluation and deployment. |
| 6 | [agno](https://github.com/agno-agi/agno) | 7.52 | 42.9k | 2026-10-21 | Apache-2.0 | PoC first | Agent framework plus runtime and control plane for running agent platforms. |
| 7 | [autogen](https://github.com/microsoft/autogen) | 6.33 | 61.5k | 2026-10-16 | CC-BY-4.0 † | Rejected | Microsoft Research multi-agent framework. **Rejected:** README states the project is archived and no longer maintained (no security fixes). Use microsoft/agent-framework instead. † License: Code under MIT (LICENSE-CODE); docs under CC-BY-4.0, which is what GitHub reports. ⚠️ Declared unmaintained in README |
| 8 | [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | 5.58 | 71.0k | 2026-01-21 | MIT | Rejected | Multi-agent framework that simulates a software company. **Rejected:** No commits since 2026-01-21 and research-oriented; general-purpose frameworks above cover the need. ⚠️ No push in ~9 months |

### Agent memory & knowledge graphs

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [mem0](https://github.com/mem0ai/mem0) | 8.06 | 67.6k | 2026-10-21 | Apache-2.0 | PoC first | Drop-in long-term memory layer for agents and assistants. |
| 2 | [graphiti](https://github.com/getzep/graphiti) | 7.84 | 32.1k | 2026-10-21 | Apache-2.0 | PoC first | Real-time, temporally-aware knowledge graphs for agent memory. |
| 3 | [cognee](https://github.com/topoteretes/cognee) | 7.34 | 32.6k | 2026-10-21 | Apache-2.0 | PoC first | Memory platform combining graph and vector stores for agents. |
| 4 | [letta](https://github.com/letta-ai/letta) | 7.17 | 25.2k | 2026-10-18 | Apache-2.0 | PoC first | Platform for stateful agents with self-editing memory (formerly MemGPT). ⚠️ GitHub reports 0 open issues/PRs and no primary language - confirm where development now happens |

### Model Context Protocol (servers, SDKs)

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [python-sdk](https://github.com/modelcontextprotocol/python-sdk) | 8.86 | 24.6k | 2026-10-17 | MIT | Library | Official Python SDK for building MCP servers and clients. |
| 2 | [github-mcp-server](https://github.com/github/github-mcp-server) | 8.75 | 33.8k | 2026-10-21 | MIT | MCP server | GitHub's official MCP server for repos, issues, PRs and Actions. |
| 3 | [fastmcp](https://github.com/PrefectHQ/fastmcp) | 8.70 | 28.2k | 2026-10-22 | Apache-2.0 | Library | High-level, Pythonic framework for MCP servers and clients (auth, composition, testing). |
| 4 | [servers](https://github.com/modelcontextprotocol/servers) | 8.55 | 91.5k | 2026-10-19 | NOASSERTION (permissive) † | MCP server | Reference MCP servers (filesystem, git, fetch, memory, time, ...). † License: Transitioning MIT -> Apache-2.0; docs CC-BY-4.0. ⚠️ Reference implementations - not hardened for production exposure |
| 5 | [playwright-mcp](https://github.com/microsoft/playwright-mcp) | 8.49 | 38.5k | 2026-10-22 | Apache-2.0 | MCP server | Browser automation for agents via Playwright's accessibility tree. |
| 6 | [typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) | 8.38 | 13.6k | 2026-10-21 | NOASSERTION (permissive) † | Library | Official TypeScript SDK for MCP servers and clients. † License: GitHub reports NOASSERTION; the MCP project is moving from MIT to Apache-2.0 (verified on modelcontextprotocol/servers, not individually on this repo). |
| 7 | [context7](https://github.com/upstash/context7) | 8.34 | 63.5k | 2026-10-21 | MIT | MCP server | Serves current, version-specific library documentation to agents. ⚠️ Backed by a hosted service - queries leave your network |
| 8 | [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 8.29 | 54.0k | 2026-10-21 | Apache-2.0 | MCP server | Chrome DevTools (performance, network, console) exposed to coding agents. |

### RAG, hybrid search & reranking

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [ragflow](https://github.com/infiniflow/ragflow) | 7.96 | 92.6k | 2026-10-22 | Apache-2.0 | PoC first | End-to-end RAG engine with deep document understanding and agent features. ⚠️ Heavy multi-container deployment |
| 2 | [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) | 7.82 | 12.3k | 2026-08-24 | MIT | Library | BGE embedding and reranker models plus training/inference code. ⚠️ Model weights carry their own licenses - check each model card |
| 3 | [LightRAG](https://github.com/HKUDS/LightRAG) | 7.81 | 40.3k | 2026-10-20 | MIT | PoC first | Lightweight graph-augmented RAG with incremental updates. |
| 4 | [graphrag](https://github.com/microsoft/graphrag) | 7.78 | 36.4k | 2026-10-20 | MIT | PoC first | Graph-based RAG that builds entity/community summaries for global questions. ⚠️ Indexing is LLM-call heavy - estimate cost before large corpora |
| 5 | [PageIndex](https://github.com/VectifyAI/PageIndex) | 7.30 | 39.4k | 2026-10-21 | MIT | PoC first | Vectorless, reasoning-based document index (tree of contents navigated by the LLM). |

### Vector databases & retrieval stores

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [pgvector](https://github.com/pgvector/pgvector) | 8.54 | 23.4k | 2026-10-22 | NOASSERTION (permissive) † | Service | Vector similarity search inside Postgres. † License: PostgreSQL License (permissive); GitHub reports NOASSERTION. |
| 2 | [qdrant](https://github.com/qdrant/qdrant) | 8.47 | 35.2k | 2026-10-21 | Apache-2.0 | Service | High-performance Rust vector database with filtering and hybrid search. |
| 3 | [chroma](https://github.com/chroma-core/chroma) | 7.91 | 29.5k | 2026-10-22 | Apache-2.0 | Library | Developer-friendly embedded/server vector store. |
| 4 | [lancedb](https://github.com/lancedb/lancedb) | 7.84 | 11.7k | 2026-10-22 | Apache-2.0 | Library | Embedded, serverless retrieval library on the Lance columnar format; multimodal. |
| 5 | [milvus](https://github.com/milvus-io/milvus) | 7.75 | 46.5k | 2026-10-22 | Apache-2.0 | Service | Cloud-native, distributed vector database for very large collections. ⚠️ Distributed deployment has many moving parts |
| 6 | [weaviate](https://github.com/weaviate/weaviate) | 7.45 | 16.9k | 2026-10-21 | NOASSERTION (open-core) † | Service | Vector database storing objects and vectors with hybrid search and modules. † License: BSD-3-Clause outside wl/; wl/ is enterprise-only. |

### Local & self-hosted inference

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [ollama](https://github.com/ollama/ollama) | 9.20 | 184.2k | 2026-10-22 | MIT | Dev tool | Run open-weight models locally with one command and an OpenAI-compatible API. ⚠️ Local API has no built-in auth - keep it bound to localhost |
| 2 | [transformers](https://github.com/huggingface/transformers) | 8.80 | 168.0k | 2026-10-22 | Apache-2.0 | Library | Model-definition framework for text, vision, audio and multimodal models. |
| 3 | [llama.cpp](https://github.com/ggml-org/llama.cpp) | 8.76 | 132.0k | 2026-10-22 | MIT | Dev tool | LLM inference in C/C++ (GGUF) on CPUs, GPUs and Apple silicon. |
| 4 | [vllm](https://github.com/vllm-project/vllm) | 8.56 | 94.9k | 2026-10-22 | Apache-2.0 | Service | High-throughput, memory-efficient LLM serving engine (PagedAttention). |
| 5 | [sglang](https://github.com/sgl-project/sglang) | 7.99 | 37.6k | 2026-10-22 | Apache-2.0 | Service | High-performance serving framework for LLMs and multimodal models. |
| 6 | [unsloth](https://github.com/unslothai/unsloth) | 7.81 | 78.4k | 2026-10-22 | Apache-2.0 | PoC first | Fast, memory-efficient fine-tuning and local training UI. |
| 7 | [LocalAI](https://github.com/mudler/LocalAI) | 7.57 | 49.8k | 2026-10-22 | MIT | Dev tool | OpenAI-compatible local engine for LLMs, images, audio and embeddings. |

### Coding agents & AI dev tools

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [codex](https://github.com/openai/codex) | 8.86 | 130.3k | 2026-10-22 | Apache-2.0 | Dev tool | OpenAI's terminal coding agent (Rust). ⚠️ 24k open issues+PRs - triage backlog is very large |
| 2 | [gemini-cli](https://github.com/google-gemini/gemini-cli) | 8.50 | 107.5k | 2026-10-22 | Apache-2.0 | Dev tool | Google's open-source terminal agent for Gemini models. |
| 3 | [cline](https://github.com/cline/cline) | 8.37 | 70.7k | 2026-10-22 | Apache-2.0 | Dev tool | Autonomous coding agent as IDE extension, CLI or SDK. |
| 4 | [goose](https://github.com/aaif-goose/goose) | 8.20 | 55.5k | 2026-10-22 | Apache-2.0 | Dev tool | Extensible local agent that installs, executes, edits and tests with any LLM. |
| 5 | [OpenHands](https://github.com/OpenHands/OpenHands) | 8.15 | 91.5k | 2026-10-22 | MIT | Dev tool | Open platform for autonomous software-development agents in sandboxes. |
| 6 | [aider](https://github.com/Aider-AI/aider) | 7.42 | 49.7k | 2026-05-22 | Apache-2.0 | Dev tool | AI pair programming in the terminal with git-aware edits. ⚠️ Last push 2026-05-22 - maintenance has slowed |

### Evaluation, observability & tracing

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [promptfoo](https://github.com/promptfoo/promptfoo) | 8.68 | 26.2k | 2026-10-22 | MIT | Dev tool | Declarative prompt/agent/RAG testing and red teaming with CI integration. |
| 2 | [langfuse](https://github.com/langfuse/langfuse) | 8.37 | 36.2k | 2026-10-22 | NOASSERTION (open-core) † | Service | Open-source LLM tracing, evals, prompt management and analytics. † License: MIT outside ee/ directories; ee/ under a separate license. |
| 3 | [deepeval](https://github.com/confident-ai/deepeval) | 8.18 | 19.0k | 2026-10-19 | Apache-2.0 | Dev tool | Pytest-style LLM evaluation framework with many built-in metrics. |
| 4 | [opik](https://github.com/comet-ml/opik) | 7.84 | 22.8k | 2026-10-22 | Apache-2.0 | Service | Tracing, automated evaluations and dashboards for LLM apps and agents. |
| 5 | [mlflow](https://github.com/mlflow/mlflow) | 7.80 | 28.5k | 2026-10-22 | Apache-2.0 | Service | AI engineering platform for experiment tracking, tracing, evaluation and model registry. |
| 6 | [phoenix](https://github.com/Arize-ai/phoenix) | 7.34 | 11.9k | 2026-10-21 | NOASSERTION (source-available) † | Service | AI observability and evaluation built on OpenTelemetry/OpenInference. † License: Elastic License 2.0 - may not be offered to third parties as a hosted/managed service. |
| 7 | [ragas](https://github.com/vibrantlabsai/ragas) | 6.39 | 16.1k | 2026-02-24 | Apache-2.0 | Dev tool | Metrics for evaluating RAG and LLM applications (faithfulness, context precision, ...). ⚠️ Repo moved from explodinggradients/ragas; last push 2026-02-24 - check activity before depending on it |

### Document processing & extraction

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [markitdown](https://github.com/microsoft/markitdown) | 9.10 | 191.5k | 2026-10-21 | MIT | Library | Lightweight converter from Office files, PDFs and more to Markdown. |
| 2 | [docling](https://github.com/docling-project/docling) | 9.07 | 69.3k | 2026-10-21 | MIT | Library | Converts PDF, DOCX, PPTX, XLSX, HTML and images to structured Markdown/JSON with layout and tables. |
| 3 | [langextract](https://github.com/google/langextract) | 8.40 | 39.0k | 2026-10-17 | Apache-2.0 | Library | LLM-based structured extraction from text with precise source grounding. |
| 4 | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | 8.03 | 91.5k | 2026-09-16 | Apache-2.0 | Library | OCR and document parsing toolkit supporting 100+ languages. ⚠️ Requires the PaddlePaddle framework |
| 5 | [marker](https://github.com/datalab-to/marker) | 8.01 | 40.6k | 2026-10-19 | Apache-2.0 | Library | Fast, accurate PDF to Markdown/JSON conversion. ⚠️ Code is Apache-2.0; check the model weights license separately before commercial use |
| 6 | [unstructured](https://github.com/Unstructured-IO/unstructured) | 7.42 | 15.6k | 2026-10-22 | Apache-2.0 | Library | ETL for partitioning and chunking many document types for LLMs. ⚠️ Large optional dependency tree - install only the extras you need |

### Security, guardrails & red teaming

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [garak](https://github.com/NVIDIA/garak) | 7.98 | 9.6k | 2026-10-21 | Apache-2.0 | Dev tool | LLM vulnerability scanner - probes for jailbreaks, injection, leakage and more. |
| 2 | [Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | 7.70 | 7.3k | 2026-10-22 | NOASSERTION (permissive) † | Library | Programmable guardrails (input/output/dialog rails) for LLM apps. † License: Apache-2.0 per LICENSE.md (GitHub reports NOASSERTION). Repo moved from NVIDIA/NeMo-Guardrails. |
| 3 | [guardrails](https://github.com/guardrails-ai/guardrails) | 7.31 | 7.6k | 2026-10-21 | Apache-2.0 | Library | Validators for LLM outputs (structure, PII, toxicity, ...) with a hub of checks. |
| 4 | [PurpleLlama](https://github.com/meta-llama/PurpleLlama) | 6.15 | 4.4k | 2026-10-12 | NOASSERTION (model-license) † | PoC first | Meta's LLM security tools (Llama Guard, Prompt Guard, CyberSecEval). † License: Llama 3.2 Community License (attribution, acceptable-use policy, 700M MAU clause). |
| 5 | [llm-guard](https://github.com/protectai/llm-guard) | 5.25 | 3.2k | 2026-07-08 | MIT | Rejected | Security toolkit for LLM interactions (scanners for prompts/outputs). **Rejected:** Archived on GitHub - no further fixes. Use NeMo Guardrails or guardrails-ai. ⚠️ Archived |

### Workflow automation, browsing & crawling

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [crawl4ai](https://github.com/unclecode/crawl4ai) | 8.63 | 86.0k | 2026-10-21 | Apache-2.0 | Library | Open-source crawler/scraper that turns websites into LLM-ready Markdown. |
| 2 | [browser-use](https://github.com/browser-use/browser-use) | 8.23 | 118.8k | 2026-10-20 | MIT | Library | Python library for AI browser agents. |
| 3 | [firecrawl](https://github.com/firecrawl/firecrawl) | 7.70 | 194.0k | 2026-10-22 | AGPL-3.0 (copyleft) † | Service | Web scraping/crawling API that returns LLM-ready data. † License: AGPL-3.0 - network use of a modified self-hosted copy triggers source-sharing obligations. |
| 4 | [langflow](https://github.com/langflow-ai/langflow) | 7.70 | 155.9k | 2026-10-22 | MIT | PoC first | Visual builder for agents and workflows. ⚠️ Had a critical unauthenticated RCE in 2025 (CVE-2025-3248) - keep patched and never expose without auth |
| 5 | [n8n](https://github.com/n8n-io/n8n) | 7.50 | 208.3k | 2026-10-22 | NOASSERTION (source-available) † | Service | Workflow automation with AI nodes, 400+ integrations and MCP support. † License: Sustainable Use License - internal business or non-commercial use only; .ee files need an enterprise license. |
| 6 | [dify](https://github.com/langgenius/dify) | 7.40 | 159.2k | 2026-10-22 | NOASSERTION (source-available) † | Service | Visual platform for agentic workflows and RAG pipelines. † License: Modified Apache-2.0 - no multi-tenant SaaS without a commercial license; frontend logo/copyright must stay. |
| 7 | [Flowise](https://github.com/FlowiseAI/Flowise) | 5.60 | 55.5k | 2026-08-13 | NOASSERTION (open-core) † | Rejected | Visual agent builder. **Rejected:** Archived on GitHub (last push 2026-08-13). Use Langflow or Dify for visual building. † License: Apache-2.0 except packages/server/src/enterprise and marked files, which are under a commercial license. ⚠️ Archived |

### UI & AI application frameworks

| # | Tool | Score | Stars | Last push | License | Adopt as | What it is / notes |
|---:|---|---:|---:|---|---|---|---|
| 1 | [ai](https://github.com/vercel/ai) | 8.49 | 27.4k | 2026-10-22 | NOASSERTION (permissive) † | Library | TypeScript AI SDK - streaming, tool calls and generative UI for React/Next/Svelte/Vue. † License: Apache-2.0 per LICENSE (GitHub reports NOASSERTION). |
| 2 | [gradio](https://github.com/gradio-app/gradio) | 8.23 | 43.8k | 2026-10-22 | Apache-2.0 | Dev tool | Build and share ML/LLM demo apps in pure Python. |
| 3 | [LibreChat](https://github.com/LibreChat-AI/LibreChat) | 8.05 | 46.1k | 2026-10-22 | MIT | Service | Multi-provider chat UI with agents, MCP, multi-user auth and code interpreter. |
| 4 | [open-webui](https://github.com/open-webui/open-webui) | 7.90 | 156.4k | 2026-10-21 | NOASSERTION (source-available) † | Service | Self-hosted chat UI for Ollama and OpenAI-compatible APIs with RAG and tools. † License: BSD-3 plus a branding clause - "Open WebUI" branding may not be removed above 50 users/30 days without permission or an enterprise license. |
| 5 | [CopilotKit](https://github.com/CopilotKit/CopilotKit) | 7.79 | 38.2k | 2026-10-22 | MIT | Library | Front-end stack for in-app agents and generative UI (makers of AG-UI). |
| 6 | [chainlit](https://github.com/Chainlit/chainlit) | 5.86 | 12.5k | 2026-09-18 | Apache-2.0 | Rejected | Python framework for conversational AI front ends. **Rejected:** Archived on GitHub. Use Gradio for Python demos or Vercel AI SDK for production UIs. ⚠️ Archived |

† GitHub's license label is incomplete or misleading here; the note says what the LICENSE file says.

## Adoption modes

- **Library** — Integrate directly as a dependency
- **Service** — Run/connect as a service or API
- **MCP server** — Add as an MCP server
- **Dev tool** — Development-only tool
- **PoC first** — Evaluate in a proof of concept first
- **Rejected** — Rejected

<!-- END GENERATED -->
