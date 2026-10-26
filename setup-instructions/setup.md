# Agent setup workflow — Nutanix first connection

This workflow is for an agent to set up one local stdio connection to an authorized customer-managed Prism Central, then verify one read-only inventory request. This repository is an independent prototype, not an official Nutanix product. Upstream [`nutanix/ntnx-api-mcp-server`](https://github.com/nutanix/ntnx-api-mcp-server) currently labels itself Technical Preview/non-production. Re-read its [quickstart](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/quickstart.md), [configuration reference](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/configuration.md), and [authentication/security guide](https://github.com/nutanix/ntnx-api-mcp-server/blob/main/docs/authentication.md) before any setup; this workflow does not override newer upstream behavior.

## Outcome and limits

Success means the chosen agent actually discovers the Nutanix MCP tools and performs one authorized, small, read-only query against the intended Prism Central. An install, `init`, validation command, or textual claim without the live agent handshake and read is not success.

This repo provides an agent-directed first connection to customer-managed Prism Central. Upstream's server is currently Technical Preview/non-production. A private local-terminal step will collect the endpoint and credentials; the agent must not ask you to enter them in chat, client forms, or approval dialogs.

## Non-negotiable safety rules

- Never request or accept a password, API key, token, or private key in chat, in client forms, or in approval dialogs. Never place a secret in the agent config, command arguments, logs, screenshots, repository, or generated output.
- Do not write, mutate, or delete anything in Prism Central. Keep server-side `READ_ONLY_MODE=true`, use PC RBAC least privilege, and make one GET-only inventory call.
- Enforce HTTPS. Upstream settings code currently constructs `http://` when `PC_PORT != 9440`; do not use a custom port for this setup. `PC_INSECURE=false` means certificate verification is enabled, not that the URL is HTTPS on every port.
- Never disable TLS verification to make setup pass. Stop on certificate failures and explain that a trusted certificate/CA path is needed.
- Preserve existing MCP configuration, credentials, files, and unrelated settings. Do not overwrite a same-named server. Backups may contain secrets: do not print or attach them.
- Ask for explicit approval before installation, configuration changes, credential storage, or contacting the target. Approval describes the precise operations, files, upstream revision, and endpoints. Respect cancellation. If privilege escalation is requested, stop and have the user perform that action.
- Diagnose failures at their source; never change tools or credentials to bypass access denials.

## Gather only what cannot be discovered

First inspect locally, without network requests or edits: operating system, agent and version, Python/Git/uv availability, existing MCP configuration and Nutanix server install. Do not dump configuration files that may contain credentials. Identify the runtime host where the agent launches local MCP processes.

Do not ask for the Prism Central hostname/IP, username, authentication method, password, or API key in a chat question, client form, approval dialog, or agent-generated prompt. The local hidden-input helper below gathers the endpoint, auth method, username, and secret. The agent may ask only the non-secret authorization and non-production confirmation as a normal explicit safety gate, without requesting account details.

Ask only for these missing items:

- A first-connection workflow may ask the user only for the non-secret confirmation they are authorized and the target is non-production, plus approval of exact local changes and contacting the target. Do not ask for Prism Central IP/FQDN, username, auth method, password, or API key in a client question/form/dialog. That information is collected by the local helper after installation approval.
- For this tested journey, proceed with `git clone`, venv creation, `pip install`, then offer the helper command plus disclosure that `.env` is plaintext at rest with mode `0600`. Let the helper collect host and credentials privately; once it succeeds, continue with MCP client registration and the read-only query.

## Private credential entry

The helper prints safe progress to standard error while the upstream init runs: it first confirms the Prism Central check is starting, then reports API-definition initialization and periodic elapsed-time updates. Upstream output remains captured and is never displayed.

> The Nutanix installer is ready. Enter your Prism Central sign-in in a separate local terminal so it never enters this chat:
>
> ```bash
> python3 /absolute/path/to/agent-toolkit-for-nutanix/scripts/configure_nutanix_credentials.py /absolute/path/to/ntnx-api-mcp-server
> ```
>
> It asks for the Prism Central address, authentication method, and username if needed, then prompts for the password/API key with input hidden. Do not paste the credential or terminal output here. When it prints that initialization completed, come back and say `done`.

Obtain the helper from this repository: clone the toolkit (`git clone https://github.com/pipoe2h/agent-toolkit-for-nutanix`) or fetch `scripts/configure_nutanix_credentials.py` from the published commit and read it first. Before asking the user to run it, the agent must show the exact script path/revision, read the helper source, verify Python and the server directory exist, explain that `.env` is plaintext at rest but owner-only (`0600`), and get approval. Never download-and-run an uninspected script.

If initialization fails, tell the user the helper's safe error sentence and diagnose that cause without reading or displaying `.env`. To retry after fixing the cause, run the same command with `--retry`; the helper asks for the credential again. Never leave the user with an unexplained blocker, and never ask for credentials in chat.

## Critical caveats

- Upstream `init` stores credentials in `.env`. The helper pre-creates this file with mode `0600` *before* init runs, and refuses to start if a `.env` already exists (so it never overwrites or reuses unknown credentials). Upstream's current `_save_config_dotenv` opens the existing file for writing, so the mode is preserved; the helper re-checks the final mode and refuses to report success if it is not `0600`.
- Credentials are plaintext at rest and readable by any process running as the same OS user. Disclose this before the user enters anything. Do not describe the helper as a vault or as zero-memory handling.
- The helper forces `PC_PORT=9440`, `PC_INSECURE=false`, and `READ_ONLY_MODE=true`, and removes inherited `PC_HOST`/`PC_PORT`/`PC_USERNAME`/`PC_PASSWORD`/`PC_API_KEY`/`PC_INSECURE`/`READ_ONLY_MODE` from the child environment so the user's shell cannot redirect the target or weaken the safety settings. It passes exactly one auth method, captures and discards raw stdout/stderr, and never puts credentials in argv or chat.
- The helper requires POSIX permissions and a real interactive terminal; it refuses non-TTY stdin and refuses to run on Windows.
- Init emits safe stderr progress: starting the Prism Central check over HTTPS 9440, then starting API-definition initialization. If it is still running, the helper prints elapsed time every 10 seconds, then a completion/failure line with total duration. Raw upstream stdout/stderr is captured and suppressed throughout.
- If the user cannot run the helper, give the exact command and explain that setup resumes after they do.
The installation described here has three distinct delays. First, the helper performs `nutanix-mcp init`; it prints safe stage progress and elapsed time because this may take minutes while Prism Central is contacted and API definitions are downloaded. Second, when the MCP client starts `nutanix-mcp serve-stdio`, the server parses the downloaded YAML artifacts and builds its operation catalog before it can answer the MCP `initialize` request. Third, on this upstream revision, `serve-stdio` does not call `validate_startup_readiness`; the separate `run` command does. Do not attribute a reported 14–15 second `serve-stdio` delay to a Prism Central retry unless logs or a reproduction demonstrate that; YAML parsing is an independent startup cost.

No actual MCP handshake was verified in the reported test: `printf 'all requests' | server` closes stdin immediately after writing, which is not the same lifecycle as an MCP client keeping both pipes open and waiting for a response before sending the next message. Do not recommend that method as proof of MCP client compatibility. Do not add a targeted `mcp` SDK pin or change `stdio_server()` based only on the report that the SDK exits when a pipe is initially quiet. Reproduce with the exact installed `mcp`, AnyIO and Python versions and an idle-open-pipe client before asserting a version bug or changing SDK/runtime code. Report verified client handshake and whether the stdio process remains alive while awaiting the first message as separate checks.



1. Inspect current upstream and local state, pin the upstream commit, and get approval for exact local changes and target access.
2. Install the MCP server in an isolated environment using the verified upstream source and version.
3. Run the private credential helper as described above. After it reports success, configure the supported MCP client using its official local-stdio setup. Store no credentials in client config; preserve existing entries, obtain approval, and restart/reload.
4. Confirm real MCP tool discovery, then perform one authorized read-only query (up to five VM names and power states only if the discovered schema supports it). No writes. If no suitable operation exists, state that and stop.
5. Report agent/server versions, pinned upstream revision, credential file permission, effective TLS/read-only posture, and live handshake/query status. For failures, explain the phase, plain-language cause, and one next action; never claim success without the real read.

## Supplemental guidance

Toolkit skills and the optional Dev Container are not prerequisites. Do not introduce Ansible, SDK/API scripts, Terraform/OpenTofu, Agent Gateway, or writes into this first milestone.
