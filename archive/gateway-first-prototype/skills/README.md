# Skills

One directory per skill, each containing a `SKILL.md` with YAML frontmatter.

- `nutanix-agent-gateway/` — router. Entry point for any Agent Gateway request.
- `nutanix-agw-connect-client/` — connect an OpenAI-compatible client to the gateway.
- `nutanix-agw-mcp-governance/` — MCP servers, client keys, and connectors.

Frontmatter follows the open Agent Skills specification: `name` must match the
directory name, and `description` should be keyword-rich so the agent can match a task
to the skill from the metadata alone.
