---
name: nutanix-automation-method-selection
description: "Choose between Nutanix MCP operations, Ansible, V4 SDK/API code, and OpenTofu or Terraform for a customer environment. Covers operation-coverage gaps, method fit, version compatibility, least privilege, idempotency, and safe human-reviewed automation. Use when MCP does not expose a requested operation or a task needs repeatable Nutanix automation."
license: Apache-2.0
metadata:
  version: "0.1.0"
---

# Choose a Nutanix automation method

## When to use

- The agent cannot find an MCP operation for the requested task.
- The user wants a repeatable playbook, custom API integration, or declarative infrastructure workflow.
- The task has different implementations across MCP, Ansible, SDKs/API, and OpenTofu/Terraform.

## Do not treat this as automatic fallback

An MCP failure is not necessarily missing feature coverage. First classify it:

| Failure | Next action |
|---|---|
| Network, DNS, timeout, or TLS | Diagnose the connection; do not switch tools to bypass it. |
| Authentication or authorization denied | Stop and review identity/RBAC with the authorized operator; do not try another credential or tool to evade the denial. |
| Invalid request or schema mismatch | Inspect the operation schema and correct the request. |
| Service error / Prism Central unavailable | Report the service failure and stop; an alternate path may hit the same fault. |
| Operation genuinely absent from the discovered MCP catalog | Evaluate Ansible, SDK/API, or IaC coverage for the exact deployment/version. |
| Task requires repeatable desired-state reconciliation | Consider Ansible or OpenTofu/Terraform based on lifecycle and state needs, even if MCP has individual operations. |

## Method selection

1. **MCP:** Best for interactive discovery and narrowly scoped API operations, especially when tools are discovered from the target PC. Inspect the operation schema and permissions; start read-only.
2. **Ansible:** Best for procedural, repeatable orchestration and configuration across resources. Check the official `nutanix.ncp` collection version and its exact module support for the required operation and target PC/AOS versions.
3. **V4 SDK/API:** Best for custom application logic, reusable libraries, or operations needing precise API control. Confirm that the relevant API namespace/revision is GA and compatible with the target PC/AOS; Nutanix publishes v4 SDKs for Python, Go, Java, and JavaScript.
4. **OpenTofu/Terraform:** Best when desired-state lifecycle, planning, drift detection, and state tracking matter. Check the provider's resource/data-source coverage and compatibility. Do not choose it just because an operation can be expressed as a create call.

A method is only a candidate after verifying: exact task/operation coverage; target PC/AOS support; tool/provider/SDK release; required role/permissions; idempotency and retry behavior; and the expected state change.

## Safe workflow for an uncovered operation

1. Confirm the MCP failure is genuinely an operation coverage gap, not a connection or permissions problem.
2. Search official Nutanix documentation and the official Ansible collection/provider for the exact operation and version. Do not invent module names or parameters.
3. If several methods fit, explain tradeoffs and recommend one. Prefer idempotent, reviewable declarative automation when the task is repeatable.
4. In this prototype, generate an artifact only for **human review and execution**. Do not execute playbooks, SDK scripts, or `tofu/terraform apply`.
5. Show the artifact's planned effects, required permissions, variables/secrets handling, preflight checks, rollback/cleanup concerns, and a verification plan.
6. Ask the operator to run it in their environment and report results. Do not claim success until they provide evidence and the resulting state is read back.

## Secret and execution handling

- Never request credentials in chat or include them in source, command arguments, or logs.
- Use protected environment injection or the tool's supported secret provider; keep local secret files out of Git.
- Do not disable TLS validation by default.
- Do not change from read-only mode or elevate permissions to make an operation work.
- Do not use an alternate tool to get around an explicit denial.

## Validation gates

- Nutanix `nutanix.ncp` collection has operation-specific coverage; verify against its current docs and installed version.
- Provider and SDK support varies by Prism Central/AOS and API namespace/revision; verify exact target versions.
- V4 EA and RC APIs are not equivalent to GA for production support; verify stage and compatibility.
- The read-only/approval posture applies to generated artifacts in this MVP, not as a product claim about every agent client.

## References

- `references/methods-and-fallback.md` — workflow for deciding whether Ansible or another method is a valid alternative.
