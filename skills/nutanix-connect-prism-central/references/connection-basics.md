# Connection basics — Nutanix V4 API MCP Server

## Upstream facts checked for this prototype

Primary source: the official Nutanix repository [`nutanix/ntnx-api-mcp-server`](https://github.com/nutanix/ntnx-api-mcp-server), especially `README.md`, `docs/quickstart.md`, `docs/configuration.md`, and `docs/authentication.md`. Re-check these before publishing or running a new setup because the project is a Technical Preview and may change.

- The README describes a local Python MCP server using stdio. It is launched by an MCP-compatible client as a subprocess; the server does not need a public Nutanix-hosted API endpoint and the stdio process does not itself expose a TCP listener.
- The quickstart currently lists Python >=3.11, Git, a Prism Central deployment exposing V4 APIs, credentials, and network access from the server host to Prism Central (default API port 9440).
- The upstream setup downloads API artifacts and discovers namespaces according to the connected Prism Central; those artifacts should not be reused across different PC instances.
- The README currently describes `READ_ONLY_MODE=true` as the default and says non-GET operations are rejected server-side in that mode. Verify the effective setting in the installed version.
- The upstream repository currently marks the project Technical Preview / non-production. Do not imply production support.
- The upstream configuration docs describe TLS verification enabled by default (`PC_INSECURE=false`). Keep it enabled. If a lab has a self-signed certificate, prefer adding the issuing CA to the host trust store; only consider disabling verification as an explicitly accepted temporary lab exception.
- Authentication options and their requirements may depend on Prism Central version and account type. Follow current upstream docs and official IAM documentation; do not assume API-key eligibility or service-account setup steps without checking.

## What the client connection means

There is no universal public Nutanix cloud API endpoint that every agent can reach. Prism Central is customer-managed. The MCP process must run in a network location that can reach that customer's Prism Central API. The user supplies the correct private IP or FQDN through a protected local configuration method.

For stdio, the MCP client starts the process and communicates over its stdin/stdout. This is convenient for local coding agents, but it means the MCP process and client must coexist on (or be managed from) a host with appropriate network reachability. A remote server or tunnel is a separate deployment design and should not be improvised as part of this setup.

## Before setup, collect non-secret facts

- Which agent client and version will launch the server?
- Which host will run the MCP process, and can that host route to Prism Central?
- What Prism Central version and V4 API namespaces are available?
- Which authorized read-only identity will be used, and how will credentials be stored outside chat?
- Does Prism Central present a certificate trusted by the MCP host?
- Is this a lab-only test? Upstream preview software is explicitly non-production.

Never ask the user to paste an API key or password into the conversation. Do not infer an endpoint from public DNS or guess hostnames.
