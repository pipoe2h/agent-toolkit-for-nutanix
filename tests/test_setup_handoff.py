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
        self.assertIn("do not contact prism central with credentials", prompt.lower())
        self.assertIn(prompt, readme)
        self.assertIn("handoff below is currently blocked at credential entry", readme.lower())

    def test_setup_guide_blocks_unsafe_credential_flow(self):
        setup = (ROOT / "setup-instructions/setup.md").read_text().lower()
        self.assertNotIn("phase 2b", setup)
        self.assertIn("do not have the agent write secrets", setup)
        self.assertIn("do not configure an incomplete mcp entry", setup)
        self.assertIn("read_only_mode=true", setup)
        self.assertIn("do not use a custom port", setup)


if __name__ == "__main__":
    unittest.main()
