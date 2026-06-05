#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-codex-seo-agent}"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/google-web-client-secret.json" >&2
  exit 1
fi

SECRET_FILE="$1"

python3 - <<'PY' "${SECRET_FILE}"
import json, sys
path = sys.argv[1]
data = json.load(open(path))
if "web" not in data:
    raise SystemExit("Expected a Google OAuth Web application client JSON with a top-level 'web' key.")
print(json.dumps(data, separators=(",", ":")))
PY

aws ssm put-parameter \
  --name "/${PROJECT_NAME}/google-client-secret-json" \
  --type SecureString \
  --value "$(python3 - <<'PY' "${SECRET_FILE}"
import json, sys
print(json.dumps(json.load(open(sys.argv[1])), separators=(",", ":")))
PY
)" \
  --overwrite >/dev/null

echo "Stored Google OAuth web client secret in /${PROJECT_NAME}/google-client-secret-json"
