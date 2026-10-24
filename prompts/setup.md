# Setup prompt

Copy this single prompt into your AI agent after the repository is public:

```text
Set up Agent Toolkit for Nutanix by following instructions: https://raw.githubusercontent.com/pipoe2h/agent-toolkit-for-nutanix/master/setup-instructions/setup.md

Read the instructions first. Explain the planned changes and wait for my explicit approval before installing software, storing credentials locally, editing agent configuration, connecting to Prism Central, or running API calls. Do not ask me to paste secrets into chat. Keep the initial setup read-only with TLS verification enabled; do not run or apply Ansible, SDK, Terraform, or OpenTofu writes.
```

The detailed instructions are in [`setup-instructions/setup.md`](../setup-instructions/setup.md). They cover the current MCP Technical Preview, network access to customer-managed Prism Central, security gates, setup verification, and how to assess Ansible as an alternative without using it to bypass MCP errors or authorization failures.
