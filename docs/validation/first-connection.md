# First-connection upstream validation notes

## Scope

Read-only source inspection of `nutanix/ntnx-api-mcp-server`; no package installed, no credentials used, and no Prism Central contacted.

## Revision and sources

- Repository HEAD fetched from GitHub on 2026-10-25: `dc447b3f948662b94c1ed61812eb0d1bb221470d`.
- `docs/quickstart.md`
- `docs/configuration.md`
- `docs/authentication.md`
- `src/config/settings.py`
- `src/cli.py`

## Findings

- Quickstart offers username/password or API key via `.env`/configuration; no private interactive credential-entry wizard is documented.
- `src/cli.py::_save_config_dotenv` writes PC host, username, password, API key, port and TLS setting into `.env` using `Path.write_text`. It does not set restrictive file permissions itself.
- `init` invokes `_save_config_dotenv(settings)` after initialization. Upstream authentication guidance explicitly warns about plaintext credential persistence and recommends inspecting `.env` after init/refresh.
- `src/config/settings.py` declares an env file at the upstream project root. `load_settings` builds environment values and then overlays config-file values, so a file can override inherited environment values. A client working-directory field is not sufficient evidence that secrets can safely be isolated.
- `Settings.pc_base_url` selects HTTPS only when `pc_port == 9440`; any other port results in HTTP. The first connection must therefore use 9440 with TLS verification enabled. Do not infer HTTPS from `PC_INSECURE=false` alone.
- Server defaults describe `READ_ONLY_MODE=true` and `PC_INSECURE=false`, but defaults are not proof of effective settings. Conflicting environment/config/CLI values must be resolved before a safe connection.
- Upstream marks the MCP server Technical Preview/non-production.

## Consequence

Current handoff is deliberately blocked before credential entry, initialization, MCP registration, or Prism Central calls. Do not ask the beginner to edit `.env`, do not have an agent write secrets, and do not claim end-to-end setup until a safe private entry mechanism and effective runtime safety verification are proven for a pinned upstream revision.

## Verification limits

This is source/documentation inspection only. No install, CLI execution, MCP handshake, credentials, target reachability, or live inventory query was exercised. Re-check current upstream source before implementation or release.
