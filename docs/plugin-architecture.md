# Plugin architecture

This repository publishes the toolkit two ways: as a **portable Agent Plugin package** under
`plugins/`, and as **canonical skills plus a prompt** under `skills/`, `rules/`, and `prompts/`.
They are one toolkit, not two products, and a check keeps them in sync.

## Layout

```text
plugin.json                         Agent Plugins 1.0.0 manifest for the package
mcp.json                            stdio MCP server entry (credential-free)
plugins/nutanix-core/
  plugin.json                       package manifest
  mcp.json                          package MCP entry
  scripts/launch-nutanix-mcp        resolves the server install, then execs serve-stdio
  skills/<name>/SKILL.md            copies of the canonical skills
skills/<name>/SKILL.md              canonical skills (source of truth)
skills/<name>/references/*.md       canonical reference material
rules/nutanix-agent-rules.md        agent rules for clients that read rules files
prompts/setup.md                    copyable prompt path for clients without plugin support
```

## Rules that keep the two paths honest

1. **Canonical skills live in `skills/`.** Everything under `plugins/*/skills/` is a copy.
   `scripts/sync-plugin-skills.py --check` fails the build when a copy drifts.
2. **The manifest is closed.** Only the fields the Agent Plugins specification defines may
   appear in `plugin.json`; client-specific data goes under `extensions`, keyed by a
   reverse-domain namespace.
3. **`mcp.json` carries no secrets.** The format defines no credential field, and `command`
   takes a single executable token, not a shell command: either a bare name resolved on
   `PATH` or a `./`-relative path inside the package. Placeholders such as `${PLUGIN_ROOT}`
   and `${PLUGIN_DATA}` expand in `args`, `env` values, and `cwd` — never in `command`.
4. **The package never reaches outside itself** except into `${PLUGIN_DATA}`, the writable
   data directory the client owns and that survives plugin updates.
5. **Read-only by default.** No component in the package writes to Prism Central.

## Where per-client distribution fits

Installation, enablement, and marketplaces are client-managed and out of scope for the
portable format. A client-specific install file, marketplace manifest, or hooks directory
belongs in an extension namespace (a top-level directory named for a reverse-domain
namespace, plus optional `extensions` manifest data). None is committed here yet: each one
is client-owned, so it should be added only against that client's documented format and
verified by an actual install.

## Verification

```bash
python3 scripts/validate-skills.py        # canonical skills and references
python3 scripts/validate-plugin.py        # package manifest, MCP entry, packaged skills
python3 scripts/sync-plugin-skills.py --check
bash scripts/test.sh                      # both validators plus the test suite
```
