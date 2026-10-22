---
name: agent-orchestration-design
description: Guides the decision between a single model call, a deterministic workflow, a single tool-using agent, and multi-agent orchestration, then the design of tools, state, approvals and failure handling, implemented with Microsoft Agent Framework on Azure. Use when designing or reviewing any agent, tool-calling loop, or multi-agent system.
---

# Agent Orchestration Design

## Overview

Most "agent" problems are workflows in disguise. Every step of autonomy adds cost, latency and failure modes, so
use the *least* autonomous design that meets the requirement. On Azure, implement with **Microsoft Agent
Framework** (the successor to Semantic Kernel agents and AutoGen; AutoGen is archived). Use the
`microsoft-agent-framework` skill for current API details.

## When to Use

- Someone says "agent", "multi-agent", "orchestrator", "planner" or "autonomous".
- Adding tools/function calling to a model, or chaining several model calls.
- NOT for a single prompt-in/answer-out call — that's `azure-openai-client`.

## Process

1. **Pick the autonomy level** (stop at the first that works):

   ```
   Single call ──► Workflow (fixed steps) ──► Single agent + tools ──► Multi-agent
   cheapest, most predictable                           most flexible, hardest to test
   ```

   - **Workflow** when the steps are known in advance (extract → validate → enrich → store).
   - **Single agent** when the *order* of tool use depends on the input.
   - **Multi-agent** only when distinct roles need separate instructions, tools or permissions *and* a single agent
     measurably fails. Write the reason down.
2. **Design tools as APIs.** Each tool: one job, typed parameters, clear description, idempotent where possible,
   validated input, bounded output size, explicit errors. Read-only tools first; write tools need approval.
3. **Set guardrails before the happy path.**
   - Max iterations/turns, max tokens, wall-clock timeout per run.
   - Human approval for irreversible or external side effects (send, pay, delete, deploy).
   - Least-privilege identity per agent; tools enforce authorization in code, not in the prompt.
4. **Decide state.** What persists between turns (thread/conversation), what is checkpointed for long-running
   workflows, and where (Foundry-managed threads vs your store). Never keep secrets in agent memory.
5. **Implement with Agent Framework.** Python baseline (verified against the project README, 2026-10-22):

   ```python
   from agent_framework import Agent
   from agent_framework.foundry import FoundryChatClient
   from azure.identity import DefaultAzureCredential

   agent = Agent(
       client=FoundryChatClient(credential=DefaultAzureCredential()),  # endpoint/model from env or args
       name="SupportTriage",
       instructions="...",
       tools=[lookup_order, create_ticket],
   )
   result = await agent.run(user_message)
   ```

   .NET: `dotnet add package Microsoft.Agents.AI` (+ `Microsoft.Agents.AI.Foundry`). Use workflows (graph-based
   orchestration with checkpointing) rather than agent-calls-agent loops for multi-step processes.
6. **Make runs inspectable.** Trace every model call and tool call with inputs/outputs (redacted), decisions and
   cost (`llm-observability`). An agent you can't replay is one you can't debug.
7. **Evaluate trajectories, not just answers.** Eval cases assert which tools were called, with what arguments,
   and that forbidden tools were not (`llm-evals`).

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Multi-agent is more powerful" | It multiplies prompts, failure modes and tokens. Prove a single agent fails first. |
| "The system prompt says not to delete things" | Prompts are not access control. Enforce permissions in tool code. |
| "We'll add a turn limit if it loops" | It will loop in production first. Limits are part of v1. |
| "AutoGen has the pattern I need" | AutoGen is archived with no security fixes. Port the pattern to Agent Framework. |

## Red Flags

- No max-iterations/timeout; an agent that can call itself or another agent unboundedly.
- Write/delete/send tools with no approval step.
- One shared high-privilege credential for all tools.
- Tool descriptions that overlap ("search", "find", "lookup") so the model guesses.
- Evals that only check the final text.

## Verification

- [ ] The chosen autonomy level and why the simpler one was insufficient are documented.
- [ ] Each tool validates input and enforces authorization in code; tests cover a denied call.
- [ ] Turn, token and time limits are configured and tested (a looping case terminates).
- [ ] Side-effecting tools require approval; a test proves the agent pauses.
- [ ] Traces show every tool call for a sample run.
