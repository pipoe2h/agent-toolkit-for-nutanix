---
name: nutanix-readonly-inventory
description: "Run complete, least-privilege read-only inventory queries against Nutanix Prism Central through an MCP client. Covers schema inspection, parameter passthrough probes, projection, filtering, pagination, reconciliation, and partial-result reporting. Use when listing VMs, clusters, hosts, subnets, alerts, or other resources."
license: Apache-2.0
metadata:
  version: "0.1.0"
---

# Read-only Nutanix inventory

Use this workflow to produce low-context inventory results without overstating coverage. Query parameters and pagination depend on the operation and the MCP client/wrapper surface; verify them per client rather than assuming they pass through.

## When to use

- List or report VMs, clusters, hosts, subnets, alerts, or other Prism Central resources.
- Produce a scoped inventory that must be complete or explicitly marked partial.

## Non-goals and boundaries

- Do not make writes, change configuration, or mutate infrastructure.
- Do not handle credentials or request secrets in prompts, parameters, or logs.
- Keep the target inventory query read-only; if the operation is not exposed by MCP, do not switch tools during the query. A later custom automation request belongs in the human-reviewed artifact lane as described in the method-selection skill.
- Do not claim completeness until collected results reconcile with the server-reported total (or another documented authoritative total).
- This skill does not promise that every MCP client forwards query options or exposes all pagination metadata.

## Query contract

1. **Inspect the operation schema.** Use `getOperationSchema` or the client's equivalent. Confirm accepted request-body fields, query options, response envelope, metadata, and permissions. Do not infer parameter support from an API specification alone.
2. **Probe passthrough on one record.** Request `$limit=1` and a small `$select`; inspect the actual result and metadata to verify each option took effect. If the wrapper exposes only `operation` and `request_body`, test how the schema represents options. See `references/tool-surface-checks.md`.
3. **Fetch a minimal, scoped page.** Request only required fields with `$select`, the largest page size confirmed safe and supported, and a narrow `$filter` where appropriate. Respect server-side maxima; never assume a requested size was honored.
4. **Paginate using observed support.** Follow `metadata.links` entries with `rel=next` when provided; otherwise use a verified `$page` mechanism. Continue until no next page remains or the authoritative total is reached. Never guess link templates or page semantics.
5. **Reconcile completeness.** Compare unique collected records with `metadata.totalAvailableResults`; check truncation flags, next/last links, and duplicate pages. The equality check is necessary but also verify there are no repeated pages/IDs. If total metadata is absent, explain what coverage can and cannot be established.
6. **Report projection and coverage.** Name the fields returned and include the required coverage line. If any option was ignored, metadata is missing, a page failed, or counts do not reconcile, mark the result partial and state why.

## Query parameters

| Option | Use | Notes |
|---|---|---|
| `$select` | Return only fields needed for the report. | Verify forwarding and field names per operation/client. Nested field syntax may vary. |
| `$filter` | Restrict the server-side result set. | OData-style expressions such as `powerState eq 'OFF'` or `startswith(name,'nkp-')`; verify supported fields/functions and quoting. |
| `$orderby` | Request stable ordering, e.g. `name asc`. | Verify support and tie-break behavior; stable order helps compare pages but does not replace duplicate detection. |
| `$limit` | Request a page size, preferably the largest confirmed permitted. | Server-side maxima may clamp or reject it. Probe that the response changes as expected. |
| `$page` | Request a page when the surface supports numbered pages. | Page base and interaction with `$limit` vary; verify against schema/response. Prefer `metadata.links` when returned. |

These are query conventions, not guarantees about the MCP tool surface. Do not assume query-string options pass through unless observed for the specific client, wrapper, operation, and version.

## Pagination and completeness

Inspect the actual response envelope. A common shape is:

```json
{
  "data": [{"extId": "...", "name": "..."}],
  "metadata": {
    "totalAvailableResults": 61,
    "isTruncated": true,
    "links": [
      {"rel": "next", "href": "<opaque next-page link>"},
      {"rel": "last", "href": "<opaque last-page link>"}
    ]
  }
}
```

This is illustrative, not a promise about every operation's exact envelope. Follow the returned `rel=next` link exactly when the tool supports it; stop when it is absent. A `rel=last` link can help understand the remaining range but does not replace following pages and reconciling counts. If links are not exposed, use `$page` only after confirming the operation schema and one-record probe show it is honored. Treat `isTruncated: true`, a remaining next link, failed page, duplicate page, or `len(unique collected) != totalAvailableResults` as incomplete. Deduplicate using a stable resource identifier such as `extId`, and separately detect an identical page repeated under a new request. Never infer completeness from one page or from an apparent short final page alone.

## Tool-surface probe

Use a bounded `$limit=1` request and minimal projection. Compare returned row count, first-row identity, projected fields, total metadata, and pagination links against a baseline request. A value that is unchanged may mean the client ignored the option; an explicit schema/validation error means the option was rejected. Neither outcome justifies guessing alternate parameter names or changing tools. Record the capability per environment and mark inventories partial if required controls cannot be honored. Detailed checks: `references/tool-surface-checks.md`.

## Failure classification

| Failure | Next action |
|---|---|
| Network, DNS, timeout, or TLS | Diagnose the connection; do not switch tools to bypass it. |
| Authentication or authorization denied | Stop and review identity/RBAC with the authorized operator; do not try another credential or tool to evade the denial. |
| Invalid request or schema mismatch | Inspect the operation schema and correct the request. |
| Service error / Prism Central unavailable | Report the service failure and stop; an alternate path may hit the same fault. |
| Operation genuinely absent from the discovered MCP catalog | Evaluate Ansible, SDK/API, or IaC coverage for the exact deployment/version. |

Keep this classification aligned with `skills/nutanix-automation-method-selection/SKILL.md`.

## Reporting format

Always include:

- Target Prism Central (safe display label/endpoint, never credentials) and query timestamp with timezone.
- MCP operation used and resource type.
- Filters applied and projection fields returned.
- Returned unique count / authoritative total count.
- Required coverage line, for example: `Coverage: COMPLETE — 61/61 resources retrieved; pages reconciled.` or `Coverage: PARTIAL — 50/61 resources retrieved; stopped because the client did not honor $page. No completeness claim.`

If the total is unavailable, say `Coverage: UNVERIFIED` and explain why. Do not bury partial coverage in a footnote.

## Safety

- Use read-only operations, TLS verification, and least-privilege Prism Central RBAC.
- Never include secrets in prompts, tool arguments, command lines, examples, or logs.
- Respect authorization and stop on denial. Do not use another tool to get around a failure.
- Avoid fetching or displaying unneeded raw payloads; project/transform while fetching each page.

## Validation gates

- Operation schema inspected and operation permission confirmed read-only.
- `$limit` and `$select` behavior verified per client; filters/order verified when used.
- Pagination method observed in schema/metadata, not guessed.
- Every page accounted for; duplicates checked; collected unique count reconciled to total.
- Output contains projection, operation, target, timestamp, filters, counts, and explicit coverage status.
- If any gate fails, report degraded/partial coverage and the exact reason; do not claim success as a complete list.

## References

- `references/query-contract.md` — worked VM inventory, OData examples, pagination, and reporting examples.
- `references/tool-surface-checks.md` — bounded passthrough probes and per-client capability matrix.
