import importlib.util
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "configure_nutanix_credentials.py"
SPEC = importlib.util.spec_from_file_location("configure_nutanix_credentials", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load credential helper")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def fake_process(returncode, stdout="", stderr="", command_log=None):
    class FakeProcess:
        def __init__(self, args, **kwargs):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr
            if command_log is not None:
                command_log.append((args, kwargs))
        def communicate(self, timeout=None):
            return self.stdout, self.stderr
    return FakeProcess


class PrivateCredentialBootstrapTests(unittest.TestCase):
    def test_precreate_private_env_without_overwriting_existing_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / ".env"
            module.create_private_env(target)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            self.assertEqual(target.read_text(), "")
            with self.assertRaises(FileExistsError):
                module.create_private_env(target)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_secret_input_validation_rejects_line_breaks(self):
        with self.assertRaises(ValueError):
            module.validate_secret("unsafe\nPC_API_KEY=attacker-value")
        with self.assertRaises(ValueError):
            module.validate_secret("unsafe\x00value")

    def test_upstream_init_sanitizes_output_and_keeps_secret_ephemeral(self):
        secret = "not-a-real-password"
        command_log = []
        fake = fake_process(0, f"PC_PASSWORD={secret}", "", command_log)
        with tempfile.TemporaryDirectory() as temporary, patch.object(module.subprocess, "Popen", fake):
            server_dir = Path(temporary)
            (server_dir / ".venv/bin").mkdir(parents=True)
            exe = server_dir / ".venv/bin/nutanix-mcp"
            exe.touch()
            result = module._run_init(server_dir, "pc.example", "reader", secret, "password")
            self.assertIn("completed", result.lower())
            args, kwargs = command_log[0]
            self.assertEqual(args, [str(exe), "init"])
            self.assertEqual(kwargs["env"]["PC_USERNAME"], "reader")
            self.assertEqual(kwargs["env"]["PC_PASSWORD"], secret)
            self.assertNotIn("PC_API_KEY", kwargs["env"])
            self.assertEqual(kwargs["env"]["READ_ONLY_MODE"], "true")
            self.assertEqual(stat.S_IMODE((server_dir / ".env").stat().st_mode), 0o600)
            self.assertNotIn(secret, result)

    def test_api_key_entry_uses_only_api_key_variable(self):
        secret = "not-a-real-key"
        command_log = []
        fake = fake_process(0, command_log=command_log)
        with tempfile.TemporaryDirectory() as temporary, patch.object(module.subprocess, "Popen", fake):
            server_dir = Path(temporary)
            (server_dir / ".venv/bin").mkdir(parents=True)
            module._run_init(server_dir, "pc.example", "", secret, "api_key")
            env = command_log[0][1]["env"]
            self.assertEqual(env["PC_API_KEY"], secret)
            self.assertNotIn("PC_PASSWORD", env)

    def test_child_env_drops_inherited_target_and_safety_overrides(self):
        inherited = {"PC_HOST": "wrong", "PC_PORT": "8888", "PC_INSECURE": "true", "READ_ONLY_MODE": "false", "PC_API_KEY": "old"}
        command_log = []
        fake = fake_process(0, command_log=command_log)
        with tempfile.TemporaryDirectory() as temporary, patch.dict(module.os.environ, inherited, clear=True), patch.object(module.subprocess, "Popen", fake):
            server_dir = Path(temporary)
            (server_dir / ".venv/bin").mkdir(parents=True)
            module._run_init(server_dir, "pc.example", "reader", "pw", "password")
            env = command_log[0][1]["env"]
            self.assertEqual(env["PC_HOST"], "pc.example")
            self.assertEqual(env["PC_PORT"], "9440")
            self.assertEqual(env["PC_INSECURE"], "false")
            self.assertEqual(env["READ_ONLY_MODE"], "true")
            self.assertNotIn("PC_API_KEY", env)

    def test_interactive_entry_refuses_non_tty(self):
        with patch.object(module.sys, "argv", [str(MODULE_PATH), "/unused"]), patch.object(module.sys.stdin, "isatty", return_value=False), patch("builtins.print") as printed:
            result = module.main()
        self.assertEqual(result, 1)
        self.assertIn("local terminal", str(printed.call_args))

    def test_interrupted_prompt_exits_cleanly_without_credential_file(self):
        for interruption in (EOFError(), KeyboardInterrupt()):
            with tempfile.TemporaryDirectory() as temporary:
                server_dir = Path(temporary)
                (server_dir / ".venv/bin").mkdir(parents=True)
                (server_dir / ".venv/bin/nutanix-mcp").touch()
                with patch.object(module.sys, "argv", [str(MODULE_PATH), str(server_dir)]), \
                     patch.object(module.sys.stdin, "isatty", return_value=True), \
                     patch("builtins.input", side_effect=interruption), \
                     patch("builtins.print") as printed, \
                     patch.object(module.subprocess, "Popen") as run:
                    result = module.main()
                self.assertEqual(result, 1)
                self.assertFalse(run.called)
                self.assertNotIn("Traceback", str(printed.call_args))
                self.assertFalse((server_dir / ".env").exists())

    def test_failed_init_does_not_echo_upstream_output(self):
        secret = "not-a-real-password"
        fake = fake_process(1, secret, secret)
        with tempfile.TemporaryDirectory() as temporary, patch.object(module.subprocess, "Popen", fake):
            server_dir = Path(temporary)
            (server_dir / ".venv/bin").mkdir(parents=True)
            (server_dir / ".venv/bin/nutanix-mcp").touch()
            with self.assertRaises(module.SetupError) as error:
                module._run_init(server_dir, "pc.example", "reader", secret, "password")
            self.assertNotIn(secret, str(error.exception))


if __name__ == "__main__":
    unittest.main()
