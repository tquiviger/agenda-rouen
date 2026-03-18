#!/usr/bin/env bash
# Generate requirements.txt from pyproject.toml for SAM build.
# SAM doesn't support uv/pyproject.toml natively — it needs requirements.txt.
set -euo pipefail

cd "$(dirname "$0")/.."
uv pip compile pyproject.toml -o requirements.txt --no-header
echo "Generated requirements.txt"
