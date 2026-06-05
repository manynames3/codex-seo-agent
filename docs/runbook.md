# Runbook

## Normal Operation

1. Open https://codex-seo-agent.pages.dev.
2. Paste the Lambda Function URL.
3. Paste the admin token from `.local/aws-admin-token.txt`.
4. Enter a Search Console property, for example `sc-domain:example.com`.
5. Connect Google if no token has been stored yet.
6. Run the workflow.
7. Open generated report links returned by the UI.

## Health Checks

```bash
curl https://YOUR_FUNCTION_URL/health
```

Authenticated report listing:

```bash
TOKEN="$(cat .local/aws-admin-token.txt)"
curl -H "Authorization: Bearer $TOKEN" https://YOUR_FUNCTION_URL/api/reports
```

## Common Failures

| Symptom | Likely Cause | Recovery |
|---|---|---|
| `Missing SSM parameter: /codex-seo-agent/google-client-secret-json` | Google OAuth web client has not been stored | Run `serverless/scripts/set-google-client-secret.sh` |
| `Stored Google credentials are invalid` | OAuth token expired or was revoked | Re-run Connect Google |
| `Invalid or missing admin token` | Wrong token in UI | Re-copy `.local/aws-admin-token.txt` |
| Competitors are `mock-competitor-*` | DataForSEO is not configured | Store optional DataForSEO SSM params |
| Lambda timeout | Workflow took more than 15 minutes | Split into async jobs or move long part to container worker |

## Rollback

- Frontend: revert or push a previous Git commit; Cloudflare Pages will redeploy `main`.
- Backend: redeploy an earlier Lambda artifact if available in the artifact S3 bucket, or revert the code and run `serverless/scripts/deploy-lambda.sh`.

## Recovery

- Reports are written to private S3. If a UI response is lost, list reports with `/api/reports`.
- OAuth can be re-established without replacing the stack by running the Google connect flow again.

## Escalation Notes

This is a single-operator work sample. It does not include paging, on-call rotation, or production SLOs.
