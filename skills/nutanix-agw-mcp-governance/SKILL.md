---
name: nutanix-agw-mcp-governance
description: "Govern MCP servers through Nutanix Agent Gateway. Covers adding remote and local MCP servers, MCP client keys, connectors, per-connector tool grants, the 34-character tool-name limit, and per-client rate limiting. Use when connecting agents to MCP tools through Nutanix Enterprise AI, or troubleshooting MCP access and tool visibility."
license: Apache-2.0
metadata:
  version: "0.1.0"
---

# MCP governance through the Agent Gateway

## When to Use

- Adding a remote or local MCP server to Nutanix Enterprise AI.
- Creating an MCP client key and connecting it to servers via a connector.
- An agent cannot see an MCP tool, or a tool works in one client and not another.
- Applying token budgets to MCP-using clients.

Not for: inference endpoint setup (see `nutanix-agw-connect-client`) or authoring an MCP
server itself.

## Why route MCP through the gateway

A single `/mcp` interface aggregates multiple tool servers for client applications, with
RBAC and auditing applied at the gateway. Clients therefore hold one credential and one
URL rather than a credential per tool server, and tool access is granted per connector
instead of being all-or-nothing.

## Procedure

1. **Add the server.** Decide remote or local:
   - *Remote* — externally hosted, added by URL. Constraints: HTTPS only, DNS host name
     required (**no IP addresses**), default port 443, public CA-signed TLS certificate,
     pinned MCP protocol version.
   - *Local* — container deployed and lifecycle-managed inside the NAI cluster.
2. **Create an MCP client key.** API Client Keys → MCP Client Keys → Create a New Key,
   selecting its connector. As with inference keys, copy it when shown.
3. **Create the MCP connector**, associating the servers with that key.
4. **Grant the specific tools** the connector may access. Expose tools only when
   necessary — this is the documentation's own guidance and the reason to prefer the
   gateway.
5. **Verify** by having the client list its tools and call one, rather than assuming
   registration worked.

Completion criterion: the client sees exactly the granted tools, and no more.

## Pitfalls

- **Tool names over 34 characters are silently ignored** by most MCP clients. Rename the
  tool at the source; you will get no error otherwise. This is the highest-value gotcha
  in this skill.
- **An IP address instead of a DNS name** fails for remote servers. The requirement is a
  host name, not just reachability.
- **Self-signed certificates fail.** A public CA-signed certificate is required for remote
  servers.
- **Reserved header prefixes cannot be used** for per-client rate limiting or header
  forwarding: `X-Nutanix`, `x-ai-eg`, `Authorization`, `x-vsr`.
- **Per-client rate limiting modes are mutually exclusive.** Identifying by API client key
  and by request header cannot both be configured; switching requires deleting the first
  configuration. In header mode the client must actually send the header, or the budget is
  not applied.

## Verification

- The client enumerates only the granted tools.
- Tool names are within the 34-character limit.
- If rate limiting is configured in header mode, confirm the header arrives at the
  gateway rather than only being present in client config.

## Validation gates

- Whether the deployed release has MCP governance enabled, and its NAI version.
- Whether one key spans inference and MCP, or they are separate key types — release notes
  and procedure pages describe this differently. Do not assert either.
- Rate limiting is a Tech Preview capability; confirm it is available before designing
  around it.
