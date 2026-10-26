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


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


class PluginScaffoldTests(unittest.TestCase):
    def test_validator_passes_on_this_repository(self):
        result = run("scripts/validate-plugin.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 1 plugin package(s).", result.stdout)

    def test_manifest_declares_the_portable_schema_and_matches_directory(self):
        manifest = (PLUGIN / "plugin.json").read_text()
        self.assertIn(
            '"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"', manifest
        )
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

    def test_validator_rejects_placeholder_in_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/broken-plugin"
            (plugin / "skills").mkdir(parents=True)
            (plugin / "plugin.json").write_text(
                '{"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", '
                '"name": "broken-plugin"}'
            )
            (plugin / "mcp.json").write_text(
                '{"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", '
                '"mcpServers": {"x": {"type": "stdio", "command": "${PLUGIN_ROOT}/run"}}}'
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("placeholders are not expanded", result.stderr)

    def test_validator_rejects_unknown_manifest_field_and_bad_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/broken-plugin"
            plugin.mkdir(parents=True)
            (plugin / "plugin.json").write_text(
                '{"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", '
                '"name": "other-name", "mcpServer": {}}'
            )
            result = run("scripts/validate-plugin.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown top-level field", result.stderr)
            self.assertIn("must match the plugin directory name", result.stderr)


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
