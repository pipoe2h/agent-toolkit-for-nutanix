# Connection basics — Nutanix V4 API MCP Server

## First-connection handoff status

- Credentials use the local hidden-input helper described in the canonical setup guide. The user is instructed to run it in their own terminal, not by an agent's tool runner. The helper pre-creates `.env` as mode 0600, sets port 9440/TLS verification/read-only mode explicitly, and suppresses raw output. Credentials are still plaintext at rest and visible to same-user processes; disclose the limitation and require approval before use.

## Upstream facts checked for this prototype

Primary source: the official Nutanix repository [`nutanix/ntnx-api-mcp-server`](https://github.com/nutanix/ntnx-api-mcp-server), especially `README.md`, `docs/quickstart.md`, `docs/configuration.md`, `docs/authentication.md`, `src/cli.py`, and `src/config/settings.py`. Re-check these before publishing or running a new setup because the project is a Technical Preview and may change. The revision inspected for the credential finding was `dc447b3f948662b94c1ed61812eb0d1bb221470d`.

- The README describes a local Python MCP server using stdio. It is launched by an MCP-compatible client as a subprocess; the server does not need a public Nutanix-hosted API endpoint and the stdio process does not itself expose a TCP listener.
- The quickstart currently lists Python >=3.11, Git, a Prism Central deployment exposing V4 APIs, credentials, and network access from the server host to Prism Central (default API port 9440).
- The upstream setup downloads API artifacts and discovers namespaces according to the connected Prism Central; those artifacts should not be reused across different PC instances.
- `src/cli.py::_save_config_dotenv` writes resolved credentials to `.env` using `Path.write_text` without applying restrictive permissions. Upstream auth docs also call out plaintext credential storage and warn to inspect `.env` after `init`/`refresh`.
- Upstream configuration currently maps non-9440 ports to `http://`; first connection must be limited to port 9440 with TLS verification enabled. Do not infer HTTPS solely from `PC_INSECURE=false`.
- The README currently describes `READ_ONLY_MODE=true` as the default and says non-GET operations are rejected server-side in that mode. Verify the effective setting in the installed version and enforce PC RBAC independently.
- The upstream repository currently marks the project Technical Preview / non-production. Do not imply production support.

## What the client connection means

There is no universal public Nutanix cloud API endpoint that every agent can reach. Prism Central is customer-managed. The MCP process must run in a network location that can reach that customer's Prism Central API. The user supplies the correct private IP or FQDN through a protected local configuration method.

For stdio, the MCP client starts the process and communicates over its stdin/stdout. This is convenient for local coding agents, but it means the MCP process and client must coexist on (or be managed from) a host with appropriate network reachability. A remote server or tunnel is a separate deployment design and should not be improvised as part of this setup.

## Safety notes

Never ask the user to paste an API key or password into the conversation. Do not infer an endpoint from public DNS or guess hostnames. Do not bypass an MCP denial by changing credentials or switching tools. Skills and client JSON are not an authorization boundary; PC RBAC and server read-only mode remain authoritative.
