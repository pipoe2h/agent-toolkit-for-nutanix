# nutanix-core (Agent Plugin)

Portable package for connecting an AI agent to a customer-managed Nutanix Prism Central and
operating it. It follows the Agent Plugins 1.0.0 format: a root `plugin.json`, an `mcp.json`
MCP server entry, and skills under `skills/`.

## What is in the package

| Component | Path | Purpose |
|---|---|---|
| Manifest | `plugin.json` | Plugin identity and Agent Plugins version. |
| MCP server | `mcp.json` | stdio entry for the Nutanix V4 API MCP Server, launched through `scripts/launch-nutanix-mcp`. |
| Skills | `skills/` | `nutanix-connect-prism-central`, `nutanix-readonly-inventory`, `nutanix-automation-method-selection`. |
| Support script | `scripts/configure_nutanix_credentials.py` | The credential helper the connection skill tells the agent to hand to the user. Packaged so the skill's reference resolves inside the plugin root. |

The skills and the helper are copies of the canonical files in this repository's `skills/`
and `scripts/` directories. `scripts/sync-plugin-skills.py --check` and a test fail if a copy
drifts, so the package stays self-contained without becoming a second source of truth.

## Where the server must live

`mcp.json` sets `NUTANIX_MCP_HOME` to `${PLUGIN_DATA}/ntnx-api-mcp-server`, and `${PLUGIN_DATA}`
is the client-owned writable directory that survives plugin updates. Because a conformant
client overlays configured `env` entries on the base environment and **replaces** same-name
entries, a `NUTANIX_MCP_HOME` you export in your shell is replaced for this server: the value
in `mcp.json` wins. Two consequences:

- To use the packaged MCP entry, install the upstream server at
  `${PLUGIN_DATA}/ntnx-api-mcp-server`.
- To use an install somewhere else, point the client's own configuration at a launcher with a
  different `NUTANIX_MCP_HOME`, or edit this package's `mcp.json` for that install.

The toolkit's first-connection workflow currently installs the server wherever the operator
chooses. Aligning that target with the package's data directory is an open integration item;
until it is closed, treat the packaged entry as needing that alignment.

## What the plugin cannot do

- **It does not carry credentials.** The format defines no portable credential or OAuth field,
  and none may be placed in `mcp.json` or `env`. The MCP entry is credential-free; the server
  reads its own `.env` from the installation directory.
- **It does not install the server.** The upstream Nutanix V4 API MCP Server must already be
  installed in a virtualenv at `<NUTANIX_MCP_HOME>/.venv`.
- **It does not make Prism Central reachable.** The host running the MCP process needs an
  authorized network path to Prism Central on port 9440 with a trusted certificate.
- **It does not set the read-only mode.** The package declares no server mode. Whether
  operations are read-only depends on the server's effective `READ_ONLY_MODE`, on the
  `.env` written by the credential helper, and on Prism Central RBAC — verify the effective
  posture per install rather than assuming the package enforces it.

## Installing

Installation, distribution, and enablement are client-managed and outside the portable format,
so use whatever plugin installation your client provides. For the clients that implement Agent
Plugins, the Agent Plugins site's compatible-clients page lists each one's setup entry point
and the components and transports it supports: https://agent-plugins.org/compatible-clients

If your client does not support Agent Plugins, use the repository's prompt-based setup path
instead (`prompts/setup.md`); it reaches the same skills and MCP configuration.

## Requirements

- A POSIX shell. `scripts/launch-nutanix-mcp` is a `/bin/sh` script, which makes the MCP
  component POSIX-only. The closed manifest has no field for platform constraints, so this
  note is the only place it is recorded.
- Python 3.11+ with the upstream server installed in `<NUTANIX_MCP_HOME>/.venv`.
- A first-connection setup run: credentials initialized by the toolkit helper, TLS verification
  enabled (`PC_INSECURE=false`), HTTPS on port 9440.

Upstream labels the Nutanix V4 API MCP Server a Technical Preview; treat this package as
non-production until that changes.
