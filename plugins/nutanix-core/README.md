# nutanix-core (Agent Plugin)

Portable package for connecting an AI agent to a customer-managed Nutanix Prism Central
and operating it read-only. It follows the Agent Plugins 1.0.0 format: a root `plugin.json`,
an `mcp.json` MCP server entry, and skills under `skills/`.

## What is in the package

| Component | Path | Purpose |
|---|---|---|
| Manifest | `plugin.json` | Plugin identity and Agent Plugins version. |
| MCP server | `mcp.json` | stdio entry for the official Nutanix V4 API MCP Server, launched through `scripts/launch-nutanix-mcp`. |
| Skills | `skills/` | `nutanix-connect-prism-central`, `nutanix-readonly-inventory`, `nutanix-automation-method-selection`. |

The skills are copies of the canonical skills in this repository's `skills/` directory.
`scripts/sync-plugin-skills.py --check` fails if the two drift apart, so the package stays
self-contained without becoming a second source of truth.

## What the plugin cannot do

- **It does not carry credentials.** The Agent Plugins format defines no portable credential
  or OAuth field, and none may be placed in `mcp.json`. The MCP entry is credential-free;
  the server reads its own `.env` from the installation directory.
- **It does not install the server.** The upstream Nutanix V4 API MCP Server must already be
  installed in a virtualenv. `mcp.json` points at `${PLUGIN_DATA}/ntnx-api-mcp-server`; if the
  server lives elsewhere, set `NUTANIX_MCP_HOME` to that directory.
- **It does not make Prism Central reachable.** The host running the MCP process needs an
  authorized network path to Prism Central on port 9440 with a trusted certificate.

## Installing

Installation, distribution, and enablement are client-managed and outside the portable
format, so use whatever plugin installation your client provides. For clients that implement
Agent Plugins, see the specification's compatible-client list for the entry point of the
client you use: https://agent-plugins.org/compatible-clients

If your client does not support Agent Plugins, use the repository's prompt-based setup path
instead (`prompts/setup.md`); it reaches the same skills and MCP configuration.

## Requirements

- A POSIX shell: the bundled `scripts/launch-nutanix-mcp` is a `/bin/sh` script.
- Python 3.11+ with the upstream server installed in `<NUTANIX_MCP_HOME>/.venv`.
- A first-connection setup run: credentials initialized by the toolkit helper, TLS
  verification enabled (`PC_INSECURE=false`), HTTPS on port 9440, read-only mode on.

Upstream labels the Nutanix V4 API MCP Server a Technical Preview; treat this package as
non-production until that changes.
