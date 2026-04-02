#!/usr/bin/env bash
# Run three DuckDuckGo-style queries non-interactively (EXERCISE Problem 1).
# Optional: MCP_SMOKE=1 adds one doc-focused turn for Problem 2 traces.
#
# Usage (from repo root, after cp .env.example .env and filling keys):
#   cd simple-agent-observability && bash run_observability_lab.sh

set -euo pipefail
cd "$(dirname "$0")"
export OBSERVABILITY_BATCH="${OBSERVABILITY_BATCH:-1}"
export MCP_SMOKE="${MCP_SMOKE:-1}"
uv run python agent.py
