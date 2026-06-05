# Observability

## Current Signals

- Lambda logs go to CloudWatch Logs.
- Frontend displays workflow errors returned by the API.
- Reports are persisted in S3 and can be listed through `/api/reports`.
- Cloudflare Pages shows deployment history for frontend changes.
- CloudFormation stack events show backend deployment history.

## What Is Logged

The Lambda logs exception type and message when a route fails. It does not intentionally print admin tokens, Google client JSON, or OAuth token JSON.

## Manual Checks

```bash
curl https://YOUR_FUNCTION_URL/health

TOKEN="$(cat .local/aws-admin-token.txt)"
curl -H "Authorization: Bearer $TOKEN" https://YOUR_FUNCTION_URL/api/reports
```

CloudWatch log group:

```text
/aws/lambda/codex-seo-agent-backend
```

## Missing Production Observability

- No CloudWatch alarms yet.
- No custom metrics for successful runs, failed runs, duration, or report counts.
- No traces.
- No dashboard-as-code.
- No synthetic check for the Cloudflare Pages frontend.

## Next Additions

- Lambda error alarm.
- Lambda duration alarm near the 15-minute timeout.
- Metric filters for authentication failures and workflow failures.
- Basic dashboard with invocations, errors, duration, and throttles.
