#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${X4_URL:-http://127.0.0.1:8080}"

health="$(curl -fsS --max-time 5 "$BASE_URL/health")"
python - <<'PY' "$health"
import json, sys
payload = json.loads(sys.argv[1])
assert payload.get("status") == "ok", payload
assert payload.get("service") == "x4-arsenal", payload
print("X4 health: PASS")
PY

status="$(curl -fsS --max-time 5 "$BASE_URL/api/x4/status")"
python - <<'PY' "$status"
import json, sys
payload = json.loads(sys.argv[1])
assert payload.get("governance") == "enforced", payload
assert payload.get("service") == "x4-arsenal", payload
print("X4 governance/status: PASS")
PY

echo "X4 deployment verification: GREEN"
