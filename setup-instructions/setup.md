# Agent setup workflow — Nutanix

This file is read by an AI coding agent after the user pastes the Agent Setup prompt on `setup-instructions/setup.md`. It guides the user through a first, read-only connection to an authorized customer-managed Prism Central using the official Nutanix V4 API MCP Server.

This repository is an independent prototype, not an official Nutanix product. The upstream MCP server currently labels itself a Technical Preview and non-production. Before each run, read the current upstream [README](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/README.md), [quickstart](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/quickstart.md), and [authentication/security guide](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/authentication.md). Follow those if they differ from this file.

## Safety contract

- **No secrets in chat.** Never ask the user to paste a password, API key, token, or private key into the conversation. Use a secure local prompt, protected environment injection, or the official secret manager path supported by their agent/runtime.
- **Read-only first.** Keep the upstream MCP `READ_ONLY_MODE` enabled (currently documented default: `true`) and use a least-privilege identity. Verify the effective mode rather than trusting a presumed default.
- **TLS verification stays enabled.** Upstream documents `PC_INSECURE=false` as the default. Do not suggest disabling TLS verification to make setup pass. If a lab uses a self-signed certificate, prefer installing its CA in the host trust store; any temporary lab-only exception requires the operator's explicit decision and must never be described as production guidance.
- **No writes in this setup.** Do not perform mutating API calls, turn off read-only mode, run Ansible, run mutating SDK/API scripts, or apply Terraform/OpenTofu. Generated automation is for user review and execution only.
- **No error-based tool fallback.** A failed MCP call may indicate a network, TLS, authentication, authorization, invalid-input, or Prism Central service problem. Diagnose it. Do not switch to another credential or tool to get around a denial.
- **Preserve existing configuration.** Never overwrite existing agent MCP servers, project rules, or config files. If the correct merge is unclear, show the intended change and ask the user before writing.
- **Human approval gate.** Before installing software, changing an MCP client config, storing a credential locally, or contacting Prism Central, explain the changes and ask for explicit approval. Respect cancellation.

## Before setup: gather non-secret information

Ask for the missing items together; do not request secret values in chat:

1. Which agent client and version will connect (e.g. Claude Code, Codex, Cursor, another MCP-compatible client)?
2. Which machine will run the MCP server, and can it reach the customer's Prism Central network?
3. What is the Prism Central IP/FQDN and port? The current upstream default is `9440`; verify this against the customer's deployment. Never guess an address.
4. What Prism Central and AOS versions are installed, if known? V4 namespaces and operations vary by release/deployment.
5. Does Prism Central present a certificate trusted by the MCP host?
6. Has the administrator provided an authorized least-privilege identity suitable for read-only discovery? Do not ask them to send its credential in chat.
7. Is this an isolated non-production lab? The MCP server is currently a Technical Preview.

If the host cannot route to Prism Central, stop before installation or configuration. Explain that the user needs an authorized host/network path first; this repo does not create a tunnel or public endpoint.

## Procedure

Each phase is a gate. Explain what will change, get approval where marked, execute only that phase, verify it, then continue. If a phase fails, stop and report the actual error and safe next diagnostic; do not improvise around it.

### Phase 1 — Discover local prerequisites (read-only)

- Identify OS, shell, agent client/version, Git, Python (upstream currently requires Python 3.11+), whether the MCP client supports local stdio servers, and whether a Python virtual environment tool is available.
- Check network/DNS/TCP reachability only after the user has supplied the exact host and approved the check. Do not send credentials during connectivity checks.
- Check whether the MCP server already exists locally and whether an MCP server with the same name is already configured. Do not change anything yet.
- Read current upstream quickstart/security docs; confirm the actual current package/install method and commands rather than relying on training data or old snippets.

**Success:** prerequisites and missing pieces are reported without credentials being displayed or config changed.

### Phase 2 — Explain and approve installation

Summarize the install method, source/release or commit, files/locations that would be created, required dependencies, network destinations, credential storage plan, and MCP config file to be modified. Note explicitly that upstream marks the server as Technical Preview/non-production.

Ask for approval before installing. Do not run an opaque downloaded shell script. Prefer the upstream documented Python package workflow in an isolated virtual environment; inspect pinned dependencies and use the current upstream procedure. If installation requires a privilege escalation or an untrusted source, stop and ask.

**Success:** the user approved the precise install and it completed from the verified upstream source.

### Phase 3 — Configure credentials securely

Use the current upstream-supported auth method. Nutanix v4 API key authentication has specific account/version requirements; do not assume all user types support API keys. If the right credential or permissions are uncertain, direct the user to their Prism Central administrator. Do not create service accounts, API keys, roles, or policies as part of this read-only setup.

Configure the secret through a secure local mechanism. Ensure the `.env` (if used) is ignored by Git and has appropriate file permissions. Keep `PC_INSECURE=false` and `READ_ONLY_MODE=true` unless current upstream semantics differ; if they differ, stop and re-evaluate this contract before continuing. Never print `.env`, command environments, API keys, or raw authorization headers.

**Success:** local config is present, secret values were not displayed, TLS verification is enabled, and effective read-only mode is confirmed.

### Phase 4 — Initialize and validate

Follow current upstream instructions to fetch Prism Central-compatible API artifacts and validate connectivity. Artifacts are specific to the Prism Central target; do not reuse them when switching environments. Do not run `serve-stdio` manually if the selected client starts it automatically; follow the upstream/client-specific setup.

Read and summarize validation output with secrets redacted. Interpret unavailable namespaces as possible deployment/version coverage differences; distinguish those from network errors, auth failures, or artifact-download failures.

**Success:** validation reports a ready connection to the intended PC, with TLS verification active and no unresolved auth/network errors.

### Phase 5 — Configure the agent client

Show the exact agent config entry using absolute paths as required by that client and the MCP server's current upstream config. Preserve all existing MCP entries and unrelated settings. The entry must pass credentials through the secure local mechanism, not as committed literals. Explain any user-specific config change, then get approval before writing it.

If the config file already contains the same server name or has an unfamiliar schema, stop and ask how to merge it rather than replacing it.

**Success:** config parses, existing entries remain unchanged, and the client recognizes the Nutanix server after a documented reload/restart.

### Phase 6 — Verify with a low-risk read-only test

First ask the agent to list the available Nutanix MCP tools. Then, after the user approves the exact query, run a narrow read-only discovery request (e.g. inspect an operation schema/permissions or list a small page of VMs). Do not expose sensitive data in the chat; summarize minimally. Verify it came from the intended Prism Central, not a different profile/target.

**Success:** MCP handshake completes and one authorized read-only request succeeds against the intended target. Do not call setup complete if only the MCP process started but no client handshake was verified.

## If the requested task is not available over MCP

Use the method-selection skill at `skills/nutanix-automation-method-selection/SKILL.md`. Confirm the task is genuinely absent from the discovered operation catalog and not blocked by permissions. Then evaluate official `nutanix.ncp` Ansible coverage, V4 SDK/API coverage, and Nutanix provider coverage for OpenTofu/Terraform against the actual target versions. Explain the choice and generate artifacts only for human review/execution in this MVP.

## Finish

Report the verified Prism Central identity/version only if safe and necessary; never include credential material. Summarize which phases passed, which remain blocked, the server/client versions, effective read-only/TLS posture, and any operations unavailable due to API namespace/version coverage. Link to current upstream docs and remind the user of the Technical Preview/non-production status.
