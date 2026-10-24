# Agent setup workflow — Nutanix

This file is read by an AI coding agent after the user pastes the Agent Setup prompt on `setup-instructions/setup.md`. It guides the user through a first, read-only connection to an authorized customer-managed Prism Central using the official Nutanix V4 API MCP Server.

**Container workflow:** when launched via this repo's Dev Container, OpenCode already has the two toolkit skills from `.agents/skills/`. The agent should load and follow them during setup. An end user who is not using this repo's Dev Container can paste this setup prompt without cloning the repo or pre-installing skills; this instruction file is the complete bootstrap workflow and references public upstream MCP documentation as needed. Skills are supplemental, not a prerequisite for MCP installation.

This repository is an independent prototype, not an official Nutanix product. The upstream MCP server currently labels itself a Technical Preview and non-production. Before each run, read the current upstream [README](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/README.md), [quickstart](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/quickstart.md), and [authentication/security guide](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/authentication.md). Follow those if they differ from this file.

## Safety contract

- **No secrets in chat or credential prompts.** Never ask the user to paste a password, API key, token, or private key into the conversation, and never ask them to type a secret into an agent prompt. For this guided setup, the operator prepares the MCP server's local `.env` file themselves. The agent may check only that the file exists, is ignored by Git, has restrictive permissions, and contains required variable names; it must never display, read back, parse-and-log, or transmit values from that file.
- **Credentials are a prerequisite, not an agent-gathered input.** If the required local `.env` has not been prepared, stop and tell the user setup cannot proceed until they configure it themselves. Do not continue to test credentials, fetch artifacts, configure the MCP client, or contact Prism Central while it is absent or incomplete.
- **Read-only first.** Keep the upstream MCP `READ_ONLY_MODE` enabled (currently documented default: `true`) and use a least-privilege identity. Verify the effective mode rather than trusting a presumed default.
- **TLS verification stays enabled.** Upstream documents `PC_INSECURE=false` as the default. Do not suggest disabling TLS verification to make setup pass. If a lab uses a self-signed certificate, prefer installing its CA in the host trust store; any temporary lab-only exception requires the operator's explicit decision and must never be described as production guidance.
- **No writes in this setup.** Do not perform mutating API calls, turn off read-only mode, run Ansible, run mutating SDK/API scripts, or apply Terraform/OpenTofu. Generated automation is for user review and execution only.
- **No error-based tool fallback.** A failed MCP call may indicate a network, TLS, authentication, authorization, invalid-input, or Prism Central service problem. Diagnose it. Do not switch to another credential or tool to get around a denial.
- **Preserve existing configuration.** Never overwrite existing agent MCP servers, project rules, or config files. If the correct merge is unclear, show the intended change and ask the user before writing.
- **Human approval gate.** Before installing software, changing an MCP client config, storing a credential locally, or contacting Prism Central, explain the changes and ask for explicit approval. Respect cancellation.

## Before setup: gather non-secret information

Ask for missing non-secret items together. Do not ask the user to provide a credential value in chat or enter it into an agent prompt:

1. Which agent client and version will connect (e.g. Claude Code, Codex, Cursor, another MCP-compatible client)?
2. Which machine will run the MCP server, and can it reach the customer's Prism Central network?
3. What is the Prism Central IP/FQDN and port? The current upstream default is `9440`; verify this against the customer's deployment. Never guess an address.
4. What Prism Central and AOS versions are installed, if known? V4 namespaces and operations vary by release/deployment.
5. Does Prism Central present a certificate trusted by the MCP host?
6. Is the user prepared to configure the MCP server's local `.env` themselves with an authorized least-privilege identity, without showing the values to the agent? The file will be needed before any credential-bearing validation or Prism Central API call.
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

Summarize the install method, source/release or commit, files/locations that would be created, required dependencies, network destinations, credential storage plan, and MCP config file to be modified. Note explicitly that upstream marks the server as Technical Preview/non-production. Do not configure an MCP client before the user-managed `.env` gate in Phase 2b has passed.

