# VM inventory query contract

## Illustrative case: 61 total, 50 on page 0

The numbers below illustrate the reported situation; they are not a product guarantee. If a response says `totalAvailableResults: 61` and returns 50 rows with truncation/next-page metadata, it is only the first page. Report 50/61 as partial until all pages have been collected and reconciled.

## One-pass, low-context flow

1. Inspect the actual list operation schema and its response shape. Confirm safe/read-only permissions.
2. Run one bounded probe using `$limit=1` and a small `$select`; verify both took effect and inspect metadata/links.
3. Fetch page 0 with `$select=name,powerState,extId,numSockets,numCoresPerSocket,memorySizeBytes,nics`, a supported maximum `$limit`, optional scoped `$filter`, and stable `$orderby=name asc` if the schema supports it.
4. Transform each page into the requested output fields as it is fetched; retain only rows/IDs and pagination metadata needed for reconciliation. Follow each `metadata.links` item where `rel=next`, or use a verified `$page` sequence if links are unavailable.
5. Stop at no next link (or the verified final page), detect repeated page signatures and duplicate `extId`s, and reconcile unique collected rows to `metadata.totalAvailableResults`.
6. Report rows, projection and explicit coverage status. Do not re-fetch the entire payload just to reshape fields already in memory.

Expected happy-path call count: one schema inspection, one single-record passthrough probe, then one list call per page. With 61 results and a confirmed page size of 50, that is one probe plus two data-page calls (three list calls total), not repeated full-list retrievals for projection or guesses at ignored parameters. Schema inspection may itself be a tool call. A wrapper may expose pagination metadata differently; verify per client and report if the expected surface is unavailable.

## Minimal VM projection

For a compact inventory table, request the smallest fields that answer the user's need. A suggested richer inventory projection is:

```text
$select=name,powerState,extId,numSockets,numCoresPerSocket,memorySizeBytes,nics
```

Confirm exact field names and nested projection syntax in the operation schema. `nics` can be large; omit it if not needed. Never request fields merely because they exist.

## OData examples

Use only after confirming the operation accepts and the client forwards these options:

```text
$filter=powerState eq 'OFF'
$filter=startswith(name,'nkp-')
$orderby=name asc
$select=name,powerState,extId
$limit=50
$page=0
```

OData string literals use single quotes; escape embedded quotes according to the operation's OData/version rules. Do not assume a filter function or field is supported. The server can enforce a maximum page size; a larger requested `$limit` may be clamped or rejected. Check actual row count and metadata.

## Illustrative metadata and link handling

```json
{
  "metadata": {
    "totalAvailableResults": 61,
    "isTruncated": true,
    "links": [
      {"rel": "next", "href": "<opaque page 1 link>"},
      {"rel": "last", "href": "<opaque final-page link>"}
    ]
  }
}
```

This is an illustrative shape only. Follow the actual returned `rel=next` link; treat it as opaque and do not reconstruct/modify its URL. Request the next page until the `next` link is absent. A `last` link may be useful evidence but does not authorize skipping intermediate pages. If links are absent or hidden by the client, inspect the schema and verify `$page` one page at a time. Do not issue speculative parameter variants.

## Example outputs

**Complete:**

```text
Target: Prism Central (authorized environment)
Timestamp: 2026-10-26T14:30:00Z
Operation: nutanix_vmm_execute / ahv_listVms
Filter: none
Projection: name, powerState, extId
Returned/total: 61/61 unique VMs
Coverage: COMPLETE — all pages retrieved; no duplicate pages; count reconciled to metadata.totalAvailableResults.
```

**Degraded:**

```text
Target: Prism Central (authorized environment)
Timestamp: 2026-10-26T14:30:00Z
Operation: nutanix_vmm_execute / ahv_listVms
Filter: none
Projection: name, powerState, extId
Returned/total: 50/61 VMs
Reason: this client's wrapper did not honor the tested $page option and exposed no usable rel=next link.
Coverage: PARTIAL — 50/61 returned. No completeness claim.
```

Do not copy the illustrative timestamp or operation as real evidence; use observed values for the current query.

## Shape during fetch, not in a second pass

As each response arrives, map only required fields into the compact result rows and record stable IDs plus pagination metadata. Preserve the information needed to detect duplicates and reconcile totals, but discard unrelated raw payload from the working context. Never make a second full inventory call solely to project, format, or summarize results already fetched.
