#!/usr/bin/env bash
set -euo pipefail
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests -v