Ask for approval before installing. Do not run an opaque downloaded shell script. Prefer the upstream documented Python package workflow in an isolated virtual environment; inspect pinned dependencies and use the current upstream procedure. If installation requires a privilege escalation or an untrusted source, stop and ask.

**Success:** the user approved the precise install and it completed from the verified upstream source.

### Phase 3 — Operator prepares local credentials

After installation, but **before connectivity validation, artifact initialization, MCP client configuration, or API requests**, require the operator to prepare the local `.env` file.

1. Tell the user: “I can't proceed to connect or validate until you configure the MCP server's local `.env` file yourself. Do not paste the values here. Copy the upstream `.env.example` to `.env` in the MCP server project directory, fill in the Prism Central host/port and exactly one supported auth method, keep `PC_INSECURE=false` and `READ_ONLY_MODE=true`, and save the file with owner-only permissions. Tell me when you have done this; do not send the file or its contents.”
2. Do not print secret placeholders together with instructions that invite pasting them into chat. Do not ask the user to type the secret into a conversational prompt. If the user asks where to put a value, refer to the variable name in the local `.env` and stop there.
3. Wait for the user to confirm the file is prepared. Then, only with approval, perform metadata-only checks: test the file exists, is ignored by Git, has POSIX mode `0600` or stricter, and contains required key names. Do not source the file, display lines, hash values, echo environment variables, enable shell tracing, or capture command output that could include credentials. A safe checker must emit only `PASS`/`FAIL` and missing variable names.
4. If checks fail or the user has not prepared the file, report the exact non-secret fix and wait. Do not continue around this gate.

Do not have the agent create/populate `.env` by writing secret values, even if a local file editor is available. The operator creates and edits the file outside the agent conversation. The agent may verify only its metadata and variable-name presence under the restrictions above.

**Success:** user confirms they prepared `.env`; the approved metadata-only checks pass; no secret value entered chat, tool output, logs, or repository.

### Phase 4 — Load toolkit guidance when available

- If a toolkit skill is available to this agent, load `nutanix-connect-prism-central` before proceeding; load `nutanix-automation-method-selection` only if the requested task needs method selection. Skills are supplemental and must not make the flow depend on a particular agent.
- If either skill is unavailable (for example, the user pasted this prompt into a different agent without cloning this repo), continue using the procedure and upstream links in this file. Do not require the user to clone a source repository just to access setup guidance.
- Never treat an installed skill as the MCP server, a credential, or authorization; it is guidance only.

**Success:** relevant local skill guidance is loaded if available, or the agent continues from this file without blocking.

### Phase 5 — Initialize and validate after the credential gate

Only proceed after Phase 3 succeeded and the user approves contacting the exact Prism Central endpoint. Follow current upstream instructions to fetch Prism Central-compatible API artifacts and validate connectivity. Artifacts are specific to the Prism Central target; do not reuse them when switching environments. Do not run `serve-stdio` manually if the selected client starts it automatically; follow the upstream/client-specific setup. Keep command output redacted; never inspect or print `.env` contents.

Read and summarize validation output with secrets redacted. Interpret unavailable namespaces as possible deployment/version coverage differences; distinguish those from network errors, auth failures, or artifact-download failures.

**Success:** validation reports a ready connection to the intended PC, with TLS verification active and no unresolved auth/network errors.

### Phase 6 — Configure the agent client

First verify from current upstream docs/code how the MCP process obtains credentials at runtime. The upstream quickstart distinguishes `.env` for `init` from AI-client runtime configuration; do not assume the `.env` automatically reaches a child process just because it exists. The runtime must load the operator-managed `.env` locally (for example, a documented `cwd`/config-file mechanism if supported), or use a client-supported local environment-variable reference whose value the operator configures outside the agent conversation. If no secure, documented path is available for this client, stop and explain the limitation; never fall back to embedding credentials in agent configuration or asking for them in chat.

