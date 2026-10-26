import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "configure_nutanix_credentials.py"
SPEC = importlib.util.spec_from_file_location("configure_nutanix_credentials", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load credential helper")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class InitProgressTests(unittest.TestCase):
    def test_init_emits_safe_stage_progress_and_elapsed_time(self):
        lines = []
        class FakeProcess:
            def __init__(self, *args, **kwargs):
                self.returncode = 0
                self.stdout = "PC_PASSWORD=FAKE-SECRET\n"
                self.stderr = "raw stderr FAKE-SECRET\n"
            def communicate(self, timeout=None):
                return (self.stdout, self.stderr)

        current = [100.0]
        def monotonic():
            current[0] += 11.2
            return current[0]
        with tempfile.TemporaryDirectory() as temporary, \
             patch.object(module.subprocess, "Popen", FakeProcess), \
             patch.object(module.time, "monotonic", side_effect=monotonic), \
             patch.object(module, "PROGRESS_INTERVAL_SECONDS", 0), \
             patch.object(module, "_progress", side_effect=lines.append):
            result = module._run_init(Path(temporary), "pc.example", "reader", "FAKE-SECRET", "password")
        self.assertIn("completed", result.lower())
        self.assertTrue(any("Starting Prism Central check" in line for line in lines))
        self.assertTrue(any("Downloading API definitions" in line for line in lines))
        self.assertTrue(any("s elapsed" in line for line in lines))
        self.assertTrue(any("completed in" in line.lower() for line in lines))
        self.assertTrue(all("FAKE-SECRET" not in line for line in lines))

    def test_init_error_progress_does_not_expose_upstream_output(self):
        lines = []
        class FakeProcess:
            def __init__(self, *args, **kwargs):
                self.returncode = 1
                self.stdout = "API_KEY=FAKE-SECRET\n"
                self.stderr = "fake traceback FAKE-SECRET\n"
            def communicate(self, timeout=None):
                return (self.stdout, self.stderr)

        with tempfile.TemporaryDirectory() as temporary, \
             patch.object(module.subprocess, "Popen", FakeProcess), \
             patch.object(module, "_progress", side_effect=lines.append):
            with self.assertRaises(module.SetupError) as error:
                module._run_init(Path(temporary), "pc.example", "reader", "FAKE-SECRET", "password")
        self.assertNotIn("FAKE-SECRET", str(error.exception))
        self.assertTrue(any("Initialization failed" in line for line in lines))
        self.assertTrue(all("fake traceback" not in line.lower() for line in lines))


if __name__ == "__main__":
    unittest.main()
