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
5. **Configure credentials outside chat.** Use the current upstream-supported method. Do not place secrets in committed files, command-line arguments, screenshots, or chat. Ensure any `.env` file is excluded from version control and has restrictive permissions. Confirm from the installed server's current configuration docs that its working directory is where `.env` is loaded.
6. **Initialize API artifacts** using the upstream-documented command. Artifacts are Prism Central-version-specific; do not reuse them when switching PC instances. Treat unavailable namespaces as potential coverage differences, not a reason to bypass access controls.
7. **Validate before connecting the agent.** Run the upstream validation-only command, if available. Confirm DNS/routing, TCP 9440, TLS verification, authentication, and the resolved namespace list. Do not continue on a failed auth/TLS check.
8. **Configure the agent client.** Installation does not register the server automatically. Add the MCP server entry using the target client's current official instructions; preserve existing MCP entries and settings, use absolute paths where required, and set its working directory to the server project directory containing `.env` and artifacts if the upstream loader requires that. Do not set `READ_ONLY_MODE=false` for this first workflow.
9. **Verify discovery and use.** Confirm the agent client lists the Nutanix server and exposes tools after reload/restart. Ask it to inspect available operations, then (if `vmm.listVms` is present and permitted) request a small read-only page of VMs using the operation schema and user approval. Read the result back and confirm it came from the intended Prism Central.

Completion criterion: the intended agent lists the MCP tools and successfully performs an authorized read-only query against the intended Prism Central, with TLS verification enabled and no credential exposed in chat or logs.

## Codex setup example

Codex CLI and IDE use a shared MCP config. Follow the current [Codex MCP documentation](https://developers.openai.com/codex/mcp.md) and upstream Nutanix configuration docs for the installed versions. For a local stdio server, configure `~/.codex/config.toml` with a `[mcp_servers.nutanix]` entry containing the absolute `command`, `args = ["serve-stdio"]`, and `cwd` set to the MCP server project directory. Do not add credential literals; the server reads its local `.env` from its working directory per current upstream configuration docs. If the user's installed version documents different behavior, follow that instead.

After configuration, verify with `codex mcp list`; in the Codex TUI use `/mcp` to inspect active servers and tools. Restart/reopen the session if needed. Then request a read-only VM test: ask Codex to list the available Nutanix tools, inspect `vmm.listVms` schema/permissions if present, and request at most five VMs showing only name and power state. Do not hard-code executor arguments; derive them from the discovered schema. If tools are absent or the query fails, troubleshoot MCP registration/process startup, `cwd` and artifact paths, network/TLS/auth, and operation permissions in that order. Never bypass a failure by changing credentials or switching tools.

## OpenCode setup example

OpenCode uses its own JSON `opencode.json`/`opencode.jsonc` configuration, not Codex TOML. Follow the official [OpenCode MCP documentation](https://opencode.ai/docs/mcp-servers/). Under the existing top-level `mcp` key, add a local server with `type: "local"`, a `command` array, `cwd` set to the MCP project directory, `enabled: true`, and an appropriate timeout. Use absolute paths within the runtime environment. Never overwrite existing config or put secrets in JSON; the `cwd` must allow the Nutanix server to load its operator-managed `.env` and artifacts according to current upstream docs.

After saving, restart/reload OpenCode and check MCP status/tools using the interface and diagnostics documented for the installed OpenCode version. Ask OpenCode to list Nutanix tools, inspect `vmm.listVms` schema/permissions, then request at most five VMs with only name and power state using the actual discovered operation arguments. If the tools do not appear, debug config parsing, server process startup, command/`cwd`/artifacts, then network/TLS/auth. Do not give Codex instructions to an OpenCode user.

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
- Codex CLI and IDE currently share MCP config; verify exact supported keys and working-directory behavior against the installed Codex version.
- Actual PC/AOS V4 API availability, namespace support, and RBAC requirements depend on the target deployment.
- A dedicated least-privilege identity and certificate trust chain must be confirmed on the user's environment.
- A successful validation-only check does not prove the agent client can launch the process; test the full client handshake separately.

## References

- `references/connection-basics.md` — network/runtime model, upstream facts, and deployment-specific questions.
