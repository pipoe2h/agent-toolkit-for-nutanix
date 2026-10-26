#!/usr/bin/env python3
"""Validate Agent Plugins packages under plugins/.

Checks the portable contract only: plugin.json conformance, mcp.json shape and
path/command rules, and the skills/ discovery layout. Client-specific extension
directories and per-client install files are out of scope by design.

Stdlib only. Exit 0 when every package is valid, non-zero otherwise.

Usage:
    python3 scripts/validate-plugin.py                 # validate every plugin
    python3 scripts/validate-plugin.py --plugin nutanix-core
    python3 scripts/validate-plugin.py --root /some/repo
"""

from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from pathlib import Path

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"

MANIFEST_FIELDS = {
    "$schema", "name", "version", "description", "author",
    "homepage", "repository", "license", "keywords", "extensions",
}
AUTHOR_FIELDS = {"name", "email", "url"}
NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
EXPANSION_RE = re.compile(r"\$\{(PLUGIN_ROOT|PLUGIN_DATA)\}")
RESERVED_ENV = {"PLUGIN_ROOT", "PLUGIN_DATA"}
TRANSPORTS = ("stdio", "streamable-http", "sse")
CWD_RE = re.compile(r"^(?:\./|\$\{PLUGIN_ROOT\}(?:/|$)|\$\{PLUGIN_DATA\}(?:/|$))")

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)
    print(f"  ERROR: {message}", file=sys.stderr)


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        fail(f"{path.name}: missing {path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        fail(f"{path}: top level must be a JSON object")
        return None
    return data


def validate_manifest(plugin_dir: Path, manifest: dict | None) -> None:
    rel = plugin_dir.name
    if manifest is None:
        return
    for key in sorted(set(manifest) - MANIFEST_FIELDS):
        fail(f"{rel}/plugin.json: unknown top-level field {key!r}")
    if manifest.get("$schema") != PLUGIN_SCHEMA:
        fail(f"{rel}/plugin.json: $schema must be {PLUGIN_SCHEMA}")
    name = manifest.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or not 1 <= len(name) <= 64:
        fail(f"{rel}/plugin.json: invalid name {name!r}")
    elif name != plugin_dir.name:
        fail(f"{rel}/plugin.json: name {name!r} must match the plugin directory name")
    for key in ("version", "description", "homepage", "repository", "license"):
        if key in manifest and not isinstance(manifest[key], str):
            fail(f"{rel}/plugin.json: {key} must be a string")
    author = manifest.get("author")
    if author is not None:
        if not isinstance(author, dict):
            fail(f"{rel}/plugin.json: author must be an object")
        else:
            for key in sorted(set(author) - AUTHOR_FIELDS):
                fail(f"{rel}/plugin.json: author has unknown field {key!r}")
            for key, value in author.items():
                if not isinstance(value, str):
                    fail(f"{rel}/plugin.json: author.{key} must be a string")
    keywords = manifest.get("keywords")
    if keywords is not None and (
        not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords)
    ):
        fail(f"{rel}/plugin.json: keywords must be an array of strings")
    extensions = manifest.get("extensions")
    if extensions is not None and not isinstance(extensions, dict):
        fail(f"{rel}/plugin.json: extensions must be an object")


def validate_stdio(rel: str, server_name: str, server: dict) -> None:
    where = f"{rel}/mcp.json: server {server_name!r}"
    allowed = {"type", "command", "args", "env", "cwd"}
    for key in sorted(set(server) - allowed):
        fail(f"{where}: unknown field {key!r}")
    command = server.get("command")
    if not isinstance(command, str) or not command:
        fail(f"{where}: command must be a non-empty string")
    elif EXPANSION_RE.search(command):
        fail(f"{where}: command is a single executable token; placeholders are not expanded there")
    elif command.startswith("./"):
        target = (plugin_dir_of(rel) / command[2:]).resolve()
        if not target.is_file():
            fail(f"{where}: command path does not exist: {command}")
        elif not target.stat().st_mode & stat.S_IXUSR:
            fail(f"{where}: command path is not executable: {command}")
    args = server.get("args")
    if args is not None and (not isinstance(args, list) or not all(isinstance(a, str) for a in args)):
        fail(f"{where}: args must be an array of strings")
    env = server.get("env")
    if env is not None:
        if not isinstance(env, dict) or not all(isinstance(v, str) for v in env.values()):
            fail(f"{where}: env must map string keys to string values")
        else:
            for key in env:
                if key in RESERVED_ENV:
                    fail(f"{where}: env must not override reserved variable {key}")
    cwd = server.get("cwd")
    if cwd is not None and (not isinstance(cwd, str) or not CWD_RE.match(cwd)):
        fail(f"{where}: cwd must be ./, ${{PLUGIN_ROOT}}-rooted, or ${{PLUGIN_DATA}}-rooted")


