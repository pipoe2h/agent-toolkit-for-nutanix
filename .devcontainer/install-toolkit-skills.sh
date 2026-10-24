#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# OpenCode discovers these project-local skills via .agents/skills/SKILL.md.
npx --yes skills@1.7.4 add . \
  -s nutanix-connect-prism-central \
  -s nutanix-automation-method-selection \
  -y -a opencode -p

printf '\nOpenCode toolkit skills are installed in .agents/skills/.\n'
printf 'The Dev Container does not configure an LLM provider or contact Prism Central.\n'
printf 'For the optional NAI provider example, see examples/opencode/README.md.\n'
