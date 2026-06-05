# Cost Model

This repo is designed for low-volume operation. It intentionally avoids always-on containers, NAT Gateway, API Gateway, and per-secret monthly Secrets Manager charges.

## Main Cost Drivers

| Component | Cost Behavior |
|---|---|
| Cloudflare Pages | Free/low-cost static hosting depending on account plan |
| Lambda Function URL | Pay per invocation and duration; no idle compute cost |
| S3 reports bucket | Storage and request cost; report files are small |
| SSM Parameter Store | Standard parameters are low/no monthly cost; API calls are small at this volume |
| CloudWatch Logs | Log ingestion/storage cost; keep logs concise |
| DataForSEO | External paid API if configured |

## Cost Controls

- Lambda only runs when the operator starts OAuth, lists reports, or runs the workflow.
- Lambda is outside a VPC, avoiding NAT Gateway hourly charges.
- Reports are private S3 objects rather than a database cluster.
- Secrets are SSM SecureString parameters rather than many Secrets Manager secrets.
- Deployment is manual for Lambda, reducing accidental cloud changes from every Git push.

## Cost Risks

- Long report runs can increase Lambda duration cost and hit timeout.
- Very verbose logging can increase CloudWatch cost.
- DataForSEO usage is external and should be monitored separately.
- Artifact zips accumulate in the artifact bucket unless lifecycle rules or manual cleanup are added.

## Cleanup

See [teardown.md](teardown.md). Teardown should remove the CloudFormation stack, report bucket objects, artifact bucket objects, and SSM parameters.
