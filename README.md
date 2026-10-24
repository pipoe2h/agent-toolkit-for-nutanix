# Agent Toolkit for Nutanix

An open, agent-friendly starting point for connecting an AI coding agent to a customer-managed Nutanix environment and choosing a safe way to inspect or automate it.

This project is an independent prototype. It is not an official Nutanix product or support statement. It starts with the Nutanix V4 API MCP Server, currently identified by its upstream repository as a Technical Preview, and documents Ansible and OpenTofu as alternative automation paths where appropriate.

## First milestone: read-only connection

The first supported journey is to connect a local MCP-compatible agent to Prism Central using the official Nutanix V4 API MCP Server, validate the connection, and perform read-only discovery. The machine running the MCP server must be able to reach Prism Central; this is normally a customer-network connection, not a publicly hosted Nutanix endpoint.

Read [Agent Setup](setup-instructions/setup.md) for the copy/paste prompt, then `ENTRY.md` for the task index. See `skills/nutanix-connect-prism-central/` for the connection path and `skills/nutanix-automation-method-selection/` for choosing MCP, Ansible, SDKs, or OpenTofu/Terraform.

## Ansible as an alternate path

Ansible can be a useful alternate implementation path when a task is not exposed through the MCP server, or when repeatable playbook automation is a better fit. It is not an automatic fallback for MCP errors. A connection, authentication, permission, TLS, or API error must be diagnosed at its source rather than silently retried through another tool. Initially, generated playbooks are for human review and execution; this toolkit does not authorize agent-executed writes.

The same task may have different API coverage or semantics across MCP, SDK, Ansible, and infrastructure-as-code. Verify the exact Prism Central/AOS release, collection/provider version, supported module/resource, required permissions, and idempotency before proposing a path.

## Install the skills

```bash
npx skills add <owner>/agent-toolkit-for-nutanix/skills
```

The current repository is private, so public distribution and the unredacted setup prompt are future decisions. The prototype does not include an auto-installer; use the agent-native installer above after the repository is available to your account.

## Scope and safety

- Start read-only. Do not request or store secrets in chat; use the agent's secure credential mechanisms or protected local environment files.
- Keep TLS verification enabled. Disabling certificate validation is a lab-only exception that requires an explicit reason and consent.
- Do not presume the Prism Central endpoint is publicly reachable; the operator supplies an address and an agent runtime that can route to it.
- Treat upstream MCP preview software as non-production until its maturity/support status changes.
- Require explicit human review and execution for any generated write-capable Ansible, SDK, or Terraform/OpenTofu artifact in this MVP.
- Distinguish operation coverage gaps from authentication, network, TLS, permission, or service failures. Do not use a different tool to bypass authorization.

## Repository layout

- `ENTRY.md` — agent-facing index and task routing.
- `prompts/setup.md` — copy-paste guided setup prompt.
- `AGENTS.md` and `rules/` — persistent safety rules.
- `skills/` — focused, progressively loaded skills.
- `archive/gateway-first-prototype/` — preserved first prototype, superseded by this foundation-first scope.

## License

Apache-2.0. See `LICENSE`.