**General rule:** installing the server does not register it with an agent. Follow the selected client's current official MCP configuration procedure, explain the exact config path/entry, preserve existing entries, obtain approval before edits, then restart/reload as that client requires. The MCP process must run on a host/container that can reach Prism Central. For this upstream server, the documented settings loader reads `.env` from its current working directory; set the client MCP process working directory (`cwd` or equivalent) to the MCP server project directory containing the operator-managed `.env` and generated artifacts. Verify this behavior against the installed upstream version before relying on it. Do not copy secrets into the agent config.

**Codex CLI / IDE example (local stdio):** current Codex documentation supports adding stdio servers with `codex mcp add <name> -- <command>` and config in `~/.codex/config.toml`. Since the command alone does not set the server's working directory, the reliable approach is an approved `config.toml` entry that explicitly sets `cwd` to the MCP project directory:

```toml
[mcp_servers.nutanix]
command = "/absolute/path/to/ntnx-api-mcp-server/.venv/bin/nutanix-mcp"
args = ["serve-stdio"]
cwd = "/absolute/path/to/ntnx-api-mcp-server"
startup_timeout_sec = 30
tool_timeout_sec = 120
enabled = true
```

These paths are examples, not universal values. Resolve them on the machine/container where Codex runs. Do not include credentials in TOML; the server loads its `.env` from `cwd` according to the upstream configuration docs. Explain that Codex's user-level config is shared by its CLI and IDE extension; a project-scoped `.codex/config.toml` may be used only when the project is trusted and the user wants project scope. Verify with `codex mcp list`, then start/restart a Codex session and use `/mcp` in its TUI to confirm the server and tools initialize. If either command is unavailable in the installed version, consult that version's official Codex docs rather than guessing.

For OpenCode, Claude Code, Cursor, or another client, use that client's official local-stdio setup and verify its supported `cwd`/working-directory field. If it cannot launch the command from the directory containing `.env`, do not assume secrets are inherited; find a documented secure equivalent or stop and explain the gap.

Show the exact non-secret client config entry, using absolute paths as required by the client. Preserve all existing MCP entries and unrelated settings. Explain each config change and ask approval before writing it. Never print a secret value or put credential literals in config. If the client requires values in a UI, the user must enter them directly in that UI without relaying them to the agent; otherwise stop if that does not meet the `.env` requirement.

If the config file already contains the same server name or has an unfamiliar schema, stop and ask how to merge it rather than replacing it.

**Success:** the secure runtime credential-loading path is verified against current upstream and client documentation, config contains no secrets, existing entries remain unchanged, and the client recognizes the Nutanix server after a documented reload/restart.

### Phase 7 — Verify with a low-risk read-only test

First ask the agent to list the available Nutanix MCP tools. If the VM namespace is present, ask it to inspect the `listVms` operation schema/permissions, then request a small page (up to five) of VMs using the discovered `vmm` namespace executor and the exact arguments from the schema. This is a read-only request; get user approval before sending it. Return only minimal fields such as VM name and power state, and avoid exposing sensitive inventory. Verify the result came from the intended Prism Central. If `vmm`/`listVms` is absent, report that accurately and inspect available namespaces/operations; do not invent a tool name or switch tools to bypass authorization.

**Success:** MCP handshake completes and one authorized read-only request succeeds against the intended target. Do not call setup complete if only the MCP process started but no client handshake was verified.

## If the requested task is not available over MCP

Use the method-selection skill at `skills/nutanix-automation-method-selection/SKILL.md`. Confirm the task is genuinely absent from the discovered operation catalog and not blocked by permissions. Then evaluate official `nutanix.ncp` Ansible coverage, V4 SDK/API coverage, and Nutanix provider coverage for OpenTofu/Terraform against the actual target versions. Explain the choice and generate artifacts only for human review/execution in this MVP.

## Finish

Report the verified Prism Central identity/version only if safe and necessary; never include credential material. Summarize which phases passed, which remain blocked, the server/client versions, effective read-only/TLS posture, and any operations unavailable due to API namespace/version coverage. Link to current upstream docs and remind the user of the Technical Preview/non-production status.
