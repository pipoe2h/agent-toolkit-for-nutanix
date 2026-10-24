# MCP gaps and alternate automation

## Safe decision rule

MCP can expose only what its current server version, Prism Central V4 API release, downloaded artifacts, namespace settings, and caller permissions allow. An MCP call returning an error is not, by itself, proof that the feature is unsupported.

Before considering another method, classify the error:

1. **Network/DNS/TLS/authentication/authorization/service error:** diagnose that failure. Do not switch to Ansible or a different identity in order to bypass it.
2. **Bad request/schema:** inspect the current operation schema and correct the request.
3. **Operation absent from catalog:** verify it is not hidden by namespace scope or target PC version; then evaluate alternate coverage.
4. **Workflow fit:** even if MCP exposes each operation, a multi-step repeatable procedure or desired-state lifecycle may be better represented as Ansible or OpenTofu/Terraform.

## Candidate path: Ansible

The official Nutanix Ansible collection is `nutanix.ncp`. Its releases include V4 API/SDK-based modules, but support is module- and version-specific. For any generated playbook, verify:

- Collection version and required Ansible Core version.
- Exact module name and parameters in the installed collection documentation (`ansible-doc`) or current official Galaxy docs.
- Target Prism Central/AOS and API compatibility.
- Required IAM roles and permissions.
- Module idempotency, check-mode support, and behavior on retries.
- SDK/runtime prerequisites of the installed collection.

If any of these are unknown, mark them as gates; do not fabricate an Ansible example or imply the playbook is tested.

## Other methods

- **V4 SDK/API:** verify namespace and GA/RC/EA status and compatibility in the Nutanix developer portal for the target release. For production use, do not treat EA or RC as supported GA.
- **OpenTofu/Terraform:** verify the exact resource/data source in the provider documentation and version compatibility. IaC state semantics matter; do not substitute an imperative operation without explaining how drift and ownership are handled.

## Prototype execution boundary

This initial toolkit may help author commands or code, but the operator reviews and executes it. The agent must not run a playbook, SDK script that mutates state, or `tofu/terraform apply`. Any later change to that boundary requires an explicit product decision, least-privilege design, dry-run strategy, confirmation contract, audit plan, and tested rollback behavior.

## Sources

- Official Nutanix Ansible collection: `https://github.com/nutanix/nutanix.ansible` and `https://galaxy.ansible.com/ui/repo/published/nutanix/ncp/`.
- Nutanix V4 APIs and SDKs: `https://www.nutanix.dev/api-reference-v4/` and `https://developers.nutanix.com/`.
- Official Nutanix Terraform provider: `https://github.com/nutanix/terraform-provider-nutanix`.
- OpenTofu provider documentation: `https://search.opentofu.org/provider/nutanix/nutanix/latest`.
- Use each project's current docs and release notes before generating examples; links above identify sources, not a promise that a particular operation is covered.
