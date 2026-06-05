# Codex SEO Agent

A production-style AWS/cloud work sample for running a low-volume SEO intelligence workflow from Google Search Console data. The project includes a Cloudflare Pages control panel, an AWS Lambda Function URL backend, private S3 report storage, SSM SecureString secret handling, CloudFormation infrastructure, validation CI, and operational documentation.

**Positioning:** Serverless SEO workflow runner showing cost-aware cloud architecture, deployment discipline, security boundaries, observability tradeoffs, and teardown ownership.

Live demo: https://codex-seo-agent.pages.dev

Source: https://github.com/manynames3/codex-seo-agent

The live UI is real, but running reports requires an admin token and a Google OAuth Web client configured by the operator. No screenshot asset is committed; use the live demo for visual inspection.

## Problem

The upstream SEO workflow was useful as a local automation, but not credible as a cloud/platform engineering work sample. It needed a clear runtime model, hosted execution path, infrastructure, security posture, operational docs, validation checks, cost controls, and honest limitations.

## Solution

This repo keeps the local Codex workflow while adding a cheap hosted path:

- Cloudflare Pages serves a static control panel from `public/`.
- AWS Lambda runs the SEO workflow through a Function URL.
- SSM Parameter Store stores admin and OAuth secrets as SecureString values.
- S3 stores generated JSON, Markdown, and HTML reports.
- CloudFormation provisions backend infrastructure.
- GitHub Actions runs lightweight validation checks.

## Operational Value

The project demonstrates how to package a practical automation as an operated cloud system: explicit deploy scripts, bounded IAM, private report storage, manual backend deployment gates, public frontend CI/CD, recovery notes, teardown steps, and clear cost tradeoffs.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Static HTML/CSS/JS on Cloudflare Pages |
| Backend | AWS Lambda Function URL, Python 3.12 |
| Infrastructure | CloudFormation |
| Secrets | SSM Parameter Store SecureString |
| Storage | S3 private reports bucket |
| External APIs | Google Search Console API, optional DataForSEO |
| CI | GitHub Actions validation workflow |
| Local workflow | Python scripts and Codex project instructions |

## Engineering Highlights

- Low-idle-cost design: Lambda + S3 + SSM instead of always-on containers.
- Manual Lambda deploy gate while frontend auto-deploys from GitHub.
- Least-privilege-style IAM scoped to one S3 bucket and named SSM parameters.
- Public Function URL with app-level bearer token and documented limitations.
- Private S3 reports with presigned links returned to the UI.
- Clear teardown path for CloudFormation, S3 artifacts, SSM parameters, and Cloudflare Pages.
- Honest fallback behavior when DataForSEO is not configured.

## Architecture Overview

Read [docs/architecture.md](docs/architecture.md) for the C4-style diagram, runtime flow, data flow, auth flow, service boundaries, and deployment shape.

Short version:

```text
Browser -> Cloudflare Pages UI -> AWS Lambda Function URL
Lambda -> Google Search Console API
Lambda -> optional DataForSEO API
Lambda -> SSM SecureString for secrets
Lambda -> S3 for generated reports
```

## Evidence Matrix

| Area | Evidence |
|---|---|
| IaC | CloudFormation template in `serverless/infra/template.yaml`; validated with AWS CLI |
| CI/CD | GitHub Actions validation in `.github/workflows/validate.yml`; Cloudflare Pages Git integration for frontend |
| Security | SSM SecureString secrets, scoped Lambda IAM role, private S3 bucket, app-level bearer token; see `docs/security.md` |
| Reliability | Runbook, failure modes, rollback/recovery notes, manual backend deploy gate; see `docs/runbook.md` |
| Observability | CloudWatch Logs, frontend error surfacing, CloudFormation/Pages deployment history; gaps documented in `docs/observability.md` |
| Cost | Lambda/S3/SSM low-idle architecture, no Fargate/API Gateway/NAT Gateway; see `docs/cost-model.md` |
| Operations | Deployment, runbook, troubleshooting, and teardown docs under `docs/` |
| Testing | Syntax, HTML, shell, template, smoke, and whitespace validation; no formal unit suite yet; see `docs/testing.md` |
| Documentation | Architecture, reviewer guide, ADRs, tradeoffs, security, cost, deployment, teardown |

