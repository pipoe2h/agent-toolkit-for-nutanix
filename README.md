# Agent Toolkit for Nutanix

The handoff below is currently blocked at credential entry. The upstream MCP server has no verified private credential wizard, and its `init` command writes secrets back to `.env` without enforcing restrictive file permissions. The agent must not collect secrets in chat or claim a completed setup. This independent prototype targets an existing AI coding agent and read-only communication with customer-managed Prism Central using the official Nutanix V4 API MCP Server. Upstream currently labels that MCP server Technical Preview/non-production; do not use it in production. The current handoff does not yet install/connect the MCP server because secure credential entry is unresolved.

## Connect your agent

Copy this prompt into your existing AI coding agent. This initial release reports the current blocker; it does not yet install or connect the MCP server.

```text
Connect this agent to my Nutanix environment by following:
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/setup-instructions/setup.md

Do the setup for me. Ask only for details you cannot discover yourself, explain local changes before requesting approval, and never ask me to paste secrets into chat. Keep the connection read-only and verify it with one small inventory query. Stop after that verification.

Important: this workflow is currently blocked at credential entry. Do not ask me to create or edit `.env`, do not write credentials to a file, do not run `nutanix-mcp init` with credentials, and do not contact Prism Central with credentials. Upstream `init` can persist secrets to `.env` without enforcing restrictive file permissions. Stop and report this blocker unless a safe private credential-entry method has been independently verified for the exact upstream revision.
```

You need an existing agent that can run local commands, an authorized Prism Central environment, and a network path from the machine running the MCP server to Prism Central. If the agent cannot reach that network, setup must stop until you arrange an authorized path. Do not use this preview server in production. The handoff is intentionally blocked at credential entry until a safe, private mechanism is validated; the agent must not represent itself as having completed setup.

## Optional resources

- [Agent Setup workflow](setup-instructions/setup.md)
- [OpenCode Dev Container](examples/opencode/README.md) — optional, not required for the first connection
- [Install toolkit skills](#install-skills) — optional guidance; skills are not the MCP server

## More toolkit paths

The first milestone is only a read-only MCP connection and one inventory query. Ansible, SDK/API code, OpenTofu/Terraform, skills, and the optional Dev Container are out of scope for that first setup. Ansible can be an alternate implementation after confirming the requested operation is not exposed by MCP; never use another tool to bypass MCP authorization or connection failures.

### Install skills

```bash
npx skills add pipoe2h/agent-toolkit-for-nutanix/skills
```

## Safety and scope

- Start read-only and keep TLS verification enabled.
- Never ask users to paste secrets into agent conversations or commit keys.
- Do not assume Prism Central is publicly reachable; the agent/MCP runtime needs an authorized network path.
- Treat the upstream Nutanix V4 API MCP Server as Technical Preview/non-production until its status changes.
- Do not use alternate tools to bypass an MCP authorization or connection failure.

## License

Apache-2.0. See `LICENSE`.