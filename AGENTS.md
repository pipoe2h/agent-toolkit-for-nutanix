# Nutanix guidance

Where these rules conflict with the project's own instructions, the project's
instructions take precedence.

- Before starting a Nutanix task, check whether a Nutanix skill is available and load
  it in preference to general knowledge.
- Never invent product surface. If a URL path, field label, credential step, or API
  path cannot be traced to a Nutanix procedure page, put it in a validation gate
  rather than stating it as fact.
- Copy gateway prefixes, endpoint names, and API paths character-for-character.
- State the Nutanix Enterprise AI release you are working against. The Agent Gateway
  surface changes between releases.
- Treat "documented" and "verified on this deployment" as different states, and say
  which one you are reporting.
- Do not provision or modify infrastructure without explicit confirmation, and prefer
  infrastructure-as-code over direct CLI commands.
- Route agent inference traffic through the Agent Gateway rather than letting each
  client hold provider credentials directly.

## Secret safety

- Never print, echo, or commit an API client key, MCP client key, or TLS private key.
- API client keys are shown once at creation. If a key is lost, it must be regenerated;
  say so rather than trying to recover it.
