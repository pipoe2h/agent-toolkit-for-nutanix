---
name: nutanix-connect-prism-central
description: "Connect an MCP-compatible AI agent to customer-managed Nutanix Prism Central. Covers the Nutanix V4 API MCP Server, stdio client configuration, local network reachability, TLS, least-privilege credentials, initialization, validation, and read-only resource discovery. Use when onboarding or troubleshooting an agent connection to a Nutanix environment."
license: Apache-2.0
metadata:
  version: "0.1.0"
---

# Connect an AI agent to Prism Central

## When to use

- Set up or verify a local MCP connection from an AI client to Prism Central.
- Identify what the installed Nutanix V4 API MCP Server can discover or execute.
- Diagnose connection failures without bypassing authentication, authorization, or TLS controls.

This skill documents the official Nutanix V4 API MCP Server, whose upstream repository currently identifies it as a Technical Preview. It does not make an inaccessible Prism Central reachable: the machine running the server must already have the required network path.

## Prerequisites

- An MCP-compatible agent client that can launch a local stdio server.
- Python 3.11+ and Git, as required by the upstream quickstart.
- A customer-authorized Prism Central endpoint exposing the V4 APIs.
- The host running the MCP process can reach the Prism Central API on port 9440 (verify the target deployment and firewall).
- Credentials managed outside chat. Prefer a dedicated low-privilege identity; ensure the account's roles match the intended read-only workflow.
- A trusted Prism Central TLS certificate. Keep verification enabled; self-signed lab certificates require an explicit, temporary lab-only exception.

## Procedure

1. **Inspect the current state.** Identify the agent client, its existing MCP configuration, host OS, Python version, Prism Central/AOS release (if known), and network location. Do not change existing client config without approval.
2. **Read upstream material.** Confirm current install commands, config schema, supported MCP clients, preview status, and security guidance from the official `nutanix/ntnx-api-mcp-server` repository. Do not copy stale commands from this skill if upstream differs.
3. **Choose the runtime host.** Place the MCP process where it can reach Prism Central. This may be the user's workstation, a management VM, or another controlled host; it does not need a public endpoint. Confirm the client can launch that process or otherwise reach its MCP transport.
4. **Install in an isolated environment** following the upstream quickstart. Pin or record the upstream release/commit used. Do not run a `curl | shell` installer without review.
5. **Configure credentials outside chat.** Use the current upstream-supported method. Do not place secrets in committed files, command-line arguments, screenshots, or chat. Ensure any `.env` file is excluded from version control and has restrictive permissions.
6. **Initialize API artifacts** using the upstream-documented command. Artifacts are Prism Central-version-specific; do not reuse them when switching PC instances. Treat unavailable namespaces as potential coverage differences, not a reason to bypass access controls.
7. **Validate before connecting the agent.** Run the upstream validation-only command, if available. Confirm DNS/routing, TCP 9440, TLS verification, authentication, and the resolved namespace list. Do not continue on a failed auth/TLS check.
8. **Configure the agent client.** Add only the MCP server entry documented for that client. Preserve all existing MCP entries and settings. Use absolute paths where required. Do not set `READ_ONLY_MODE=false` for this first workflow.
9. **Verify from the agent.** Ask it to list available discovery operations, inspect one harmless operation schema and required permissions, then perform a narrowly scoped read-only query (for example, list a small page of VMs) only after the user authorizes that query. Read the result back and confirm it came from the intended Prism Central.

Completion criterion: the intended agent lists the MCP tools and successfully performs an authorized read-only query against the intended Prism Central, with TLS verification enabled and no credential exposed in chat or logs.

## Troubleshooting order

1. Is the MCP process installed and executable by the agent client?
2. Is the command path absolute and are all required files/artifacts present?
3. Can the process host resolve and reach the Prism Central endpoint on the expected port?
4. Does TLS validation pass with the configured trust chain?
5. Does the selected credential authenticate, and does the identity have the required V4 operation permissions?
6. Is the requested API namespace/operation actually present for this Prism Central release and deployment?
7. Is the request valid for the operation schema?

Do not change the transport or switch to Ansible to mask a failure in steps 1–5. Ansible is an alternate task implementation only after confirming the requested operation is not exposed or is better handled as repeatable automation.

## Security notes

- MCP stdio is a local process boundary, not a remote cloud service. Control the machine and user account that run the process.
- The upstream preview server describes read-only mode as its default. Verify the effective runtime setting rather than assuming it.
- Tool discovery can include operations with different permissions; inspect operation permissions before any sensitive call.
- Never enable writes for a convenience test. This toolkit's MVP deliberately stays read-only.
- Do not treat an agent's confirmation prompt as a substitute for Prism Central RBAC.

## Validation gates

- Upstream repository currently labels the server Technical Preview and non-production; re-check before each release.
- Client-specific configuration schema and launch behavior must be verified against the installed client version.
- Actual PC/AOS V4 API availability, namespace support, and RBAC requirements depend on the target deployment.
- A dedicated least-privilege identity and certificate trust chain must be confirmed on the user's environment.
- A successful validation-only check does not prove the agent client can launch the process; test the full client handshake separately.

## References

- `references/connection-basics.md` — network/runtime model, upstream facts, and deployment-specific questions.
