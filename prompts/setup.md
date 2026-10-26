# Start here: connect, then operate

Copy this prompt into your existing AI coding agent. It checks whether a Nutanix MCP connection is
already live in the current session, then either routes your task to the matching toolkit skill or,
only if nothing is connected, walks you through the existing first-connection workflow — including a
private credential-entry step in your own terminal.

The prompt is the canonical copy. `README.md` mirrors it exactly, and `tests/test_setup_handoff.py`
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

The detailed instructions are in [`setup-instructions/setup.md`](../setup-instructions/setup.md); the
route index is [`ENTRY.md`](../ENTRY.md). The agent requests approval before running the local credential
helper, explains that `.env` is plaintext-at-rest despite mode `0600`, then guides the user through hidden
local-terminal entry. Never paste credentials or terminal output into chat.

Setup is conditional: when the MCP server is already connected in the current session, the prompt sends
the task to the matching skill instead of reinstalling anything.
