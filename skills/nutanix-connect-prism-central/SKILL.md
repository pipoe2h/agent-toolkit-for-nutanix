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
- A trusted Prism Central TLS certificate. Keep verification enabled; stop if certificate validation fails and arrange a trusted certificate/CA path. Never disable verification for this first-connection workflow.

## Procedure

1. **Inspect the current state.** Identify the agent client/version, OS, Python version, existing MCP configuration, Prism Central endpoint (only if already safely available), and network location. Do not change existing client config without approval.
2. **Read upstream material.** Confirm current install commands, config schema, supported MCP clients, preview status, authentication, credential-write behavior, TLS URL construction, and security guidance from official upstream docs and code. Do not copy stale commands from this skill.
3. **Keep first scope narrow.** Use only local stdio, HTTPS on the documented 9440 port, effective `READ_ONLY_MODE=true`, TLS verification enabled, and one authorized read-only inventory request. Never perform infrastructure writes or bypass a failed authorization/network/TLS check.
4. **Collect credentials privately.** Once installation succeeds, provide the user the exact `configure_nutanix_credentials.py` command to run in a separate local terminal. Before they run it, obtain approval and disclose that the upstream `.env` stores plaintext credentials with mode `0600`; never ask for details in chat/client forms. The helper uses hidden input, enforces HTTPS/read-only settings, captures raw output and confirms completion. If it cannot be run, tell the user why and the next step.
After adding the MCP server entry, fully quit and relaunch OpenCode so it starts the configured local server. Then verify it in OpenCode's MCP view (`/mcps` on current versions) and confirm the server is connected and its tools appear. The exact status command can vary by OpenCode release; consult the installed version's docs. A CLI config listing alone does not prove the running session has connected. After tools appear, perform one read-only query.

Completion criterion: the intended agent lists actual MCP tools and successfully performs an authorized read-only query against the intended Prism Central, with TLS verification enabled and no credential exposed. If blocked at credentials, report it as blocked rather than connected.

## Codex setup example

The canonical setup workflow uses the separate-terminal credential helper. Do not put secrets in Codex config; set only server command, args, and working directory after helper success.



## OpenCode setup example

The canonical setup workflow uses the separate-terminal credential helper. Do not put secrets in OpenCode JSON config; set only server command, args, and working directory after helper success.



## Troubleshooting order

1. Is the MCP process installed and executable by the agent client?
2. Is the command path absolute and are all required files/artifacts present?
3. Can the process host resolve and reach the Prism Central endpoint on the expected port?
4. Does TLS validation pass with the configured trust chain?
5. Does the selected credential authenticate, and does the identity have the required V4 operation permissions?
6. Is the requested API namespace/operation actually present for this Prism Central release and deployment?
7. Is the request valid for the operation schema?

Do not change the transport or switch to Ansible to mask a failure in steps 1–5. Ansible is an alternate task implementation only after confirming the requested operation is not exposed or is better handled as repeatable automation.

## Safety notes

- MCP stdio is a local process boundary, not a remote cloud service. Control the machine and user account that run the process.
- Verify effective read-only settings and enforce PC RBAC independently.
- Tool discovery can include operations with different permissions; inspect operation permissions before any sensitive call.
- Never enable writes for a convenience test. This toolkit's MVP deliberately stays read-only.
- Do not treat an agent's confirmation prompt as a substitute for Prism Central RBAC.
- Credential setup uses a separate local hidden-input helper; disclose plaintext-at-rest storage and exact permissions, and never ask for secrets in chat.

## Validation gates

- Upstream repository currently labels the server Technical Preview and non-production; re-check before each release.
- Client-specific configuration schema and launch behavior must be verified against the installed client version.
- Codex CLI and IDE currently share MCP config; verify exact supported keys and working-directory behavior against the installed Codex version.
- Actual PC/AOS V4 API availability, namespace support, and RBAC requirements depend on the target deployment.
- A dedicated least-privilege identity and certificate trust chain must be confirmed on the user's environment.
- A successful validation-only check does not prove the agent client can launch the process; test the full client handshake separately.

## References

- `references/connection-basics.md` — network/runtime model, upstream facts, and deployment-specific questions.
