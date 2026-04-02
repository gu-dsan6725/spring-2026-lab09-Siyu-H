#!/usr/bin/env bash
# Regenerate alice_output.txt and carol_output.txt against a local API on :9090.
# Start the server first:
#   uv run uvicorn agent_api:app --host 127.0.0.1 --port 9090

set -euo pipefail
BASE="http://127.0.0.1:9090"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required (brew install jq)" >&2
  exit 1
fi

call() {
  local user_id="$1"
  local run_id="$2"
  local query="$3"
  curl -s -X POST "${BASE}/invocation" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg u "$user_id" --arg r "$run_id" --arg q "$query" \
      '{user_id:$u, run_id:$r, query:$q}')" | jq -r '.response'
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Alice Session 1 ===" > alice_output.txt
echo "" >> alice_output.txt

echo "User: Hi, I'm Alice. I'm a software engineer." >> alice_output.txt
r="$(call alice alice-session-1 "Hi, I'm Alice. I'm a software engineer.")"
echo "Agent: $r" >> alice_output.txt
echo "" >> alice_output.txt

echo "User: I prefer Python for development." >> alice_output.txt
r="$(call alice alice-session-1 "I prefer Python for development.")"
echo "Agent: $r" >> alice_output.txt
echo "" >> alice_output.txt

echo "User: What programming languages do I like?" >> alice_output.txt
r="$(call alice alice-session-1 "What programming languages do I like?")"
echo "Agent: $r" >> alice_output.txt
echo "" >> alice_output.txt

echo "User: I'm working on a FastAPI project." >> alice_output.txt
r="$(call alice alice-session-1 "I'm working on a FastAPI project.")"
echo "Agent: $r" >> alice_output.txt
echo "" >> alice_output.txt

echo "User: What have we discussed so far?" >> alice_output.txt
r="$(call alice alice-session-1 "What have we discussed so far?")"
echo "Agent: $r" >> alice_output.txt
echo "" >> alice_output.txt

# Mem0 queues memory processing; search needs a delay before Session 2 (cross-session demo)
echo "Waiting ~50s for Mem0 to index Alice Session 1..." >&2
sleep 50

echo "" >> alice_output.txt
echo "=== Alice Session 2 (New Session) ===" >> alice_output.txt
echo "" >> alice_output.txt

echo "User: What do you remember about me?" >> alice_output.txt
r="$(call alice alice-session-2 "What do you remember about me?")"
echo "Agent: $r" >> alice_output.txt
echo "" >> alice_output.txt

echo "User: What project am I working on?" >> alice_output.txt
r="$(call alice alice-session-2 "What project am I working on?")"
echo "Agent: $r" >> alice_output.txt
echo "" >> alice_output.txt

echo "=== Carol Session 1 ===" > carol_output.txt
echo "" >> carol_output.txt

echo "User: Hi, I'm Carol. I'm a data scientist." >> carol_output.txt
r="$(call carol carol-session-1 "Hi, I'm Carol. I'm a data scientist.")"
echo "Agent: $r" >> carol_output.txt
echo "" >> carol_output.txt

echo "User: What programming languages do I like?" >> carol_output.txt
r="$(call carol carol-session-1 "What programming languages do I like?")"
echo "Agent: $r" >> carol_output.txt
echo "" >> carol_output.txt

echo "User: Do you know what Alice prefers?" >> carol_output.txt
r="$(call carol carol-session-1 "Do you know what Alice prefers?")"
echo "Agent: $r" >> carol_output.txt
echo "" >> carol_output.txt

echo "Wrote alice_output.txt and carol_output.txt"
