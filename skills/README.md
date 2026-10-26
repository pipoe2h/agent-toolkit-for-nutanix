# Installation notes

Skills here are two complementary layers:

- **Connection setup** — the MCP server supplies the connectivity and the tools an agent can call. It is not a skill and is not installed by one.
- **Task skills** — each skill supplies the workflow for a class of tasks that uses those tools.

Install selected skills with the open installer:

```bash
npx skills add <owner>/agent-toolkit-for-nutanix/skills
```

Installing is optional. An agent can also read the skill files directly from a clone of this repository, which is what this repo's setup prompt assumes. Clients that implement Agent Plugins can load these skills from the bundled package `plugins/nutanix-core/` instead.

Installing or reading skills does not configure, install, or connect an MCP server, manage Prism Central credentials, or change client configuration. Connection setup is a separate step: `skills/nutanix-connect-prism-central/SKILL.md`.

## Skill catalog

- `skills/nutanix-connect-prism-central/SKILL.md` — connection setup and validation.
- `skills/nutanix-readonly-inventory/SKILL.md` — read-only inventory queries.
- `skills/nutanix-automation-method-selection/SKILL.md` — pick Ansible, SDK/API, or IaC when MCP does not cover the task.

Next operational skills are candidates only: `docs/roadmap/next-operational-skills.md`.
