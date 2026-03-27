#!/bin/bash
# Helper per testare template flow Activepieces
# Usage: source test_helper.sh

API="http://localhost:8080/api/v1"
PROJECT_ID="ctxq6E1nbcME4wTgkD5Qe"

get_token() {
  local cfg="$HOME/.config/activepieces/config.toml"
  local email=$(python3 -c "import tomllib; d=tomllib.load(open('$cfg','rb')); print(d['default']['email'])")
  local password=$(python3 -c "import tomllib; d=tomllib.load(open('$cfg','rb')); print(d['default']['password'])")
  TOKEN=$(curl -s -X POST "$API/authentication/sign-in" -H 'Content-Type: application/json' \
    -d "{\"email\":\"$email\",\"password\":\"$password\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
  echo "$TOKEN"
}

create_flow() {
  local name="$1"
  local token=$(get_token)
  curl -s -X POST "$API/flows" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "{\"projectId\":\"$PROJECT_ID\",\"displayName\":\"$name\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])"
}

flow_op() {
  local flow_id="$1"
  local body="$2"
  local token=$(get_token)
  curl -s -X POST "$API/flows/$flow_id" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "$body"
}

publish_and_enable() {
  local flow_id="$1"
  flow_op "$flow_id" '{"type":"LOCK_AND_PUBLISH","request":{}}' > /dev/null
  flow_op "$flow_id" '{"type":"CHANGE_STATUS","request":{"status":"ENABLED"}}' > /dev/null
  sleep 2
  local token=$(get_token)
  local status=$(curl -s "$API/flows/$flow_id" -H "Authorization: Bearer $token" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'], d.get('operationStatus',''))")
  echo "$status"
}

disable_flow() {
  local flow_id="$1"
  flow_op "$flow_id" '{"type":"CHANGE_STATUS","request":{"status":"DISABLED"}}' > /dev/null
  sleep 1
}

delete_flow() {
  local flow_id="$1"
  local token=$(get_token)
  curl -s -X DELETE "$API/flows/$flow_id" -H "Authorization: Bearer $token" > /dev/null
}

get_runs() {
  local flow_id="$1"
  local token=$(get_token)
  curl -s "$API/flow-runs?projectId=$PROJECT_ID&flowId=$flow_id&limit=1" \
    -H "Authorization: Bearer $token"
}

send_webhook() {
  local flow_id="$1"
  local payload="$2"
  curl -s -X POST "$API/webhooks/$flow_id" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

test_trigger() {
  local flow_id="$1"
  local token=$(get_token)
  curl -s -X POST "$API/v1/test-trigger" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "{\"flowId\":\"$flow_id\",\"projectId\":\"$PROJECT_ID\",\"testStrategy\":\"SIMULATION\"}"
}
