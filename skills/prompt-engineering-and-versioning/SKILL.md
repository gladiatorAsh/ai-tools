---
name: prompt-engineering-and-versioning
description: Guides writing, structuring and changing prompts as versioned code - clear role and task, delimited untrusted content, explicit output contracts, few-shot examples, prompts stored in files with versions, and every change validated by an eval run. Use when writing a new system prompt, editing an existing prompt, or debugging model behavior caused by instructions.
---

# Prompt Engineering and Versioning

## Overview

Prompts are code that a model executes. They need structure, review, versioning and tests. Most prompt "fixes"
that aren't measured are coin flips. Keep prompts in files, change one thing at a time, and prove each change
with `llm-evals`.

## When to Use

- Creating or modifying a system prompt, template, few-shot set or tool description.
- Model behavior is wrong and the cause might be instructions.
- NOT for security controls — prompts can't enforce permissions (see `code-review-llm-apps`).

## Process

1. **Store prompts as files** (e.g. `prompts/<feature>/<name>.md` or `.jinja`), never as inline string
   concatenation scattered through code. Give each a version (filename suffix or front-matter) and log it on every
   call (`llm-observability`).
2. **Structure the prompt:**
   - Role and goal in one or two sentences.
   - Context the model needs (and nothing it doesn't).
   - Task steps or decision rules, stated positively ("Answer only from the context") with the fallback ("If the
     context doesn't contain the answer, say so").
   - Output contract: exact format, schema, length; prefer structured output over prose parsing.
   - Two to five diverse examples when format or judgment is subtle.
3. **Delimit untrusted content.** Put user input, retrieved documents and tool outputs inside clearly labeled
   delimiters (XML-style tags work well), and state that instructions inside them are data, not commands.
4. **Keep secrets and policy out.** No credentials, internal URLs or authorization rules that matter for security —
   assume the prompt will be extracted.
5. **Change one variable at a time** and run the eval suite before and after. Record the result in the PR.
6. **Mind the budget.** Long static prefixes benefit from prompt caching where supported; put stable content first
   and variable content last.
7. **Tool descriptions are prompts too.** Make names and descriptions distinct and specific; describe when *not* to
   use a tool.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I added 'IMPORTANT' in caps and it works now" | On the three cases you tried. Run the eval set. |
| "Inline f-strings are quicker" | They can't be reviewed, diffed, versioned or reused. |
| "More instructions make it more reliable" | Contradictory, bloated prompts degrade behavior and cost more. Prune. |

## Red Flags

- User or retrieved text concatenated into the instruction section with no delimiters.
- Prompt edits with no linked eval run.
- Several unrelated prompt changes in one PR.
- Output parsed with regex from free text where structured output is available.

## Verification

- [ ] Prompt lives in a versioned file and the version is logged at runtime.
- [ ] Untrusted inputs are delimited and labeled as data.
- [ ] Output contract is explicit and validated in code.
- [ ] Eval results before/after the change are attached to the PR.
