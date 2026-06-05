# Testing And Validation

## Current Coverage

There is no formal unit or integration test suite yet. Current validation is syntax, template, smoke, and deployment checks.

## Local Validation Commands

```bash
python3 -m py_compile scripts/*.py
python3 -m py_compile codex-skill/seo-intelligence/scripts/*.py
python3 -m py_compile serverless/lambda/app.py
bash -n serverless/scripts/*.sh
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
HTMLParser().feed(Path("public/index.html").read_text())
print("public/index.html parsed")
PY
aws cloudformation validate-template --template-body file://serverless/infra/template.yaml
git diff --check
```

## Smoke Checks

```bash
curl https://YOUR_FUNCTION_URL/health

TOKEN="$(cat .local/aws-admin-token.txt)"
curl -H "Authorization: Bearer $TOKEN" https://YOUR_FUNCTION_URL/api/reports
```

## CI

`.github/workflows/validate.yml` runs dependency-light checks:

- Python compilation for local scripts, bundled skill scripts, and Lambda handler.
- Shell syntax validation for deploy scripts.
- Static HTML parser check for `public/index.html`.
- CloudFormation template file presence.
- `git diff --check`.

It does not deploy AWS resources.

## Gaps

- No unit tests for recommendation logic.
- No mocked Google Search Console API tests.
- No OAuth callback test harness.
- No browser e2e tests.
- No infrastructure policy scanner yet.
