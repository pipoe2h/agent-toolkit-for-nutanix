"""Contract tests for the Agent Plugins package scaffold."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/nutanix-core"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


def scaffold(root: Path, name: str = "broken-plugin") -> Path:
    """Create a minimal plugin at root/plugins/<name> with a valid manifest."""
    plugin = root / "plugins" / name
    (plugin / "skills").mkdir(parents=True)
    (plugin / "plugin.json").write_text(
        '{"$schema": "%s", "name": "%s"}' % (PLUGIN_SCHEMA, name)
    )
    return plugin


class PluginScaffoldTests(unittest.TestCase):
    def test_validator_passes_on_this_repository(self):
        result = run("scripts/validate-plugin.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 1 plugin package(s).", result.stdout)

    def test_manifest_declares_the_portable_schema_and_matches_directory(self):
        manifest = (PLUGIN / "plugin.json").read_text()
        self.assertIn('"$schema": "%s"' % PLUGIN_SCHEMA, manifest)
        self.assertIn('"name": "nutanix-core"', manifest)

    def test_mcp_command_is_a_single_plugin_relative_token(self):
        command = re.search(r'"command": "([^"]+)"', (PLUGIN / "mcp.json").read_text()).group(1)
        self.assertTrue(command.startswith("./"), command)
        self.assertNotIn("${", command)
        target = PLUGIN / command[2:]
        self.assertTrue(target.is_file(), command)
        self.assertTrue(target.stat().st_mode & 0o100, f"{command} is not executable")

    def test_mcp_entry_carries_no_credentials(self):
        config = (PLUGIN / "mcp.json").read_text().lower()
        for token in ("password", "api_key", "apikey", "secret", "token", "pc_username"):
            self.assertNotIn(token, config)

    def test_packaged_skills_are_discoverable_immediate_children(self):
        skills = sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir())
        self.assertEqual(
            skills,
            [
                "nutanix-automation-method-selection",
                "nutanix-connect-prism-central",
                "nutanix-readonly-inventory",
            ],
        )
        for name in skills:
            self.assertTrue((PLUGIN / "skills" / name / "SKILL.md").is_file(), name)

    def test_packaged_credential_helper_matches_canonical_copy(self):
        canonical = (ROOT / "scripts/configure_nutanix_credentials.py").read_bytes()
        packaged = (PLUGIN / "scripts/configure_nutanix_credentials.py").read_bytes()
        self.assertEqual(canonical, packaged)

    def test_connect_skill_helper_reference_resolves_inside_the_package(self):
        skill = PLUGIN / "skills/nutanix-connect-prism-central/SKILL.md"
        for reference in re.findall(r"`(scripts/[^`]+)`", skill.read_text()):
            self.assertTrue((PLUGIN / reference).is_file(), reference)

    def test_launcher_does_not_depend_on_ambient_home(self):
        launcher = (PLUGIN / "scripts/launch-nutanix-mcp").read_text()
        self.assertNotIn("${HOME:-", launcher)
        self.assertIn("PLUGIN_DATA", launcher)

    def test_validator_rejects_placeholder_in_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "mcp.json").write_text(
                '{"$schema": "%s", "mcpServers": {"x": {"type": "stdio", '
                '"command": "${PLUGIN_ROOT}/run"}}}' % MCP_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("placeholders are not expanded", result.stderr)

    def test_validator_rejects_unknown_manifest_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "plugin.json").write_text(
                '{"$schema": "%s", "name": "broken-plugin", "mcpServer": {}}' % PLUGIN_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown top-level field", result.stderr)

    def test_name_directory_mismatch_is_a_warning_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "plugin.json").write_text(
                '{"$schema": "%s", "name": "other-name"}' % PLUGIN_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("differs from the plugin directory name", result.stderr)

    def test_empty_mcp_servers_object_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "mcp.json").write_text(
                '{"$schema": "%s", "mcpServers": {}}' % MCP_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_non_loopback_http_endpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "mcp.json").write_text(
                '{"$schema": "%s", "mcpServers": {"x": {"type": "streamable-http", '
                '"url": "http://prism.example.test/mcp"}}}' % MCP_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("non-loopback endpoints must use https", result.stderr)

    def test_loopback_http_endpoint_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "mcp.json").write_text(
                '{"$schema": "%s", "mcpServers": {"x": {"type": "streamable-http", '
                '"url": "http://localhost:9440/mcp"}}}' % MCP_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_header_name_differing_only_by_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "mcp.json").write_text(
                '{"$schema": "%s", "mcpServers": {"x": {"type": "streamable-http", '
                '"url": "https://example.test/mcp", "headers": '
                '{"X-Tenant": "a", "x-tenant": "b"}}}}' % MCP_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate header name", result.stderr)

    def test_reserved_env_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = scaffold(root)
            (plugin / "mcp.json").write_text(
                '{"$schema": "%s", "mcpServers": {"x": {"type": "stdio", "command": "npx", '
                '"env": {"PLUGIN_DATA": "/tmp/x"}}}}' % MCP_SCHEMA
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("reserved variable", result.stderr)


class SkillParityTests(unittest.TestCase):
    def test_plugin_skills_match_canonical_skills(self):
        result = run("scripts/sync-plugin-skills.py", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_parity_check_detects_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "skills", root / "skills")
            shutil.copytree(PLUGIN, root / "plugins/nutanix-core")
            drifted = root / "plugins/nutanix-core/skills/nutanix-readonly-inventory/SKILL.md"
            drifted.write_text(drifted.read_text() + "\nextra line\n")
            result = run("scripts/sync-plugin-skills.py", "--root", str(root), "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("differs: SKILL.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
