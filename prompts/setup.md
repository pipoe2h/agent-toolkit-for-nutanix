# Connect your agent to Nutanix

Copy this prompt into your existing AI coding agent. It will inspect its environment and guide you through the setup, including a private credential-entry step. It does not query Prism Central automatically yet.

```text
Connect this agent to my Nutanix environment by following:
https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/b40d617/setup-instructions/setup.md

Do not ask me to enter a credential in this chat. When credential entry is needed, give me the exact command to run in a separate local terminal using `scripts/configure_nutanix_credentials.py`; make sure the helper uses hidden input and never prints credentials. Do not claim setup is blocked without explaining what I should do next. Keep the connection read-only and verify it with one small inventory query. Stop after that verification.

After the local helper exits successfully, return to the agent and say `done`; it should continue with client registration, handshake and one read-only query.

Important: the workflow includes a local helper for upstream `.env` behavior. Explain that credentials remain plaintext in an owner-only `.env` file and get approval before asking me to run it. If the helper is not available or verified, stop and give me a clear next step; do not ask me to create `.env` or run `nutanix-mcp init` myself.
```

The detailed instructions are in [`setup-instructions/setup.md`](../setup-instructions/setup.md). The agent requests approval before running the local credential helper, explains that `.env` is plaintext-at-rest despite mode `0600`, then guides the user through hidden local-terminal entry. Never paste credentials or terminal output into chat.
