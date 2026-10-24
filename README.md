# Nutanix Agent Skills

Agent skills for Nutanix Enterprise AI (NAI) and the Nutanix Agent Gateway — in the
open `SKILL.md` format, installable into Claude Code, Codex, Cursor, opencode, Hermes
Agent, and any other agent that reads skills.

A skill is a directory with a `SKILL.md` (YAML frontmatter + markdown instructions) and
optional `references/`. Agents read the frontmatter at startup and load the body only
when a task matches, so the whole collection stays cheap until it is needed.

## Quick start

Paste the prompt in [`prompts/setup.md`](prompts/setup.md) into your agent. It points
the agent at [`ENTRY.md`](ENTRY.md), which indexes everything else.

To install mechanically instead:

```bash
npx skills add <owner>/<repo>/skills
```

## Layout

```
ENTRY.md                  # the index an agent reads first
prompts/setup.md          # the copy-paste prompt
AGENTS.md                 # persistent rules; copy into your project's rules file
rules/                    # canonical rules content
skills/                   # one directory per skill
```

## Scope

This collection covers the **Agent Gateway** — the control layer between agents, LLMs,
and MCP servers. Private Inference (self-hosted model deployment) and cluster
installation are out of scope.

## Licence

Apache-2.0. See `LICENSE`.
