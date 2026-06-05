# Architecture Decision Records

## ADR 001 - Use Lambda Function URL For The Hosted Backend

**Status:** Accepted

**Context:** The project needs a hosted way to run a low-volume SEO workflow from a browser without paying for always-on compute.

**Decision:** Use AWS Lambda with a Function URL for the backend API.

**Consequences:** There is no idle compute cost and the deployment remains small. The backend must finish within Lambda limits and app-level authorization must be implemented carefully.

## ADR 002 - Store Single-Operator Secrets In SSM SecureString

**Status:** Accepted

**Context:** The app needs to store an admin token, Google OAuth client JSON, Google OAuth token JSON, and optional DataForSEO credentials.

**Decision:** Use SSM Parameter Store SecureString parameters.

**Consequences:** This avoids the fixed per-secret monthly cost of Secrets Manager for a small work sample. It does not provide the same rotation ergonomics as Secrets Manager.

## ADR 003 - Keep Lambda Deployment Manual

**Status:** Accepted

**Context:** The repo is public and backend deployment mutates AWS resources and writes secrets.

**Decision:** Frontend deploys automatically from GitHub to Cloudflare Pages, but Lambda deployment is manual through `serverless/scripts/deploy-lambda.sh`.

**Consequences:** Cloud changes are explicit and controlled. Backend deploys are less automated than a production CI/CD pipeline.

## ADR 004 - Avoid VPC And NAT Gateway

**Status:** Accepted

**Context:** The Lambda needs outbound internet access to Google Search Console and optional DataForSEO.

**Decision:** Run Lambda outside a VPC.

**Consequences:** The app avoids NAT Gateway hourly cost and networking complexity. It does not access private VPC resources.

## ADR 005 - Keep Mock Competitor Fallback

**Status:** Accepted

**Context:** DataForSEO is optional and paid.

**Decision:** If DataForSEO credentials are missing, competitor analysis returns clearly labeled mock fallback data.

**Consequences:** The workflow remains demonstrable without paid credentials, but mock competitor output is not real SERP intelligence.
