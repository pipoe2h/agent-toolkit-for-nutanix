import os
from pathlib import Path
import stat
import subprocess
import sys


class SetupError(Exception):
    """A safe-to-display setup failure."""


def create_private_env(path: Path) -> None:
    """Create an empty credential file exclusively with owner-only permissions."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if os.name == "nt":
        raise SetupError("This credential helper currently supports POSIX file permissions only. Use a trusted POSIX terminal host or follow the supported Windows setup instructions.")
    fd = os.open(path, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        mode = stat.S_IMODE(os.fstat(fd).st_mode)
        if mode != 0o600:
            raise SetupError("Could not enforce private permissions on credential file")
    finally:
        os.close(fd)


def validate_secret(value: str) -> None:
    if not value or "\n" in value or "\r" in value or "\x00" in value:
        raise ValueError("Credential must be non-empty and contain no line breaks")


def _run_init(server_dir: Path, host: str, username: str, secret: str, auth_method: str, retry: bool = False) -> str:
    """Run upstream init with transient credentials and a pre-protected .env."""
    if auth_method not in {"password", "api_key"}:
        raise SetupError("Choose either password or API key authentication.")
    validate_secret(secret)
    env_path = server_dir / ".env"
    if retry:
        try:
            mode = stat.S_IMODE(env_path.stat().st_mode)
        except FileNotFoundError:
            raise SetupError("No saved credential file exists to retry. Run the helper without --retry.") from None
        if mode != 0o600:
            raise SetupError("Saved credential file permissions are unsafe. Do not retry; ask the agent for recovery steps.")
    else:
        try:
            if env_path.exists():
                raise SetupError("A .env already exists. It was not changed. Ask the agent to review it safely before continuing.")
            create_private_env(env_path)
        except FileExistsError:
            raise SetupError("A .env already exists. It was not changed. Ask the agent to review it safely before continuing.") from None
        except OSError:
            raise SetupError("Could not safely create the credential file. No credentials were sent. Ask the agent for recovery steps.") from None
    env = os.environ.copy()
    for key in (
        "PC_HOST", "PC_PORT", "PC_USERNAME", "PC_PASSWORD", "PC_API_KEY",
        "PC_INSECURE", "READ_ONLY_MODE",
    ):
        env.pop(key, None)
    env.update({
        "PC_HOST": host,
        "PC_PORT": "9440",
        "PC_INSECURE": "false",
        "READ_ONLY_MODE": "true",
    })
    if auth_method == "password":
        env.update({"PC_USERNAME": username, "PC_PASSWORD": secret})
    else:
        env["PC_API_KEY"] = secret
    try:
        result = subprocess.run(
            [str(server_dir / ".venv/bin/nutanix-mcp"), "init"],
            cwd=server_dir,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        env_path.unlink(missing_ok=True)
        raise SetupError("Initialization could not complete. Check the local installation and network, then retry.") from None
    mode = stat.S_IMODE(env_path.stat().st_mode)
    if mode != 0o600:
        raise SetupError("Initialization created a credential file with unsafe permissions. Stop; the file remains in place for safe manual cleanup.")
    if result.returncode != 0:
        raise SetupError("Initialization failed. The private credential file is retained for retry. Check network reachability, TLS trust, and authorization; raw output is omitted to protect credentials.")
    return "Initialization completed. The credential file has owner-only permissions; TLS verification and read-only mode were explicitly enabled."


def discard_empty_credential_file(server_dir: Path) -> None:
    """Remove a pre-created credential file only when it holds no credentials."""
    env_path = server_dir / ".env"
    try:
        if env_path.is_file() and env_path.stat().st_size == 0:
            env_path.unlink()
    except OSError:
        pass


def main() -> int:
    if not sys.stdin.isatty():
        print("Credential entry requires a private interactive local terminal. Re-run this helper in a terminal; do not paste credentials into chat.")
        return 1
    if len(sys.argv) not in {2, 3} or (len(sys.argv) == 3 and sys.argv[2] != "--retry"):
        print("Usage: configure_nutanix_credentials.py <mcp-server-directory> [--retry]")
        return 2
    retry = len(sys.argv) == 3
    server_dir = Path(sys.argv[1]).expanduser().resolve()
    if not (server_dir / ".venv/bin/nutanix-mcp").is_file():
        print("The Nutanix MCP server is not installed at the selected location. Ask the agent to install it first.")
        return 2
    try:
        host = input("Prism Central hostname or IP (HTTPS port 9440): ").strip()
        if not host or any(ch in host for ch in ("\r", "\n", "\x00", "/", "@", "\\")):
            raise SetupError("Enter only a Prism Central hostname or IP address, without a scheme or path.")
        auth_method = input("Authentication method (password/api_key): ").strip().lower()
        if auth_method not in {"password", "api_key"}:
            raise SetupError("Choose password or api_key authentication.")
        username = input("Prism Central username: ").strip() if auth_method == "password" else ""
        if auth_method == "password" and not username:
            raise SetupError("A username is required for password authentication.")
        import getpass
        secret = getpass.getpass("Prism Central password (input hidden): " if auth_method == "password" else "Prism Central API key (input hidden): ")
        validate_secret(secret)
        message = _run_init(server_dir, host, username, secret, auth_method, retry=retry)
        print(message)
        return 0
    except (SetupError, ValueError) as exc:
        discard_empty_credential_file(server_dir)
        print(str(exc))
        return 1
    except (EOFError, KeyboardInterrupt):
        discard_empty_credential_file(server_dir)
        print("Input ended before a credential was entered. Nothing was sent and no credential file was written; re-run the command when ready.")
        return 1
    finally:
        secret = "" if "secret" in locals() else None


if __name__ == "__main__":
    raise SystemExit(main())
