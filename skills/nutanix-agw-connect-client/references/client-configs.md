# Client configuration shapes

Shared rules: the base URL always carries the gateway prefix
`https://<nai-fqdn>/enterpriseai/gateway/v1`, and the model identifier is always the
unified endpoint name.

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
          "name": "Nutanix Agent Gateway",
          "limit": { "context": 128000, "output": 16384 }
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
- `limit.context` / `limit.output` are required in practice — custom providers do not
  inherit model metadata.

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
        context_length: 128000
model:
  provider: custom:nai-agw
  default: <unified-endpoint-name>
```

- The secret goes in `~/.hermes/.env`, never in `config.yaml`.
- Declare `context_length`: Hermes rejects models under 64,000 tokens and custom endpoints
  get no automatic catalogue metadata.

## Not yet written

LibreChat, Claude Code environment overrides, and raw OpenAI SDK examples are not yet
captured here. Add them as sections to this file rather than as new files.
