# meta-prompt-skill

A Claude Code skill for generating high-quality prompt templates using Anthropic's [metaprompt technique](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-generator).

## What it does

Given a plain task description (and optional variable names), generates a structured, reusable Claude prompt template — with XML tags, examples, and `{$VARIABLE}` placeholders.

## Files

| File | Purpose |
|------|---------|
| `metaprompt.py` | Runnable script — edit `TASK` and `VARIABLES`, run to generate a prompt |
| `skill/SKILL.md` | Claude Code skill — auto-triggers when you ask to "generate a prompt for X" |

## Usage

### Run the script directly

```bash
# Edit TASK in metaprompt.py, then:
python metaprompt.py
```

### Use as a Claude Code skill

Copy `skill/SKILL.md` to `~/.claude/skills/meta-prompt/SKILL.md`.

Then in any Claude Code session, just say:
> "Generate a prompt for summarizing legal documents"

Claude will run the metaprompt workflow and return a ready-to-use prompt template.

## Requirements

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key
```

## Notes

- Use `claude-sonnet-4-6` for generation (temperature=0). Do **not** use claude-sonnet-5 — it rejects `temperature=0`.
- The metaprompt text is from [Anthropic's claude-cookbooks](https://github.com/anthropics/claude-cookbooks).
