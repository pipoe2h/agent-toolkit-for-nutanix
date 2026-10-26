# OpenCode Dev Container (optional)

The Dev Container is optional guidance for trying OpenCode, not a prerequisite for connecting your existing agent. It installs OpenCode and toolkit skills only; it does not install/configure the Nutanix MCP server. Follow the [first-connection workflow](../../setup-instructions/setup.md). After the MCP entry is written, fully quit and relaunch OpenCode to load the server. Verify `nutanix` in the reopened session's MCP view (`/mcps` on current versions) before attempting a query. Credential entry uses a local hidden prompt in the helper; it must never happen in chat. Credentials are stored in `.env` with owner-only permissions, plaintext at rest. Review this limitation before continuing.

The Dev Container is model-provider agnostic: it does not choose a model, set an API key, or force Nutanix Enterprise AI. The optional NAI example below configures model inference only; that is separate from Prism Central MCP access.


## Optional: OpenCode with Nutanix Enterprise AI

`opencode.nai.example.json` is an optional example for users who want OpenCode to call an OpenAI-compatible NAI unified endpoint. It is not loaded by default. Replace `<nai-fqdn>`, `<documented-openai-compatible-base-path>`, and `<unified-endpoint-name>` with values verified for your NAI deployment. Supply `NUTANIX_AGW_API_KEY` through a secure local environment mechanism; never put the key in this file or commit it.

A safe local workflow is:

1. Copy the example to an ignored local file, for example `opencode.nai.local.json` in the repository root.
2. Replace the endpoint and model placeholders.
3. Set the API key in your terminal environment without adding it to shell history or a committed file.
4. Run `OPENCODE_CONFIG=opencode.nai.local.json opencode` from the repository root.
5. Verify the exact endpoint path, unified endpoint model ID, API key assignment, and certificate trust for your NAI release before testing.

The Dev Container itself doesn't contact NAI until OpenCode is run with this optional configuration. The NAI inference connection is separate from the Prism Central MCP connection described in the Agent Setup workflow. The Nutanix V4 API MCP Server is upstream-labeled Technical Preview/non-production; use a non-production lab for MCP testing.
