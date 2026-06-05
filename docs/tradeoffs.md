# Tradeoffs

## Lambda Function URL Instead Of API Gateway

**Why:** lower cost and less infrastructure for a single-operator tool.

**Tradeoff:** fewer built-in API management features. The app handles bearer-token authorization itself.

## SSM Parameter Store Instead Of Secrets Manager

**Why:** lower fixed monthly cost for a small number of low-rotation secrets.

**Tradeoff:** fewer lifecycle and rotation features.

## Synchronous Workflow Instead Of Queue-Based Jobs

**Why:** simpler control panel and less infrastructure.

**Tradeoff:** Lambda must finish within 15 minutes. Long competitor analysis should become an async job.

## CloudFormation Instead Of Terraform/CDK

**Why:** no extra toolchain; AWS-native template is easy to inspect in a public repo.

**Tradeoff:** less modular and less ergonomic than Terraform or CDK for a larger platform.

## Public Function URL With App Token Instead Of Cognito

**Why:** cheap and fast for a single operator.

**Tradeoff:** not a full user-management or SSO model. Cognito or Cloudflare Access would be better for teams.

## Mock SERP Fallback

**Why:** lets the workflow run without paid DataForSEO credentials.

**Tradeoff:** mock competitor output is not live market intelligence and is labeled as such.
