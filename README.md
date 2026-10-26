# Agent Toolkit for Nutanix

This project helps an existing AI coding agent connect to an authorized, customer-managed Prism Central
using the official Nutanix V4 API MCP Server. Upstream currently labels the MCP server Technical
Preview/non-production; do not use it in production.

## Quick start: pick one path

**Path A — install the plugin package (preferred).** `plugins/nutanix-core/` is a portable
[Agent Plugins 1.0.0](https://agent-plugins.org/specification) package: one manifest, one
credential-free MCP server entry, and the skills bundled together. Clients that implement the
format load all of it from one install, with no prompt to paste. Install it with whatever plugin
installation your client provides — installation and enablement are client-managed and outside the
portable format; the Agent Plugins site's compatible-clients page lists each client's entry point. See [docs/plugin-architecture.md](docs/plugin-architecture.md) and
[plugins/nutanix-core/README.md](plugins/nutanix-core/README.md).

**Path B — paste the prompt (fallback).** For clients without Agent Plugins support, copy the
prompt below. It reaches the same skills and MCP configuration; it just carries the instructions in
text instead of in a package.

Neither path installs the upstream MCP server, stores credentials, or makes Prism Central
reachable. Those remain environment steps in the first-connection workflow.

## Start here: connect, then operate

Copy this prompt into your existing AI coding agent. It first checks whether a Nutanix MCP connection is
already live in the current session. If one is connected, it routes your task to the matching operational
skill — starting with read-only inventory. Only if nothing is connected does it coordinate the existing
first-connection workflow, including a clear local-terminal step for entering credentials privately.

The prompt below is an exact copy of the copyable block in [`prompts/setup.md`](prompts/setup.md); a test
fails if the two drift apart.

```text
Connect this agent to my Nutanix environment, or use the connection that is already live.

First, in this current session, read the toolkit's rules and its route index:
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/AGENTS.md
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/ENTRY.md

Then inspect the actual MCP state of this current session before assuming anything. A configured server entry, a config file listing, an installed package, or a previous session is not proof of a live connection: use the client's MCP view (`/mcps` on current OpenCode releases; check your installed version's docs for the exact command) and confirm the Nutanix server shows connected and exposes its tools. If you cannot observe a live handshake in this session, say so and treat the connection as not live.

If connected:
- Load the skill that matches my task, using the routing table in ENTRY.md. Do not merely repeat setup instructions.
- If I ask you to "list my VMs" or any other inventory or reporting question, load:
  https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/skills/nutanix-readonly-inventory/SKILL.md
  and follow its query contract, including its references:
  https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/skills/nutanix-readonly-inventory/references/query-contract.md
  https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/skills/nutanix-readonly-inventory/references/tool-surface-checks.md
- If I have not named a task, ask me what task I want before doing anything else. Do not reinstall, reconfigure, or redo setup steps that are already working.
- Keep the first milestone to one authorized, scoped read-only inventory query with TLS verification enabled and least-privilege Prism Central RBAC. No infrastructure writes. Do not switch to Ansible, SDK/API, or Terraform/OpenTofu to work around a failure.
- Report the operation used, the fields returned, returned/total counts, and the explicit Coverage line. Stop after that query, or stop with a clear actionable blocker.

If no live connection exists, establish one by following the toolkit's setup instructions and the connection skill:
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/setup-instructions/setup.md
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/skills/nutanix-connect-prism-central/SKILL.md

In that disconnected case only, and after I approve each step:

Do not ask me to enter a credential in this chat. When credential entry is needed, give me the exact command to run in a separate local terminal using `scripts/configure_nutanix_credentials.py`; make sure the helper uses hidden input and never prints credentials. Do not claim setup is blocked without explaining what I should do next. Keep the connection read-only and verify it with one small inventory query. Stop after that verification.

Once the agent has installed Nutanix MCP and safely completed private credential initialization, it will update your OpenCode config with a local `nutanix` MCP server entry. **Fully quit and relaunch OpenCode after the config changes** so the new server process starts. Then, in the reopened session, use OpenCode's MCP view (`/mcps` on current releases) to verify it shows connected and exposes Nutanix tools; check your installed version's docs for the exact status command. A CLI config listing alone does not prove the running session has connected. If tools are visible, continue to the single read-only inventory check. If they are not, report the actual failure without retrying any credential prompt blindly.

Important: the workflow includes a local helper for upstream `.env` behavior. Explain that credentials remain plaintext in an owner-only `.env` file and get approval before asking me to run it. If the helper is not available or verified, stop and give me a clear next step; do not ask me to create `.env` or run `nutanix-mcp init` myself.

In both branches, never bypass TLS certificate verification, Prism Central RBAC, or an access denial to make a step pass.
```

The installer stores credentials in upstream `.env`, plaintext but restricted to your OS account (`0600`);
same-user processes may still access it. Review that tradeoff before continuing. The machine running the
MCP server must already have an authorized network path to Prism Central. First connection is HTTPS on port
9440, with TLS verification and read-only mode enabled; the agent does not write to Nutanix.

## Toolkit files the agent uses

You do not need to read or combine these yourself; the prompt above points the agent at them.

- [Plugin package](plugins/nutanix-core/README.md) — the portable Agent Plugins package: manifest, credential-free MCP entry, bundled skills.
- [Plugin architecture](docs/plugin-architecture.md) — how the package and the canonical skills stay one toolkit.
- [ENTRY.md](ENTRY.md) — the agent-facing route index: which skill to load for which task.
- [Connect an agent to Prism Central](skills/nutanix-connect-prism-central/SKILL.md) — the connection workflow, used only when no live connection exists.
- [Read-only inventory](skills/nutanix-readonly-inventory/SKILL.md) — schema inspection, pagination, reconciliation, and partial-result reporting for VMs, clusters, hosts, subnets, and alerts.
- [Automation method selection](skills/nutanix-automation-method-selection/SKILL.md) — what to evaluate when MCP does not expose the requested operation.
- [Agent Setup workflow](setup-instructions/setup.md) — the detailed first-connection instructions the disconnected branch follows.
- [OpenCode Dev Container](examples/opencode/README.md) — optional, not required for the first connection.
- [Install toolkit skills](#install-skills) — optional guidance; skills are not the MCP server.

## More toolkit paths

The initial milestone is one read-only MCP connection and one authorized inventory query. Ansible can be
considered only after confirming the needed operation is not exposed by MCP; never use another tool to
bypass MCP authorization or connection failures. Writes are out of scope for this milestone.

### Install skills

```bash
npx skills add pipoe2h/agent-toolkit-for-nutanix/skills
```

## Safety and scope

- Never ask users to paste secrets into agent conversations or commit keys.
- Do not assume Prism Central is publicly reachable; the agent/MCP runtime needs an authorized network path.
- Treat the upstream Nutanix V4 API MCP Server as Technical Preview/non-production until its status changes.
- Do not use alternate tools to bypass an MCP authorization or connection failure.

## License

Apache-2.0. See `LICENSE`.
