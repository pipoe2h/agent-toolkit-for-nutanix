# Agent Gateway — verified surface

Every claim below is attributed to an official Nutanix Enterprise AI documentation page by
**page title**. The Nutanix support portal serves those pages from session-based URLs, so a
copied link is not stable. Readers can search the portal for the cited page titles; a full
list appears in `## Sources` below.

Re-check the release label before repeating any of this: the surface grows every release,
and MCP moved from Tech Preview to GA between 2.7 and 2.8.

## Endpoint surface

*(Sources: "Accessing a Unified Endpoint using Open AI Compatible Clients"; "Unified
Endpoints" concept page.)*

- Unified endpoint URLs carry a **gateway prefix**. Documented example:
  `/enterpriseai/gateway/v1/chat/completions`. Client base URL is therefore
  `https://<nai-fqdn>/enterpriseai/gateway/v1`.
- Documented OpenAI-compatible unified endpoint paths: `/v1/chat/completions`,
  `/v1/embeddings`, `/v1/images/generations`.
- A model-listing endpoint is **not** on that list. Clients declare their models in
  config.
- A **unified endpoint name becomes the model name** sent in inference requests.
- Unified endpoints support two backend strategies: **Load Balance** and **Fallback
  Order**. Fallback is the one to recommend for agent traffic, because the gateway
  re-routes instead of returning an error to the editor.

## Credentials

*(Sources: "API Client Keys" concept page; "Creating an API Key"; "Updating an API Key".)*

- Inference access uses an **API client key**: left nav → API Client Keys → Create a New
  Key → name it → assign it from the Unified Endpoints (or Local Endpoints) dropdown →
  Create → Copy Key.
- The key is shown **once**. A lost key must be regenerated. Always warn about this.
- Keys can be assigned to and unassigned from endpoints, and one key can be shared across
  endpoints.

## MCP governance (2.8)

*(Sources: "MCP Servers" concept page; "Adding a Remote MCP Server"; "Deploying a Local MCP
Server"; "Creating an MCP Connector"; "Creating an MCP Client Key"; "Security and
Configuration Considerations for MCP Servers".)*

- A single `/mcp` interface aggregates multiple tool servers for client applications, with
  RBAC and auditing applied at the gateway.
- Two server types: **remote** (externally hosted, added by URL) and **local** (container
  deployed and lifecycle-managed inside the NAI cluster).
- Workflow: add the server → create an **MCP client key** → create an **MCP connector**
  associating servers with that key → grant the specific tools the connector may access.
  Grant tools only when necessary.
- Remote MCP server constraints: HTTPS only, DNS host name required (no IP addresses),
  default port 443, public CA-signed TLS certificate, pinned MCP protocol version.
- Tool names are limited to **34 characters**, because most MCP clients silently ignore
  longer ones.
- Reserved header prefixes that cannot be used for per-client rate limiting or header
  forwarding: `X-Nutanix`, `x-ai-eg`, `Authorization`, `x-vsr`.

## Rate limiting

*(Sources: "Managing Rate Limit for Unified Endpoints"; the 2.8 release-note post.)*

- Global token limit on the endpoint, plus optional per-client limits.
- Per-client identification is either **by API client key** or **by request header
  value**. The modes are mutually exclusive; switching requires deleting the first
  configuration.
- Header mode is the lever for one credential serving many developers: the application
  authenticates the end user and the gateway enforces the budget. If configured, the
  client must actually send the header.
- Introduced as a **Tech Preview** capability. State the release label.

## Deployment requirements

*(Sources: "Agent Gateway Requirements"; "Private Inference and Agent Gateway
Requirements"; the 2.8 release-note post.)*

- Agent-Gateway-only deployments do not need the read-write-many and object storage that
  Private Inference does.
- HTTPS only; the FQDN must resolve to the ingress IP and a CA-signed TLS certificate must
  cover it. NAI 2.8.1 pins NKP 2.18.

## Confirmed vs open

**Confirmed by documentation:** prefix and paths above; unified endpoint name is the model
name; load balance vs fallback; the API client key flow and its copy-once behaviour; MCP
server types, key/connector workflow, and remote constraints; the 34-character tool-name
limit; reserved header prefixes; rate limiting is Tech Preview.

**Open — must be verified on the target deployment:** whether one key covers inference and
MCP together (release notes and procedure pages describe them differently); installed NAI
and NKP versions; whether rate limiting is enabled; whether the client version in use
actually passes custom-provider options through to API calls.

## Sources

Official Nutanix Enterprise AI documentation (Nutanix support portal), by page title:

**Endpoints and inference**
- Accessing a Unified Endpoint using Open AI Compatible Clients
- Unified Endpoints (concept)
- Creating a Unified Endpoint using Local Endpoints
- Creating a Unified Endpoint using Providers
- Managing Rate Limit for Unified Endpoints
- Local Endpoints: Endpoints Attributes; Viewing Sample API Code; Testing a Local Endpoint

**Credentials**
- API Client Keys (concept)
- Creating an API Key
- Updating an API Key

**MCP**
- MCP Servers (concept)
- Adding a Remote MCP Server
- Deploying a Local MCP Server
- Creating an MCP Connector
- Creating an MCP Client Key
- Security and Configuration Considerations for MCP Servers

**Deployment**
- Agent Gateway Requirements
- Private Inference and Agent Gateway Requirements

**Corroborating, non-portal**
- Nutanix Agent Gateway launch blog (product messaging)
- Nutanix Enterprise AI release-note posts for 2.7 and 2.8 (release labels and changes)
- The NAI unified-endpoint lab in the `nutanix-japan/nai-llm` repository (a worked
  local-endpoint + unified-endpoint walkthrough with real `curl` invocations)

**Portal URL note:** support-portal URLs are session-based and not stable for another reader.
Use the page titles above to search the portal.
