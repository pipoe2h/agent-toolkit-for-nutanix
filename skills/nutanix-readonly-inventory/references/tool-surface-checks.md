# Per-client MCP query-surface checks

Query-parameter support is a property of the exposed client/wrapper operation surface, not something to infer from a V4 API specification or another client. Run these checks only against an authorized, read-only operation.

## Bounded `$limit=1` probe

1. Inspect the exact operation schema and identify how query options and request body are represented. Record the client and wrapper versions.
2. Submit one request with `$limit=1` and a small `$select` (for example `name,extId`) using only the documented input shape.
3. Assert from returned evidence that the option took effect: at most one data row is returned; the row contains only the requested fields (subject to any documented mandatory fields); and metadata/links are consistent with a one-row page and remaining data when a known total exceeds one.
4. Compare with a baseline request if safe and necessary: check the first-row identity, count, projected fields, `totalAvailableResults`, `isTruncated`, and next/last links. One matching observation alone may be inconclusive if the baseline naturally has one row.
5. Test pagination only after schema inspection; use a returned `rel=next` link or a documented `$page` field. Do not guess names or issue loops of speculative probes.

A claimed maximum of one row is not established solely because the client accepted the call. Inspect actual row count and metadata. Conversely, a required singleton response can be valid even if it returns zero rows; report the observed evidence and do not overstate the probe.

## Ignored option vs validation error

| Evidence | Interpretation | Action |
|---|---|---|
| Call succeeds, but `$limit=1` still returns the same first page/count as baseline; `$select` has no effect; pagination links/metadata are unchanged | The parameter may be silently ignored, or the compared requests may not distinguish behavior. | Recheck the schema and perform at most a controlled, bounded comparison that can distinguish the option. If still inconclusive, mark support unverified; do not guess. |
| Tool/schema returns an explicit invalid-argument, unknown-field, or validation error naming the option/value | The option is rejected in this operation/client surface or the syntax is invalid. | Correct only from schema/documentation evidence. If unsupported, record that limitation. |
| Response data is reduced and metadata/links change consistently with the requested limit/projection | Evidence that the option is honored for this tested operation/version. | Record the exact tested surface; do not generalize to other operations or clients. |

Same first row is not enough to prove ignoring: legitimate order may make the first row identical. Compare count, selected fields, totals/truncation, and links together. If the evidence remains ambiguous, report `unverified` rather than declaring support or non-support.

## Capability matrix

Fill in from observed tests for each deployed environment; avoid secrets and sensitive endpoint details.

| Client | Wrapper/server version | Query params honored (`$select`, `$filter`, `$limit`, `$page`) | Pagination method (`rel=next`, `$page`, other verified) | Notes / evidence |
|---|---|---|---|---|
|  |  |  |  |  |

## Boundary

A tool-surface limitation is reported, not bypassed with a direct SDK/API script, shell request, alternate credential, or another tool. If the user later requests custom automation, route it to the existing human-reviewed artifact lane; do not execute it as a workaround for this inventory query. If query controls or pagination are unavailable, report returned/known total and explicitly mark coverage partial or unverified.
