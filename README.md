# Agent Toolkit for Nutanix

An open, agent-friendly starting point for connecting AI coding agents to customer-managed Nutanix environments and choosing safe ways to inspect or automate them.

This project is an independent prototype, not an official Nutanix product or support statement. It starts with the Nutanix V4 API MCP Server, currently identified by its upstream repository as a Technical Preview, and documents Ansible and OpenTofu as alternative automation paths where appropriate.

## Optional OpenCode Dev Container

The repository root contains `.devcontainer/`. Clone this repo, open its root in VS Code, and select **Dev Containers: Reopen in Container**. VS Code builds an Ubuntu-based container with OpenCode pre-installed and installs the toolkit skills into `.agents/skills/`.

The container does not choose an LLM provider or require Nutanix Enterprise AI. Use any provider/subscription you already configure for OpenCode; other agents on your host are unaffected. If you want OpenCode to use an NAI unified endpoint, see the optional example in [`examples/opencode/README.md`](examples/opencode/README.md) and [`examples/opencode/opencode.nai.example.json`](examples/opencode/opencode.nai.example.json). That config is not activated automatically.

## Agent Setup and first milestone

Read [Agent Setup](setup-instructions/setup.md) for the copy/paste prompt and guided workflow. The first supported journey is a read-only connection from an MCP-compatible agent to Prism Central using the official Nutanix V4 API MCP Server. The machine running the MCP server must be able to reach customer-managed Prism Central; there is no universal public endpoint for customer clusters.

See `skills/nutanix-connect-prism-central/` for connection guidance and `skills/nutanix-automation-method-selection/` for choosing MCP, Ansible, SDK/API code, or OpenTofu/Terraform.

## Ansible as an alternate path

Ansible can be a useful alternate implementation when MCP does not expose a needed operation or repeatable playbooks are a better fit. It is not an automatic fallback for MCP errors. Diagnose network, TLS, authentication, authorization, input, and service errors at their source. Generated write-capable automation is for human review and execution in this prototype.

## Install skills in another agent

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