def plugin_dir_of(rel: str) -> Path:
    for candidate in plugin_roots:
        if candidate.name == rel:
            return candidate
    return Path(rel)


def validate_mcp(plugin_dir: Path, config: dict | None) -> None:
    rel = plugin_dir.name
    if config is None:
        return
    for key in sorted(set(config) - {"$schema", "mcpServers"}):
        fail(f"{rel}/mcp.json: unknown top-level field {key!r}")
    if config.get("$schema") != MCP_SCHEMA:
        fail(f"{rel}/mcp.json: $schema must be {MCP_SCHEMA}")
    servers = config.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        fail(f"{rel}/mcp.json: mcpServers must be a non-empty object")
        return
    for server_name, server in sorted(servers.items()):
        if not isinstance(server, dict):
            fail(f"{rel}/mcp.json: server {server_name!r} must be an object")
            continue
        transport = server.get("type")
        if transport not in TRANSPORTS:
            fail(f"{rel}/mcp.json: server {server_name!r} has invalid type {transport!r}")
            continue
        if transport == "stdio":
            validate_stdio(rel, server_name, server)
            continue
        allowed = {"type", "url", "headers"}
        for key in sorted(set(server) - allowed):
            fail(f"{rel}/mcp.json: server {server_name!r}: unknown field {key!r}")
        url = server.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            fail(f"{rel}/mcp.json: server {server_name!r}: url must be http(s)")
        headers = server.get("headers")
        if headers is not None and (
            not isinstance(headers, dict) or not all(isinstance(v, str) for v in headers.values())
        ):
            fail(f"{rel}/mcp.json: server {server_name!r}: headers must map strings to strings")


def validate_skills(plugin_dir: Path) -> None:
    rel = plugin_dir.name
    skills_dir = plugin_dir / "skills"
    if not skills_dir.exists():
        return
    if not skills_dir.is_dir():
        fail(f"{rel}/skills: exists but is not a directory")
        return
    for child in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_file = child / "SKILL.md"
        if not skill_file.is_file():
            fail(f"{rel}/skills/{child.name}: missing SKILL.md")
            continue
        text = skill_file.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            fail(f"{rel}/skills/{child.name}/SKILL.md: frontmatter must start at byte 0")
            continue
        match = re.search(r"\n---\n", text[4:])
        if not match:
            fail(f"{rel}/skills/{child.name}/SKILL.md: closing frontmatter delimiter missing")
            continue
        frontmatter = text[4 : match.start() + 4]
        name = re.search(r"^name:\s*(.*?)\s*$", frontmatter, re.MULTILINE)
        description = re.search(r"^description:\s*(.*?)\s*$", frontmatter, re.MULTILINE)
        if not name or name.group(1).strip("\"'") != child.name:
            fail(f"{rel}/skills/{child.name}/SKILL.md: name must match the skill directory")
        if not description or not description.group(1).strip("\"'"):
            fail(f"{rel}/skills/{child.name}/SKILL.md: description is required")
        for link in re.findall(r"`(references/[^`]+)`", text):
            if not (child / link).is_file():
                fail(f"{rel}/skills/{child.name}: broken reference {link}")


plugin_roots: list[Path] = []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--plugin", action="append", default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    plugins_dir = root / "plugins"
    if not plugins_dir.is_dir():
        print("No plugins/ directory; nothing to validate.")
        return 0

    candidates = sorted(p for p in plugins_dir.iterdir() if p.is_dir())
    if args.plugin:
        candidates = [p for p in candidates if p.name in set(args.plugin)]
    if not candidates:
        print("No plugin directories matched.")
        return 0

    plugin_roots.extend(candidates)
    for plugin_dir in candidates:
        validate_manifest(plugin_dir, load_json(plugin_dir / "plugin.json"))
        validate_mcp(plugin_dir, load_json(plugin_dir / "mcp.json"))
        validate_skills(plugin_dir)

    if errors:
        print(f"Plugin validation failed with {len(errors)} error(s).")
        return 1
    print(f"Validated {len(candidates)} plugin package(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
