# Agent Toolkit for Nutanix

An open, agent-friendly starting point for connecting AI coding agents to customer-managed Nutanix environments and choosing safe ways to inspect or automate them.

This project is an independent prototype, not an official Nutanix product or support statement. It starts with the Nutanix V4 API MCP Server, currently identified by its upstream repository as a Technical Preview, and documents Ansible and OpenTofu as alternative automation paths where appropriate.

## Optional OpenCode Dev Container

The Dev Container builds an Ubuntu-based image with OpenCode pre-installed. On first container creation, `.devcontainer/install-toolkit-skills.sh` installs the toolkit's two skills into the repository-local `.agents/skills/` directory, which OpenCode discovers automatically. The skills are available as guidance; **the MCP server itself is not installed or configured by the image**.

After the container opens, paste the prompt from [`prompts/setup.md`](prompts/setup.md) into OpenCode. That prompt points the agent at the detailed Agent Setup workflow; the workflow then guides the agent and user through the later MCP installation, approval, credential, configuration, and read-only verification steps. `opencode` starts with the user's default provider/subscription; no LLM provider or key is set by the container.

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
