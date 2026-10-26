# Agent Toolkit for Nutanix

This project helps an existing AI coding agent connect to an authorized, customer-managed Prism Central using the official Nutanix V4 API MCP Server. Upstream currently labels the MCP server Technical Preview/non-production; do not use it in production.

# Connect your agent to Nutanix

Copy this prompt into your existing AI coding agent. It will inspect the environment and coordinate the setup, including a clear local-terminal step for entering credentials privately.

```text
Connect this agent to my Nutanix environment by following:
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/b40d617/setup-instructions/setup.md

Do not ask me to enter a credential in this chat. When credential entry is needed, give me the exact command to run in a separate local terminal using `scripts/configure_nutanix_credentials.py`; make sure the helper uses hidden input and never prints credentials. Do not claim setup is blocked without explaining what I should do next. Keep the connection read-only and verify it with one small inventory query. Stop after that verification.

Once the agent has installed Nutanix MCP and safely completed private credential initialization, it will update your OpenCode config with a local `nutanix` MCP server entry. **Fully quit and relaunch OpenCode after the config changes** so the new server process starts. Then, in the reopened session, use OpenCode's MCP view (`/mcps` on current releases) to verify it shows connected and exposes Nutanix tools; check your installed version's docs for the exact status command. A CLI config listing alone does not prove the running session has connected. If tools are visible, continue to the single read-only inventory check. If they are not, report the actual failure without retrying any credential prompt blindly.

Important: the workflow includes a local helper for upstream `.env` behavior. Explain that credentials remain plaintext in an owner-only `.env` file and get approval before asking me to run it. If the helper is not available or verified, stop and give me a clear next step; do not ask me to create `.env` or run `nutanix-mcp init` myself.
```

The installer stores credentials in upstream `.env`, plaintext but restricted to your OS account (`0600`); same-user processes may still access it. Review that tradeoff before continuing. The machine running the MCP server must already have an authorized network path to Prism Central. First connection is HTTPS on port 9440, with TLS verification and read-only mode enabled; the agent does not write to Nutanix.

## Optional resources

- [Agent Setup workflow](setup-instructions/setup.md)
- [OpenCode Dev Container](examples/opencode/README.md) — optional, not required for the first connection
- [Install toolkit skills](#install-skills) — optional guidance; skills are not the MCP server

## More toolkit paths

The initial milestone is only a read-only MCP connection and one inventory query. Ansible can be considered only after confirming the needed operation is not exposed by MCP; never use another tool to bypass MCP authorization or connection failures.

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