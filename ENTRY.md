# Nutanix Agent Skills — start here

This is the index. If you are an AI coding agent that was pointed at this file by a
prompt, read this page, then load only the skill that matches the user's task.

## What this repository is

A set of **agent skills** for Nutanix Enterprise AI and the Nutanix Agent Gateway.
Each skill is a directory containing a `SKILL.md` with YAML frontmatter and
instructions. Skills are loaded on demand, so nothing here costs context until it is used.

## How to find what you need

| The user wants to | Read |
|---|---|
| Route a Nutanix gateway request to the right skill | `skills/nutanix-agent-gateway/SKILL.md` |
| Connect a client (OpenCode, Hermes, SDK) to the gateway | `skills/nutanix-agw-connect-client/SKILL.md` |
| Govern MCP servers, client keys, and connectors | `skills/nutanix-agw-mcp-governance/SKILL.md` |
| Set persistent guardrails for how the agent works | `AGENTS.md` (copy into your project's rules file) |
| Understand what is verified vs unconfirmed | the `Validation gates` section of each skill |

## Install

```bash
npx skills add <owner>/<repo>/skills
```

Or copy `skills/<name>/` into your agent's skills directory (`~/.claude/skills/`,
`~/.codex/skills/`, `~/.agents/skills/`, `~/.hermes/skills/`, ...).

## Ground rules for any agent working from this repo

1. **Do not invent product surface.** Every URL path, field label, and credential
   step must trace to a Nutanix procedure page. If you cannot source it, it belongs
   in a validation gate, not in prose presented as fact.
2. **Copy exact strings literally.** Gateway prefixes, endpoint names, and API paths
   are character-for-character. Do not normalise `/v1`, capitalisation, or a prefix.
3. **State the release.** The Agent Gateway surface changes between releases; a fact
   that was true in 2.7 may not hold in 2.8.
4. **Prefer the gateway for agent traffic**, and say why, instead of letting each
   client talk to a model provider directly.
