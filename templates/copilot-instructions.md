# Copilot instructions (template)

<!-- Copy to .github/copilot-instructions.md in a project that uses the ai-tools skills. Keep it short:
     always-on instructions cost context on every request; the skills hold the detail. -->

## AI features in this repository

- Before starting an LLM, RAG, agent or MCP task, use the `using-ai-tools-skills` skill to pick the right skill.
- Azure-first: Azure OpenAI (v1 API), Azure AI Search, Microsoft Agent Framework, Azure Monitor. Justify any
  third-party AI service or framework with the `choose-ai-tool` skill.
- Keyless auth only (`DefaultAzureCredential` / managed identity). Never add API keys or connection strings to code.
- Verify Azure API details against current docs (`microsoft-docs` skill) and cite the URL in the PR.
- Prompts live in versioned files; untrusted text is delimited as data; model output is validated before use.
- Any change to prompts, models, retrieval or tools must include an eval result (`llm-evals`).

## Boundaries

- Always: run tests and evals before committing AI-behavior changes.
- Ask first: new AI dependencies, new tools with side effects, changes to identity/role assignments.
- Never: commit secrets, put secrets or other tenants' data in prompts, rely on a prompt as an access control.