## Local Quickstart

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your Search Console property:

```text
GSC_SITE_URL=sc-domain:example.com
```

Run the local gap finder:

```bash
.venv/bin/python scripts/gap_finder.py
```

Or open Codex in the repo and say:

```text
Run the full weekly workflow
```

## Hosted Deployment

Frontend deploys from GitHub to Cloudflare Pages. Manual deploy:

```bash
wrangler pages deploy public --project-name codex-seo-agent --branch main
```

Backend deploys to AWS:

```bash
./serverless/scripts/deploy-lambda.sh
```

Create a Google OAuth **Web application** client and add:

```text
https://YOUR_FUNCTION_URL/auth/google/callback
```

Store the downloaded client JSON:

```bash
./serverless/scripts/set-google-client-secret.sh /path/to/google-web-client-secret.json
```

More detail: [docs/deployment.md](docs/deployment.md).

## Test And Validation Commands

```bash
python3 -m py_compile scripts/*.py
python3 -m py_compile codex-skill/seo-intelligence/scripts/*.py
python3 -m py_compile serverless/lambda/app.py
bash -n serverless/scripts/*.sh
aws cloudformation validate-template --template-body file://serverless/infra/template.yaml
git diff --check
```

Smoke checks after backend deploy:

```bash
curl https://YOUR_FUNCTION_URL/health

TOKEN="$(cat .local/aws-admin-token.txt)"
curl -H "Authorization: Bearer $TOKEN" https://YOUR_FUNCTION_URL/api/reports
```

## Security Summary

- Admin token is generated locally and stored in SSM SecureString.
- Google OAuth client and token JSON are stored in SSM SecureString.
- S3 report bucket blocks public access.
- Lambda IAM role is scoped to required S3 and SSM resources.
- Function URL is public but protected by app-level bearer token.

This is a single-operator model, not a complete multi-user SaaS auth system. See [docs/security.md](docs/security.md).

## Observability Summary

- Lambda execution logs go to CloudWatch Logs.
- CloudFormation and Cloudflare Pages provide deployment history.
- The frontend displays API errors.
- No production alarms or custom metrics are configured yet.

See [docs/observability.md](docs/observability.md).

## Cost Controls

- No always-on compute.
- No NAT Gateway.
- No API Gateway required for the current backend.
- SSM SecureString is used instead of Secrets Manager for a small number of low-rotation secrets.
- Reports are small private S3 objects.

See [docs/cost-model.md](docs/cost-model.md).

## Teardown

Teardown covers the CloudFormation stack, S3 buckets/objects, SSM parameters, Cloudflare Pages project, and local generated files. See [docs/teardown.md](docs/teardown.md).

## Project Structure

```text
public/                    Cloudflare Pages control panel
serverless/lambda/         Lambda backend source and requirements
serverless/infra/          CloudFormation template
serverless/scripts/        Backend deploy and secret setup scripts
scripts/                   Local SEO workflow scripts
workflow-guides/           Codex-readable workflow guides
codex-skill/               Optional installable Codex skill
docs/                      Architecture and operations documentation
examples/sample-reports/   Upstream sample reports
reports/                   Local generated reports
drafts/                    Local generated article drafts
```

## Known Limitations

- Google OAuth setup is manual.
- DataForSEO is optional; without it, competitor intelligence uses mock fallback competitors.
- No formal unit/integration/e2e test suite yet.
- No Cognito, Cloudflare Access, WAF, custom domain, or multi-user authorization.
- Lambda workflow is synchronous and bounded by Lambda timeout.
- No CloudWatch alarms or dashboard-as-code yet.

## What I Would Improve Next

- Add unit tests around scoring, OAuth callback handling, and report serialization.
- Add CloudWatch alarms for Lambda errors and long duration.
- Restrict CORS to the Pages domain.
- Add async job status for long-running workflows.
- Add Cloudflare Access or Cognito if this becomes team-facing.
- Add lifecycle cleanup for Lambda artifact zips.
