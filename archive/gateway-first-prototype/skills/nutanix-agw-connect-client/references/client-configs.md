# Client configuration shapes

Shared rules: the base URL always carries the gateway prefix
`https://<nai-fqdn>/enterpriseai/gateway/v1`, and the model identifier is always the
unified endpoint name.

Every value in angle brackets is a **placeholder you must replace**. These are config
templates, not ready-to-run files. In particular, the context and output limits are **not**
recommendations or defaults: custom endpoints get no catalogue metadata, and the actual
values come from the model deployed behind the endpoint. The quoted limit placeholders
below must be replaced with JSON integers.

## OpenCode — `opencode.json` (project) or `~/.config/opencode/opencode.json` (user)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "<provider-id>": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Nutanix Agent Gateway",
      "options": {
        "baseURL": "https://<nai-fqdn>/enterpriseai/gateway/v1",
        "apiKey": "{env:NUTANIX_AGW_KEY}"
      },
      "models": {
        "<unified-endpoint-name>": {
          "name": "<unified-endpoint-name>",
          "limit": { "context": "<model-context-window>", "output": "<model-max-output>" }
        }
      }
    }
  },
  "model": "<provider-id>/<unified-endpoint-name>"
}
```

- `npm` must be `@ai-sdk/openai-compatible` for anything speaking
  `/v1/chat/completions`.
- The provider ID must match the ID used at connect time, or the credential is not found.
- **`limit.context` / `limit.output` are required in practice** because custom providers do
  not inherit model metadata. Replace both quoted placeholders with JSON integers from the
  deployed model's own documentation; do not copy guessed token limits into a deployment.

## Hermes Agent — `~/.hermes/config.yaml`

```yaml
providers:
  nai-agw:
    api: https://<nai-fqdn>/enterpriseai/gateway/v1
    key_env: NUTANIX_AGW_KEY
    transport: chat_completions
    default_model: <unified-endpoint-name>
    models:
      <unified-endpoint-name>:
        context_length: <model-context-window>
model:
  provider: custom:nai-agw
  default: <unified-endpoint-name>
```

- The secret goes in `~/.hermes/.env`, never in `config.yaml`.
- Declare `context_length`: Hermes rejects models under 64,000 tokens and custom endpoints
  get no automatic catalogue metadata. Use the deployed model's real window.

## Not yet written

LibreChat, Claude Code environment overrides, and raw OpenAI SDK examples are not yet
captured here. Add them as sections to this file rather than as new files.
