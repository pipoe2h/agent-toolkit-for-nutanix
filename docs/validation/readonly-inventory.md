# Read-only inventory validation notes

## Scenario

Validate that an authorized MCP client can execute a bounded, read-only resource inventory query, honor the tested field projection and page-size options, traverse every exposed page, and report reconciled coverage without fetching the full unfiltered raw payload repeatedly.

## Prerequisites

- An existing MCP connection to the intended customer-managed Prism Central.
- A dedicated low-privilege identity authorized only for the read operation being validated; TLS certificate verification enabled.
- The operation schema and client/wrapper version available for inspection.
- No writes, credential changes, direct SDK/API helper, or fallback tool use as part of this scenario.

## Procedure and expected evidence

1. Record client/wrapper version and target Prism Central in a safe, non-secret form. Inspect the list-operation schema and confirm it is read-only.
2. Run one `$limit=1` probe with minimal `$select`; capture row count, projected fields, totals/truncation, and pagination metadata. Record whether each option was actually honored.
3. Fetch only required fields at the largest confirmed permitted page size. Apply an optional supported scope filter. Transform each page during fetch, recording stable IDs and metadata rather than retaining/displaying the full raw response.
4. Follow `metadata.links` where `rel=next`, or a verified `$page` path when links are unavailable. Do not guess parameters or issue speculative variants.
5. Reconcile unique collected records against `metadata.totalAvailableResults`, and check duplicate IDs/pages, `isTruncated`, remaining links, and failed pages.
6. Report operation, target, timestamp, filters, projection, returned/total counts, call count, and `COMPLETE`, `PARTIAL`, or `UNVERIFIED` coverage with evidence.

For the illustrative total of 61 with a confirmed page size of 50, expected data calls are two pages plus one single-record passthrough probe; include a schema call if schema inspection is a separate tool call. Evidence should show 61 unique rows collected, no repeated page, no next link remaining, and a reconciled total before declaring complete. Numbers and call count depend on observed metadata and actual page size; do not promise them in another environment.

## Failure modes

- A parameter is rejected by schema/validation: correct it only from schema evidence; otherwise mark the capability unavailable.
- A parameter appears silently ignored: perform a bounded, distinguishable comparison; if still inconclusive, mark unverified.
- Pagination is unavailable, a page fails, truncation remains, or counts differ: stop and report partial coverage with the reason and counts. Do not bypass the limitation with another tool or credential.
- Network/TLS, authentication/authorization, or service errors: classify and stop according to `skills/nutanix-automation-method-selection/SKILL.md`; do not present them as pagination gaps.

## Verification limits

This document specifies a reusable test scenario. It does not assert that any specific Nutanix operation, MCP server release, or client forwards a given query option. Validate the actual operation schema and client surface for each environment.
