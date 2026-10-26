from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SetupHandoffTests(unittest.TestCase):
    def test_handoff_is_consistent_and_stops_safely(self):
        prompt_text = (ROOT / "prompts/setup.md").read_text()
        match = re.search(r"```text\n(.*?)\n```", prompt_text, re.S)
        if match is None:
            self.fail("Canonical setup prompt must exist")
        prompt = match.group(1)
        readme = (ROOT / "README.md").read_text()
        self.assertIn("configure_nutanix_credentials.py", prompt)
        self.assertIn("separate local terminal", prompt.lower())
        self.assertNotIn("currently blocked at credential entry", prompt.lower())
        self.assertIn(prompt, readme)
        self.assertIn("plaintext but restricted", readme.lower())
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
