---
name: nutanix-agw-connect-client
description: "Connect an OpenAI-compatible client, SDK, or agent to Nutanix Agent Gateway. Covers base URL and gateway prefix, API client keys, unified endpoints, load balance versus fallback, and the model identifier. Use when configuring OpenCode, Hermes Agent, a chat UI, or a raw SDK against Nutanix Enterprise AI Agent Gateway."
license: Apache-2.0
metadata:
  version: "0.1.0"
---

# Connect a client to the Agent Gateway

## When to Use

- Pointing a coding agent, chat UI, or SDK at a Nutanix gateway unified endpoint.
- Diagnosing a client that cannot reach the gateway or reports "model not found".
- Choosing between load balance and fallback order for agent traffic.

Not for: installing NAI, deploying models, or MCP server governance (see
`nutanix-agw-mcp-governance`).

## Prerequisites

- A deployed NAI instance with an FQDN that resolves to the ingress IP, and a CA-signed
  TLS certificate covering it. NAI is HTTPS only — a client set to plain HTTP will fail.
- A **unified endpoint** created, with its **name** noted.
- An **API client key** assigned to that endpoint.

## Procedure

1. **Create the API client key.** Left nav → API Client Keys → Create a New Key → name it
   → assign it from the Unified Endpoints dropdown → Create → **Copy Key now**. It is
   shown once; a lost key must be regenerated.
2. **Note the unified endpoint name.** This exact string is the model identifier clients
   send. Do not paraphrase it.
3. **Configure the client** with base URL `https://<nai-fqdn>/enterpriseai/gateway/v1`
   and that endpoint name as the model. The gateway prefix is not optional.
4. **Choose the backend strategy.** Prefer **Fallback Order** for agent traffic so the
   gateway re-routes rather than returning an error to the editor mid-task.
5. **Verify** with a request the client actually issues — a chat completion through the
   client, not a `curl` against a path the client never calls.

Completion criterion: the client returns a completion, and the model identifier in the
client's config is character-for-character the unified endpoint name.

## Client configuration

Per-client config shapes are in `references/client-configs.md`. Shared across all clients:
the gateway is not in any model catalogue a client ships with, so every client is
configured as a **custom OpenAI-compatible endpoint** rather than through a one-click
connect flow.

The configuration examples show the intended shape; claims about endpoint paths,
field names, and credential workflows still need to be checked against the official
Nutanix procedure for the deployed release. This skill currently provides no direct
source links or per-claim citations; do not treat the examples as independently sourced
documentation.

## Pitfalls

- **Missing gateway prefix.** The single most common misconfiguration. A base URL of
  `https://<fqdn>/v1` is wrong; it needs `/enterpriseai/gateway/v1`.
- **No model-listing endpoint.** A client configured to enumerate models from the server
  will find nothing. Declare the model explicitly.
- **Custom endpoints get no catalogue metadata.** In clients that track context windows,
  declare the context length yourself; do not rely on detection.
- **Load balance hides a dead backend** until every backend is dead. Fallback order is the
  better default for interactive agent traffic.
- **Do not persist the key in plaintext config** where the client supports environment or
  file substitution.

## Verification

- A completion succeeds through the client's own code path.
- The exact model string in the client config matches the unified endpoint name.
- On failure, check prefix, then key assignment, then TLS — in that order.

## Validation gates

- Client-version-specific behaviour (e.g. whether a client passes custom-provider options
  through to API calls) must be confirmed on the installed version, not assumed.
- Context-length limits must be taken from the deployed model behind the endpoint.
- The official source page and release supporting each documented path, field, and
  credential step must be identified and linked before publishing or operational use.
