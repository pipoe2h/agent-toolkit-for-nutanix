#!/usr/bin/env python3
"""Validate Agent Plugins packages under plugins/.

These are structural checks that mirror the normative rules of the Agent Plugins
1.0.0 specification. The canonical JSON Schemas at
https://agent-plugins.org/schemas/1.0.0/ remain authoritative for the manifest and
MCP configuration documents; this script is a dependency-free gate for CI, not a
replacement for validating against them.

Client-specific extension directories and per-client install files are out of
scope by design.

Stdlib only. Exit 0 when every package is valid, non-zero on a hard error.

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
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1", "[::1]"}
LOOPBACK_RE = re.compile(r"^127(?:\.\d{1,3}){3}$")
HEADER_NAME_RE = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)
    print(f"  ERROR: {message}", file=sys.stderr)


def warn(message: str) -> None:
    warnings.append(message)
    print(f"  WARNING: {message}", file=sys.stderr)


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
        # Convention in this repository, not a specification requirement.
        warn(
            f"{rel}/plugin.json: name {name!r} differs from the plugin directory name; "
            "the specification does not require them to match"
        )
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


def resolve_command_target(plugin_dir: Path, command: str) -> Path:
    return (plugin_dir / command[2:]).resolve()


def validate_stdio(plugin_dir: Path, server_name: str, server: dict) -> None:
    rel = plugin_dir.name
    where = f"{rel}/mcp.json: server {server_name!r}"
    allowed = {"type", "command", "args", "env", "cwd"}
    for key in sorted(set(server) - allowed):
        fail(f"{where}: unknown field {key!r}")
    command = server.get("command")
    if not isinstance(command, str) or not command:
        fail(f"{where}: command must be a non-empty string")
    elif EXPANSION_RE.search(command):
        fail(
            f"{where}: command is a single executable token; placeholders are not expanded there"
        )
    elif command.startswith("./"):
        target = resolve_command_target(plugin_dir, command)
        if not str(target).startswith(str(plugin_dir.resolve())):
            fail(f"{where}: command path escapes the plugin root: {command}")
        elif not target.is_file():
            fail(f"{where}: command path does not exist: {command}")
        elif not target.stat().st_mode & stat.S_IXUSR:
            fail(f"{where}: command path is not executable: {command}")
    args = server.get("args")
    if args is not None and (
        not isinstance(args, list) or not all(isinstance(a, str) for a in args)
    ):
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


def validate_remote(rel: str, server_name: str, server: dict) -> None:
    where = f"{rel}/mcp.json: server {server_name!r}"
    for key in sorted(set(server) - {"type", "url", "headers"}):
        fail(f"{where}: unknown field {key!r}")
    url = server.get("url")
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        fail(f"{where}: url must be an absolute http(s) URL")
    elif url.startswith("http://"):
        host = url.split("//", 1)[1].split("/", 1)[0]
        host = host.rsplit("@", 1)[-1].split(":", 1)[0].strip("[]")
        if not host or not (host in LOOPBACK_HOSTS or LOOPBACK_RE.match(host)):
            fail(f"{where}: non-loopback endpoints must use https")
    headers = server.get("headers")
    if headers is not None:
        if not isinstance(headers, dict) or not all(
            isinstance(v, str) for v in headers.values()
        ):
            fail(f"{where}: headers must map string keys to string values")
        else:
            seen: set[str] = set()
            for key in headers:
                if not HEADER_NAME_RE.match(key):
                    fail(f"{where}: invalid HTTP header name {key!r}")
                lowered = key.lower()
                if lowered in seen:
                    fail(f"{where}: duplicate header name {key!r} differing only by case")
                seen.add(lowered)


def validate_mcp(plugin_dir: Path, config: dict | None) -> None:
    rel = plugin_dir.name
    # MCP configuration is an optional component: a missing fixed location is not
    # an error per the discovery rules. A present-but-invalid document still fails.
    if not (plugin_dir / "mcp.json").exists() or config is None:
        return
    for key in sorted(set(config) - {"$schema", "mcpServers"}):
        fail(f"{rel}/mcp.json: unknown top-level field {key!r}")
    if config.get("$schema") != MCP_SCHEMA:
        fail(f"{rel}/mcp.json: $schema must be {MCP_SCHEMA}")
    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        fail(f"{rel}/mcp.json: mcpServers must be an object; an empty object is valid")
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
            validate_stdio(plugin_dir, server_name, server)
        else:
            validate_remote(rel, server_name, server)


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
            # Per the discovery rule this directory is simply not a skill.
            warn(f"{rel}/skills/{child.name}: no SKILL.md, so it is not discovered as a skill")
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

    for plugin_dir in candidates:
        validate_manifest(plugin_dir, load_json(plugin_dir / "plugin.json"))
        mcp_path = plugin_dir / "mcp.json"
        validate_mcp(plugin_dir, load_json(mcp_path) if mcp_path.exists() else None)
        validate_skills(plugin_dir)

    if errors:
        print(f"Plugin validation failed with {len(errors)} error(s).")
        return 1
    suffix = f" ({len(warnings)} warning(s))" if warnings else ""
    print(f"Validated {len(candidates)} plugin package(s){suffix}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
