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


if __name__ == "__main__":
    unittest.main()
