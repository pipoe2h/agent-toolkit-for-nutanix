# Agent setup workflow — Nutanix first connection

This workflow is for an agent to set up one local stdio connection to an authorized customer-managed Prism Central, then verify one read-only inventory request. This repository is an independent prototype, not an official Nutanix product. Upstream [`nutanix/ntnx-api-mcp-server`](https://github.com/nutanix/ntnx-api-mcp-server) currently labels itself Technical Preview/non-production. Re-read its [quickstart](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/quickstart.md), [configuration reference](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/configuration.md), and [authentication/security guide](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/authentication.md) before any setup; this workflow does not override newer upstream behavior.

## Outcome and limits

Success means the chosen agent actually discovers the Nutanix MCP tools and performs one authorized, small, read-only query against the intended Prism Central. An install, `init`, validation command, or textual claim without the live agent handshake and read is not success.

The user already has an agent/model subscription and must authorize access to Prism Central. The machine running the local MCP subprocess needs an existing authorized route to Prism Central; this workflow does not create a tunnel. Use only a non-production environment while upstream labels the server Technical Preview. Stop if any prerequisite or safety property cannot be confirmed.

## Non-negotiable safety rules

- Never request or accept a password, API key, token, or private key in chat. Never place a secret in the agent config, command arguments, logs, screenshots, repository, or generated output.
- Do not write, mutate, or delete anything in Prism Central. Keep server-side `READ_ONLY_MODE=true`, use PC RBAC least privilege, and make one GET-only inventory call.
- Enforce HTTPS. Upstream settings code currently constructs `http://` when `PC_PORT != 9440`; do not use a custom port for this setup. `PC_INSECURE=false` means certificate verification is enabled, not that the URL is HTTPS on every port.
- Never disable TLS verification to make setup pass. Stop on certificate failures and explain that a trusted certificate/CA path is needed.
- Preserve existing MCP configuration, credentials, files, and unrelated settings. Do not overwrite a same-named server. Backups may contain secrets: do not print or attach them.
- Ask for explicit approval before installation, configuration changes, credential storage, or contacting the target. Approval describes the precise operations, files, upstream revision, and endpoints. Respect cancellation. If privilege escalation is requested, stop and have the user perform that action.
- Diagnose failures at their source; never change tools or credentials to bypass access denials.

## Gather only what cannot be discovered

First inspect locally, without network requests or edits: operating system, agent and version, Python/Git/uv availability, existing MCP configuration and Nutanix server install. Do not dump configuration files that may contain credentials. Identify the runtime host where the agent launches local MCP processes.

Ask only for these missing items:

1. The exact Prism Central IP/FQDN, if not already known from a safe local config. Do not guess it. This first workflow requires HTTPS port `9440`.
2. Confirmation the user is authorized to connect to this PC and it is non-production.
3. If the user wants to continue after the installation plan is explained, approval of that exact plan.

Do not require the user to look up PC/AOS versions before setup; discover them only if a specific error requires them. Test TCP reachability only after exact target and approval, without credentials. If unreachable, stop and explain the network-path prerequisite.

## Critical credential blocker

The checked upstream revision `dc447b3f948662b94c1ed61812eb0d1bb221470d` has no documented interactive, non-echoing credential wizard. Its authentication guide recommends `.env`/environment/config credentials, states credentials are plaintext at rest in `.env`, and warns that `nutanix-mcp init`/`refresh` can write credentials to `.env`. Its `src/cli.py::_save_config_dotenv` writes `PC_PASSWORD` and other values using `Path.write_text` without setting restrictive mode. The app's settings source uses a repository `.env` and process environment; config-file values override environment values. Do not assume a generic MCP client's `cwd` selects a safe credential file.

Therefore, until a separately verified private-entry method exists, do not ask a beginner to create/edit `.env`, do not have the agent write secrets, and do not run `init` with credentials. Stop at this gate and explain the exact limitation. Do not configure an incomplete MCP entry, contact Prism Central with credentials, or call setup successful. A human may choose to do a separately documented local credential step outside this handoff, but the agent must not observe the secret entry. Do not claim agent-led end-to-end setup in README while this blocker remains.

## Procedure when the credential gate is resolved

### 1. Inspect upstream and local state

Pin and record the upstream commit/release. Inspect the current documented package/install route, all settings sources and precedence, credential writes, logging, TLS URL construction, read-only enforcement, and chosen agent's current local stdio configuration schema. A git clone of upstream is code to execute: show its source/revision and destinations before approval. Do not execute an opaque install script.

### 2. Explain and receive bounded approval

List exact destinations, dependency provenance, files to create/change, network endpoints (Prism Central: HTTPS 9440; developer namespace service only if upstream requires it), credential mechanism, and expected user-only action. State preview/non-production status, plaintext-at-rest risks if relevant, and no writes to PC. Ask for approval of this complete bounded scope. Reconfirm if scope changes.

### 3. Install and configure local runtime

After approval, use the verified upstream procedure in an isolated virtual environment; record revision and package versions. Do not use `latest` without pinning/recording. Prepare directories and non-secret config with restrictive permissions. Preserve existing client config by parsing and merging the named server entry; if parsing/merging or name collision is unclear, stop. Never write secrets into agent config. Configure `PC_PORT=9440`, `PC_INSECURE=false`, and `READ_ONLY_MODE=true` explicitly in the effective runtime source only after safely resolving environment overrides. Do not proceed if inherited environment or CLI arguments can override safety settings.

### 4. Private credential entry, initialization, and validation

Use only the private credential mechanism approved and validated at the critical gate. It must not echo or log secret values, must safely handle special characters, and must produce a local credential source with owner-only access without printing it. The mechanism must ensure initialization cannot rewrite credentials into a permissive `.env`; inspect the exact pinned upstream code first. If this cannot be guaranteed, stop.

Only then, after explicit approval for contacting the exact target, run upstream initialization and validation with output reviewed for leakage. Verify effective URL is HTTPS to the intended host on port 9440, TLS verification is on, read-only mode is on, and exactly one auth method is active. Emit only allowlisted safe facts/booleans; never print full settings, env dumps, exceptions with values, or credential hashes. Do not treat key-name checks or documented defaults as proof of effective runtime posture. Stop on any mismatch/auth/TLS/network failure.

### 5. Register the client and verify the real query

Merge the local stdio server using the client version's official configuration, with absolute executable path and only non-secret values. Start/reload the client as documented. Confirm it reports the Nutanix server and actual tools. Ask the agent to inspect the discovered read operation schema and permissions; request up to five VM records only if the discovered `vmm` operation supports it. Keep returned fields minimal (name, power state); do not expose broader inventory. If no suitable read is available, report that accurately and stop; never invent tool names or switch to bypass access controls.

### 6. Report result honestly

Report the agent/server versions, pinned upstream revision, effective TLS/read-only checks, and whether the MCP client handshake and real read passed. Separate local validation from live acceptance. If blocked, state the exact stage, reason, and one safe next action. Never report "connected" based solely on successful installation or validation.

## Supplemental guidance

Toolkit skills and the optional Dev Container are not prerequisites for this first connection. If available, the `nutanix-connect-prism-central` skill may supplement this workflow, but may not relax any safety gate. Do not introduce Ansible, SDK/API scripts, Terraform/OpenTofu, Agent Gateway, or write tasks into this milestone.
