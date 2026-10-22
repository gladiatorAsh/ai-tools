---
name: llm-evals
description: Guides evaluation-driven development for LLM, RAG and agent features - building a golden dataset, choosing deterministic checks before LLM-as-judge, measuring retrieval and answer quality separately, running promptfoo or DeepEval in CI against Azure OpenAI, and gating merges on regressions. Use when changing a prompt, model, retrieval setting or agent, or when asked whether an AI feature got better or worse.
---

# LLM Evals

## Overview

An eval suite is the test suite for non-deterministic code. Every prompt, model, chunking or tool change is a
hypothesis; the eval run is the evidence. Start small (20–50 cases), prefer cheap deterministic assertions, use an
LLM judge only for what can't be checked mechanically, and run it in CI. Tools: **promptfoo** (YAML, any
language, CI-native) or **DeepEval** (pytest-style, Python).

## When to Use

- Before and after changing a prompt, model/deployment, temperature, retrieval or tool definitions.
- When someone says an AI feature "seems worse/better".
- When a red-team finding or bug report needs a regression test.

## Process

1. **Build the golden set.** 20–50 cases from real or realistic traffic: typical, edge, adversarial and
   "should refuse/say I don't know" cases. For RAG, record the expected source document per question. Store as
   versioned data in the repo (`evals/cases.yaml` or `.jsonl`) — no customer PII.
2. **Assert mechanically first.** JSON validity and schema, required/forbidden substrings, citations present and
   resolvable, tool called with expected arguments, length bounds, latency and cost ceilings.
3. **Then judge.** Use model-graded rubrics only for qualities like correctness vs a reference, groundedness in
   retrieved context and helpfulness. Use a strong judge deployment different from the system under test, and
   spot-check judge verdicts by hand on ~10 cases.
4. **Separate retrieval from generation** for RAG: report recall@k (did the right chunk come back?) apart from
   answer faithfulness/correctness. Fix whichever half is failing.
5. **Wire it to Azure.** promptfoo example (provider syntax verified 2026-10-22):

   ```yaml
   # promptfooconfig.yaml
   prompts: [file://prompts/answer.txt]
   providers:
     - id: azure:responses:my-gpt-deployment
       config:
         apiHost: my-resource.openai.azure.com
   defaultTest:
     options:
       provider: azure:chat:my-judge-deployment   # grader for llm-rubric
   tests: file://evals/cases.yaml
   ```

   Auth: `AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET`/`AZURE_TENANT_ID` (service principal with *Cognitive Services
   OpenAI User*), or `az login` locally. Run with a pinned version: `npx promptfoo@<version> eval`.

   DeepEval alternative (pytest): `LLMTestCase` + metrics such as `FaithfulnessMetric`/`AnswerRelevancyMetric`,
   `assert_test(...)`, run with `deepeval test run evals/`. Configure its judge to your Azure deployment per its docs.
6. **Gate in CI.** Run on PRs that touch prompts, model config, retrieval or tools. Fail on regressions against the
   main-branch baseline (pass rate drop, any previously-passing safety case failing), not on an absolute score.
   Cache or sample if cost matters.
7. **Keep it alive.** Every production bug or red-team finding becomes a case. Review the set quarterly for drift.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We'll eval once it's stable" | It's never stable without evals; you just can't see the regressions. |
| "LLM-as-judge for everything is easier" | Judges are slow, costly and biased. Deterministic checks catch most regressions for free. |
| "A 0.82 average score means it's good" | Averages hide the safety case that started failing. Track per-case diffs vs baseline. |
| "The judge model can grade itself" | Same-model judging inflates scores. Use a different, stronger deployment. |

## Red Flags

- Prompt or model changes merged without an eval run linked.
- Golden set built from synthetic data only, or containing real customer PII.
- Only an aggregate score reported; no per-case regression list.
- RAG evals that never check which documents were retrieved.

## Verification

- [ ] Golden set is versioned in the repo with expected outputs/sources and refusal cases.
- [ ] Deterministic assertions exist for structure, citations and forbidden content.
- [ ] A CI job runs the suite on relevant PRs and fails on regressions vs baseline.
- [ ] The PR description links the eval result for the change.
