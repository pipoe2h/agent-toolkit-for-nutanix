from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROMPT_RE = re.compile(r"```text\n(.*?)\n```", re.S)


def read_prompt():
    text = (ROOT / "prompts/setup.md").read_text()
    match = PROMPT_RE.search(text)
    if match is None:
        raise AssertionError("Canonical setup prompt must exist")
    return match.group(1)


class SetupHandoffTests(unittest.TestCase):
    def test_prompt_routes_live_connection_before_conditional_setup(self):
        prompt = read_prompt()
        low = prompt.lower()
        self.assertIn(
            "https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/",
            prompt,
        )
        for path in (
            "AGENTS.md",
            "ENTRY.md",
            "setup-instructions/setup.md",
            "skills/nutanix-connect-prism-central/SKILL.md",
            "skills/nutanix-readonly-inventory/SKILL.md",
            "skills/nutanix-readonly-inventory/references/query-contract.md",
            "skills/nutanix-readonly-inventory/references/tool-surface-checks.md",
        ):
            with self.subTest(path=path):
                self.assertIn(path, prompt)
                self.assertTrue((ROOT / path).is_file())
        self.assertIn("current session", low)
        self.assertIn("if connected", low)
        self.assertIn("if no live connection", low)
        self.assertLess(low.index("if connected"), low.index("if no live connection"))
        self.assertIn("ask me what task", low)
        self.assertIn("list my vms", low)
        self.assertIn("do not reinstall", low)
        self.assertIn("no infrastructure writes", low)
        self.assertIn("one authorized, scoped read-only inventory query", low)
        self.assertIn("do not switch to ansible, sdk/api, or terraform/opentofu", low)
        self.assertIn("tls verification enabled", low)
        self.assertIn("least-privilege prism central rbac", low)
        self.assertIn("plaintext", low)
        self.assertIn("approval", low)
        self.assertIn("actionable blocker", low)
        self.assertIn("coverage", low)

    def test_prompt_keeps_setup_out_of_the_connected_branch(self):
        low = read_prompt().lower()
        connected = low.index("if connected")
        disconnected = low.index("if no live connection")
        connected_branch = low[connected:disconnected]
        self.assertIn("entry.md", connected_branch)
        self.assertIn("do not reinstall", connected_branch)
        self.assertNotIn("configure_nutanix_credentials.py", connected_branch)

    def test_handoff_is_consistent_and_stops_safely(self):
        prompt = read_prompt()
        readme = (ROOT / "README.md").read_text()
        self.assertIn("configure_nutanix_credentials.py", prompt)
        self.assertIn("separate local terminal", prompt.lower())
        self.assertNotIn("currently blocked at credential entry", prompt.lower())
        self.assertIn(prompt, readme)
        self.assertIn("plaintext but restricted", readme.lower())

    def test_readme_prompt_matches_canonical_prompt_exactly(self):
        readme = (ROOT / "README.md").read_text()
        matches = PROMPT_RE.findall(readme)
        self.assertEqual(len(matches), 1, "README must embed exactly one copyable prompt")
        self.assertEqual(matches[0], read_prompt())

    def test_readme_links_router_skills_and_connection_workflow(self):
        readme = (ROOT / "README.md").read_text()
        for target in (
            "ENTRY.md",
            "setup-instructions/setup.md",
            "skills/nutanix-connect-prism-central/SKILL.md",
            "skills/nutanix-readonly-inventory/SKILL.md",
            "skills/nutanix-automation-method-selection/SKILL.md",
        ):
            with self.subTest(target=target):
                self.assertIn(target, readme)
                self.assertTrue((ROOT / target).is_file())
        low = readme.lower()
        self.assertIn("if no live connection", low)
        self.assertIn("technical preview", low)

    def test_open_code_handoff_requires_restart_and_live_session_check(self):
        readme = (ROOT / "README.md").read_text().lower()
        prompt = (ROOT / "prompts/setup.md").read_text().lower()
        skill = (ROOT / "skills/nutanix-connect-prism-central/SKILL.md").read_text().lower()
        self.assertIn("fully quit and relaunch opencode", readme)
        self.assertIn("fully quit and relaunch opencode", prompt)
        self.assertIn("fully quit and relaunch opencode", skill)
        self.assertIn("mcp view", readme)
        self.assertIn("if tools are visible", prompt)
        self.assertIn("cli config listing alone", prompt.lower())
        self.assertIn("cli config listing alone", readme.lower())
        self.assertIn("cli config listing alone", skill)


if __name__ == "__main__":
    unittest.main()
