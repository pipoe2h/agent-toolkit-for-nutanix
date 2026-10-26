# Roadmap: next operational skills

Status: proposal only. Nothing in this document asserts a verified Nutanix operation name, request or response schema, query-option behavior, or RBAC permission requirement. Those details are **not verified** here and must not be inferred from this file.

## What exists today

`skills/nutanix-readonly-inventory/SKILL.md` is the only operational skill implemented. It is deliberately written against a generic read-only list/inventory contract — schema inspection, bounded passthrough probes, pagination, and reconciliation — instead of a catalog of named operations, so it does not depend on any particular operation being present.

The other two skills are not operational skills: `skills/nutanix-connect-prism-central/SKILL.md` supplies connection setup and discovery, and `skills/nutanix-automation-method-selection/SKILL.md` covers tasks MCP does not expose. No mutation skill exists, and writes are out of scope for the current read-only posture.

## Category A — writable now, without an unverified operation claim

A skill belongs in Category A only if its text can be written without naming a specific operation, schema field, or permission requirement. The only capability this repository currently treats as confirmed is the generic read-only inventory contract that `nutanix-readonly-inventory` already implements.

- Pending Category A work: none. Every remaining domain below would require naming operations or schemas that have not been observed against a live MCP catalog, so none of them qualifies yet.

## Category B — candidate domains (operations, schemas, and permissions not verified)

These are candidates only. The table records intent and open questions, not capability. No operation name, schema, query option, or permission requirement is asserted as verified.

| Candidate domain | Intended scope | Why it is not writable yet |
|---|---|---|
| VM lifecycle | Read-only discovery first. Any mutation is explicitly deferred behind separate user approval and is out of scope for the current read-only posture. | The operations that expose VM state, and their schemas and permissions, have not been observed in a live catalog. |
| Cluster and host health and capacity | Read-only reporting of cluster and host state and capacity signals. | No live catalog observation; the shape of health and capacity data is unknown. |
| Network and subnet inventory | Read-only inventory of networks and subnets, extending the existing inventory contract. | Whether the relevant list operations are exposed, and with which query options, is unverified. |
| Alert and event triage | Read-only listing and triage of alerts and events. | Alert and event operations, their schemas, and their required permissions are unverified, and triage semantics (severity, acknowledgement) are unknown. |

## Evidence required before writing any Category B skill

1. A live MCP session against an authorized Prism Central, with the discovered operation list captured along with the client/wrapper version, target, and timestamp.
2. The specific operation's request and response schema as that session reports it, including which query options are honored, observed with a bounded single-record probe.
3. The RBAC permission that operation requires, confirmed read-only, together with the least-privilege identity used for the observation.
4. A recorded run in the existing validation-notes format (`docs/validation/readonly-inventory.md`) showing observed evidence rather than inference from Nutanix API documentation or from another environment.

Only then is the skill authored. Mutations stay deferred: they would need separate approval gating that does not exist in this toolkit yet. Without that evidence a candidate domain stays in Category B. Do not promote a domain by naming an operation from memory, from documentation, or from a different environment.
