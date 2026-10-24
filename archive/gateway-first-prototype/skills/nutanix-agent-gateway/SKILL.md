---
name: nutanix-agent-gateway
description: "Routes Nutanix Agent Gateway tasks to the correct skill. Covers connecting OpenAI-compatible clients, API client keys and unified endpoints, MCP servers and connectors, and rate limiting. Use when configuring, integrating, or troubleshooting Nutanix Enterprise AI Agent Gateway, unified endpoints, MCP governance, or agent traffic control. Not for Private Inference model deployment or cluster installation."
license: Apache-2.0
metadata:
  version: "0.1.0"
  owner: jose-gomez
---

# Nutanix Agent Gateway

## Overview

Nutanix Agent Gateway is the control layer in Nutanix Enterprise AI (NAI) that governs
traffic from agents to LLMs and from agents to MCP servers. It is the governance plane,
not the model-hosting plane — model deployment is Private Inference and is out of scope
here.

**Works best with** a deployed Nutanix environment that exposes Prism Central V4 APIs. This collection starts with the Nutanix V4 API MCP Server for read-only discovery. The server is currently published as a Technical Preview and is not for production workloads. The connection host must be able to reach Prism Central on TCP 9440, and the agent client must support local MCP over stdio.

Use this router to choose the access method; it is not itself a connection, credential store, or authorization layer. See `references/connection-basics.md` for the deployment boundary, security assumptions, and supported alternatives.

## How to use this skill

1. Match the user's request against the routing table below. Match on meaning.
2. Load the target skill and tell the user which one you loaded.
3. Read this skill's `references/gateway-facts.md` before making any claim about a URL
   path, field label, or credential flow.
4. If the request is in scope but no skill covers it yet, say so rather than improvising.
5. Skills state their own validation gates. Report those to the user; do not silently
   promote a gate to a fact.

## Routing table

| The request is about | Load | Notes |
|---|---|---|
| Pointing a client, SDK, or agent at the gateway | `nutanix-agw-connect-client` | Base URL, key, model identifier |
| Creating or managing an API client key | `nutanix-agw-connect-client` | Key is shown once |
| Creating a unified endpoint, or choosing load balance vs fallback | `nutanix-agw-connect-client` | Endpoint name becomes the model name |
| Adding MCP servers, MCP client keys, or connectors | `nutanix-agw-mcp-governance` | Remote vs local servers |
| Limiting tokens or spend per client | `nutanix-agw-mcp-governance` | Rate limiting; check release label |
| Installing, sizing, or upgrading NAI itself | *not in this collection* | Out of scope |
| Deploying or serving models | *not in this collection* | That is Private Inference |

## Two concepts that decide most answers

**The gateway prefix.** Unified endpoint URLs carry a prefix before the OpenAI-compatible
path. The documented example is `/enterpriseai/gateway/v1/chat/completions`, so a client
base URL is `https://<nai-fqdn>/enterpriseai/gateway/v1`. A client configured without the
prefix will fail.

**The unified endpoint name is the model name.** Clients declare the unified endpoint's
name in their `model` field; the gateway resolves the backend from it. A mismatch here is
the most likely "model not found" in the wild, and it is also why clients must declare
their models explicitly — a model-listing endpoint is not on the documented
OpenAI-compatible surface.

## Reference

- `references/gateway-facts.md` — the verified surface, credential flows, and the list of
  what is still unconfirmed.

## Validation gates

Everything in `references/gateway-facts.md` is documented by Nutanix. The following are
open on the user's deployment and must be checked rather than assumed:

- Whether a single API key covers both inference and MCP access, or whether they are
  separate key types.
- Whether rate limiting is enabled on the deployed release.
- The NAI and NKP versions actually installed.
