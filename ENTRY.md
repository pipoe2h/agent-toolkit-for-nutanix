# Agent Toolkit for Nutanix — agent entry point

This file is the index. Read it top-down: connect first, then operate.

- **Connect first.** The skill collection is not the connectivity layer: you need a running local MCP server (or another installed automation tool) with network reachability to the customer's Prism Central.
- **Then operate.** Once a connection is live, this same index is the operating entry point. Load the skill for the task the user asked for. This file only routes; the skills hold the procedures.

## Routes

| User task | Load this skill | Starting method |
|---|---|---|
| Connect an agent to a customer's Prism Central | `skills/nutanix-connect-prism-central/SKILL.md` | Official Nutanix V4 API MCP Server, stdio transport |
| Verify an existing connection, discover API operations, inspect schemas or permissions | `skills/nutanix-connect-prism-central/SKILL.md` | MCP discovery and read-only API operations |
| Use an already connected Nutanix environment — operate on it | This route index (`ENTRY.md`) | Connection is assumed live: use this file as the operating entry point, then load the row matching the requested task |
| List or report resources (VMs, clusters, hosts, subnets, alerts) | `skills/nutanix-readonly-inventory/SKILL.md` | MCP, read-only, paginated |
| Task not covered by available MCP operations; generate repeatable automation | `skills/nutanix-automation-method-selection/SKILL.md` | Evaluate supported Ansible modules first; then SDK/IaC coverage |
| Build custom programmatic integrations | `skills/nutanix-automation-method-selection/SKILL.md` | Nutanix V4 SDKs/API, after confirming release support |
| Manage declarative infrastructure state | `skills/nutanix-automation-method-selection/SKILL.md` | Nutanix provider with OpenTofu or Terraform, after coverage review |
| Agent Gateway / NAI-specific work | Not the first milestone | Not covered by this toolkit's foundation scope |

Read-only inventory is the only operational skill implemented today. Other operational domains are candidates, not capabilities: `docs/roadmap/next-operational-skills.md`.

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
- `skills/nutanix-readonly-inventory/references/query-contract.md`
- `skills/nutanix-readonly-inventory/references/tool-surface-checks.md`
- `skills/nutanix-automation-method-selection/references/methods-and-fallback.md`
- `docs/roadmap/next-operational-skills.md`
