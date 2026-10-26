# Nutanix guidance

These rules are independent project guidance, not an authorization system. Prism Central RBAC and local execution controls remain authoritative.

- Start with the available MCP connection to the authorized Prism Central environment; do not assume a public Nutanix API endpoint.
- Verify the active Prism Central and AOS release and the actual discovered API operations before making product-specific claims.
- Begin read-only. Keep TLS verification enabled. Never request credentials in chat or place secrets in committed files, command arguments, logs, or generated examples.
- Do not treat an MCP error as permission to try another tool. Diagnose network, TLS, authentication, authorization, input, and missing-operation failures separately.
- If an operation is not exposed by MCP, evaluate official `nutanix.ncp` Ansible coverage for the target release. Use the exact supported module and collection version; do not invent module names or parameters.
- Use SDK/API code for custom workflows where the required operation is confirmed; use OpenTofu/Terraform when declarative state management is the right fit. These tools are complementary, not interchangeable.
- For this prototype, produce potentially mutating Ansible, SDK, Terraform, or OpenTofu artifacts only for human review and execution. Do not run or apply them.
- Treat the Nutanix V4 API MCP Server as Technical Preview according to its upstream repository until that status is explicitly changed.
- Report inventory results with returned/total counts and the operation used. Verify pagination and field projection; if the client cannot pass query parameters, say so and do not claim a complete list.
- Preserve existing agent configuration and project rules; append clearly delimited rules rather than overwriting existing content.
