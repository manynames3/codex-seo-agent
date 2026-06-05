# Reviewer Guide

## What To Look At First

1. [README.md](../README.md) for the project story and evidence matrix.
2. [docs/architecture.md](architecture.md) for the runtime and deployment model.
3. [serverless/infra/template.yaml](../serverless/infra/template.yaml) for AWS infrastructure.
4. [serverless/lambda/app.py](../serverless/lambda/app.py) for the hosted workflow backend.
5. [.github/workflows/validate.yml](../.github/workflows/validate.yml) for validation discipline.

## What This Project Proves

- Ability to turn a local automation repo into a deployed cloud workflow.
- Cost-aware AWS service selection for low-volume workloads.
- Secure-enough single-operator secret handling without exposing Google credentials to the frontend.
- Honest operational documentation: runbook, teardown, security, observability, cost model, tradeoffs, and limitations.

## Evidence Map

- Infrastructure: `serverless/infra/template.yaml`
- Backend: `serverless/lambda/app.py`
- Frontend: `public/index.html`
- Local workflow scripts: `scripts/`
- Codex operating instructions: `AGENTS.md`, `workflow-guides/`, `codex-skill/`
- CI: `.github/workflows/validate.yml`
- Operations docs: `docs/runbook.md`, `docs/deployment.md`, `docs/teardown.md`
- Architecture decisions: `docs/adrs/README.md`

## How To Run Or Inspect

- Inspect live frontend: https://codex-seo-agent.pages.dev
- Run local scripts: follow [SETUP.md](../SETUP.md)
- Deploy/update Lambda: `./serverless/scripts/deploy-lambda.sh`
- Validate locally: run the commands in [docs/testing.md](testing.md)

## Strongest Engineering Decisions

- Kept the default deployment serverless and low-idle-cost instead of using always-on ECS/Fargate.
- Used SSM SecureString for single-operator secrets to avoid Secrets Manager monthly cost.
- Kept Lambda deployment manual because the repo is public and cloud mutations should be explicit.
- Documented mock SERP fallback instead of pretending it is live competitor intelligence.

## Tradeoffs

- Lambda Function URL with bearer token is cheaper and simpler than Cognito/API Gateway, but not appropriate for multi-user SaaS.
- Synchronous Lambda workflow is simple, but long workflows would need queueing or Step Functions.
- CloudFormation is direct and inspectable, but not as modular as Terraform/CDK for larger systems.

## Demo-Only Or Incomplete

- Google OAuth must be configured by the operator before real Search Console runs.
- DataForSEO is optional; otherwise competitor output is mock fallback.
- No formal unit test suite yet.
- No alarms, dashboards, WAF, custom domain, or user management.

## Improve Next

- Add unit tests for gap scoring, OAuth callback validation, and report serialization.
- Add CloudWatch alarms for Lambda errors and duration.
- Add async job status for long report runs.
- Add Cognito or Cloudflare Access if this becomes multi-user.
