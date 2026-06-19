#!/usr/bin/env bash
set -euo pipefail

: "${SKILLAYER_API_KEY:?Set SKILLAYER_API_KEY}"
: "${SKILLAYER_REPO_ID:?Set SKILLAYER_REPO_ID}"
: "${SKILLAYER_ORG_ID:?Set SKILLAYER_ORG_ID}"

API_URL="${SKILLAYER_API_URL:-https://api.skillayer.com}"

curl -s -H "API-Key: $SKILLAYER_API_KEY" -A "codex/1.0" \
  "$API_URL/repos/$SKILLAYER_REPO_ID/skills/load" | python3 -m json.tool

curl -s -H "Authorization: Bearer $SKILLAYER_API_KEY" -A "claude-code/1.0 anthropic" \
  "$API_URL/repos/$SKILLAYER_REPO_ID/skills/load" | python3 -m json.tool

curl -s -H "API-Key: $SKILLAYER_API_KEY" -A "cursor/1.0" \
  "$API_URL/repos/$SKILLAYER_REPO_ID/skills/load" | python3 -m json.tool

status="$(curl -s -H "Authorization: Bearer $SKILLAYER_API_KEY" "$API_URL/orgs/$SKILLAYER_ORG_ID/setup-status")"
echo "$status" | python3 -m json.tool
has_loads="$(printf '%s' "$status" | python3 -c 'import json,sys; print(str(json.load(sys.stdin).get("has_agent_loads")).lower())')"
echo "has_agent_loads=$has_loads"
test "$has_loads" = "true"
