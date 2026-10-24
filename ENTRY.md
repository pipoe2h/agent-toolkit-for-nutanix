# Agent Toolkit for Nutanix — agent entry point

This file is the index. Do not treat the skill collection as the connectivity layer: you need a running local MCP server or another installed automation tool with network reachability to the customer's Prism Central.

## Routes

| User task | Load this skill | Starting method |
|---|---|---|
| Connect an agent to a customer's Prism Central | `skills/nutanix-connect-prism-central/SKILL.md` | Official Nutanix V4 API MCP Server, stdio transport |
| Check connection, discover API operations, inspect schemas/permissions | `skills/nutanix-connect-prism-central/SKILL.md` | MCP discovery and read-only API operations |
| Task not covered by available MCP operations; generate repeatable automation | `skills/nutanix-automation-method-selection/SKILL.md` | Evaluate supported Ansible modules first; then SDK/IaC coverage |
| Build custom programmatic integrations | `skills/nutanix-automation-method-selection/SKILL.md` | Nutanix V4 SDKs/API, after confirming release support |
| Manage declarative infrastructure state | `skills/nutanix-automation-method-selection/SKILL.md` | Nutanix provider with OpenTofu or Terraform, after coverage review |
| Agent Gateway / NAI-specific work | Not the first milestone | Not covered by this toolkit's foundation scope |

## Security rules

1. Begin with read-only access and a low-privilege identity.
2. Do not ask the user to paste passwords, API keys, or tokens in chat.
3. Keep TLS certificate validation enabled. Do not bypass certificate, authorization, or network failures by switching tools.
4. Never silently fall back from a failed MCP call. Identify whether the failure is missing operation coverage, bad input, network/TLS, authentication, authorization, or service health.
5. Ansible, SDK, OpenTofu, and Terraform artifacts that can write are generated for human review and execution only in this MVP. Do not run/apply them.
6. Preserve the user's own project rules and existing agent configuration when helping set up a client.
7. Treat the Nutanix V4 API MCP Server as Technical Preview per its upstream disclaimer; do not present it as production-supported.

## References

- `skills/nutanix-connect-prism-central/references/connection-basics.md`
- `skills/nutanix-automation-method-selection/references/methods-and-fallback.md`
