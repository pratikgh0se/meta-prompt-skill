---
name: meta-prompt
description: Use when asked to generate, create, or improve a prompt for a specific task. Triggers on "write me a prompt", "generate a prompt", "create a system prompt", "make a prompt for X", or when the user describes a task and needs a well-structured Claude prompt template for it.
---

# meta-prompt

## Overview

Generate high-quality Claude prompt templates from a plain task description using Anthropic's metaprompt technique. Core principle: a structured metaprompt (with examples and XML tags) reliably produces better prompt templates than writing one from scratch.

## When to Use

- User asks to "generate/write/create a prompt for X"
- User describes a task and wants a reusable prompt template
- User wants to improve an existing prompt
- User needs a prompt with input variables (e.g. `{$DOCUMENT}`, `{$QUESTION}`)

## Quick Reference

| Input | Output |
|---|---|
| Task description (required) | Prompt template with XML structure |
| Variable names (optional) | `{$VAR}` placeholders in template |

## Implementation

### Option A: Run the metaprompt script (preferred)

The metaprompt script lives at `~/incubator/meta-prompt-skill/metaprompt.py`.

1. Edit `TASK` and optionally `VARIABLES` in the script
2. Run: `python ~/incubator/meta-prompt-skill/metaprompt.py`
3. The generated prompt appears in stdout

```bash
# Quick one-liner to inject task and run
python -c "
import subprocess, sys
task = '''$TASK_DESCRIPTION'''
# Edit TASK in the script, then run
"
```

Or use the helper below to invoke it programmatically.

### Option B: Inline metaprompt call (when script not available)

Construct the metaprompt directly. The core system prompt structure:

```
Today you will be writing instructions to an eager, helpful, but inexperienced 
and unworldly AI assistant who needs careful instruction and examples to 
understand how best to behave. I will explain a task to you. You will write 
instructions that will direct the assistant on how best to accomplish the task 
consistently, accurately, and correctly.
```

Then pass:
- `<Task>` — the user's task description
- `<Inputs>` — the variable names, written as `{$VARNAME}`
- Ask Claude to produce `<Instructions>` — the final prompt template

Use `claude-sonnet-4-6` with `temperature=0` for deterministic output. Do NOT use claude-sonnet-5 (rejects temperature=0).

### Step-by-step workflow

1. **Gather task** — ask user: "Describe the task in 1-2 sentences. What should the AI do?"
2. **Gather variables** — ask: "What inputs does this prompt need? (e.g. DOCUMENT, QUESTION, USER_INPUT) — or leave blank for none"
3. **Generate** — run metaprompt with task + variables
4. **Present** — show the generated `<Instructions>` block as the prompt template
5. **Test (optional)** — offer to run the generated prompt on an example input using `claude-haiku-4-5`

## Common Mistakes

- Using claude-sonnet-5 for generation — it rejects `temperature=0`, use `claude-sonnet-4-6`
- Skipping variable elicitation — prompts without `{$VAR}` placeholders can't be reused
- Presenting the full metaprompt output — extract only the `<Instructions>` block for the user
- Adding variables the user didn't specify — only use what they asked for

## Example

**User:** "Generate a prompt that summarizes legal documents"

**Variables:** `DOCUMENT`, `FOCUS_AREA` (optional)

**Generated template** (from metaprompt):
```
You will summarize the following legal document.

<document>
{$DOCUMENT}
</document>

{$FOCUS_AREA}

Provide a structured summary covering: key parties, obligations, 
important dates, and risk factors. Use bullet points for clarity.
```
