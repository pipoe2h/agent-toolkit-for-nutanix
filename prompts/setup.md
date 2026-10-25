# Connect your agent to Nutanix

Copy this prompt into your existing AI coding agent. It will inspect its environment and report the current blocker; this initial release does not yet complete setup.

```text
Connect this agent to my Nutanix environment by following:
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/main/setup-instructions/setup.md

Do the setup for me. Ask only for details you cannot discover yourself, explain local changes before requesting approval, and never ask me to paste secrets into chat. Keep the connection read-only and verify it with one small inventory query. Stop after that verification.

Important: this workflow is currently blocked at credential entry. Do not ask me to create or edit `.env`, do not write credentials to a file, do not run `nutanix-mcp init` with credentials, and do not contact Prism Central with credentials. Upstream `init` can persist secrets to `.env` without enforcing restrictive file permissions. Stop and report this blocker unless a safe private credential-entry method has been independently verified for the exact upstream revision.
```

The detailed instructions are in [`setup-instructions/setup.md`](../setup-instructions/setup.md). The current workflow is explicitly blocked at the credential step: upstream's checked revision lacks a verified private-entry mechanism and `init` writes credentials to `.env`. The agent must stop rather than ask you to manage a credentials file or pretend the connection is complete. These instructions take effect after the repository changes are published; verify the public workflow URL is up to date before distributing the prompt.
