# Architecture

Codex SEO Agent is a low-volume SEO workflow runner. The public frontend is a static Cloudflare Pages control panel. The hosted backend is an AWS Lambda Function URL that runs a Google Search Console workflow, writes report artifacts to S3, and stores OAuth/admin secrets in SSM Parameter Store.

## Container Diagram

```mermaid
C4Container
    title Codex SEO Agent - container view
    Person(operator, "Operator", "Runs SEO analysis for a Search Console property")
    System_Ext(gsc, "Google Search Console API", "Query-level performance data")
    System_Ext(dataforseo, "DataForSEO API", "Optional live SERP data")
    System_Ext(github, "GitHub", "Source repository and Cloudflare Pages trigger")

    System_Boundary(cloudflare, "Cloudflare") {
      Container(pages, "Cloudflare Pages", "Static HTML/CSS/JS", "Control panel UI served from public/index.html")
    }

    System_Boundary(aws, "AWS") {
      Container(lambda, "Lambda Function URL", "Python 3.12", "OAuth, report workflow, report API")
      ContainerDb(ssm, "SSM Parameter Store", "SecureString", "Admin token, Google OAuth client JSON, Google refresh token, optional DataForSEO credentials")
      ContainerDb(s3, "S3 Reports Bucket", "Private object storage", "Generated JSON, Markdown, and HTML reports")
      Container(logs, "CloudWatch Logs", "Managed logs", "Lambda execution logs")
      Container(cfn, "CloudFormation", "IaC", "Lambda, IAM role, S3 bucket, Function URL permissions")
    }

    Rel(operator, pages, "Uses browser UI")
    Rel(pages, lambda, "Calls Function URL with bearer admin token")
    Rel(lambda, ssm, "Reads/writes SecureString parameters")
    Rel(lambda, gsc, "Fetches Search Console data with OAuth token")
    Rel(lambda, dataforseo, "Optionally fetches live SERP data")
    Rel(lambda, s3, "Writes reports and generates presigned links")
    Rel(lambda, logs, "Writes logs")
    Rel(github, pages, "Triggers Pages deployment on main")
    Rel(cfn, lambda, "Provisions backend")
```

## Runtime Flow

1. The operator opens the Cloudflare Pages UI.
2. The operator enters the Lambda Function URL, admin token, and Search Console property.
3. `Connect Google` starts Google OAuth through `/auth/google/start`.
4. Google redirects back to `/auth/google/callback`; Lambda stores the OAuth token JSON in SSM SecureString.
5. `Run Workflow` calls `/api/run` with the admin token.
6. Lambda fetches Search Console data, identifies ranking gaps, optionally calls DataForSEO, creates a content plan, writes reports to S3, and returns summary JSON plus presigned report links.

## Deployment Shape

- Frontend: Cloudflare Pages, Git-integrated with the GitHub `main` branch.
- Backend: CloudFormation stack `codex-seo-agent-lambda`.
- Artifact packaging: `serverless/scripts/deploy-lambda.sh` builds a Lambda zip in `.local/`, uploads it to an artifact bucket, stores an admin token in SSM, and deploys CloudFormation.
- Reports: private S3 bucket created by CloudFormation.

## AWS Boundaries

- Lambda runs outside a VPC to avoid NAT Gateway cost and complexity.
- Lambda Function URL is public with app-level bearer-token authorization.
- The IAM role is scoped to the reports bucket and named SSM parameters.
- S3 public access is blocked.

## Data Flow

- Search Console query data enters Lambda from Google APIs.
- Report JSON/Markdown/HTML is written to S3 under date-based prefixes.
- The frontend receives summary JSON and time-limited presigned links.
- Admin token and OAuth tokens are not committed to Git and are stored outside the frontend.

## Auth Flow

- App access uses a single admin bearer token stored in SSM and pasted into the browser UI.
- Google Search Console access uses OAuth Web application flow.
- The OAuth callback URL is the Lambda Function URL path `/auth/google/callback`.

## CI/CD Flow

- GitHub `main` pushes trigger Cloudflare Pages for the static frontend.
- GitHub Actions validate Python syntax, shell syntax, static HTML parsing, CloudFormation template presence, and whitespace.
- Lambda deployment is manual via `serverless/scripts/deploy-lambda.sh`; this is intentional to avoid accidental cloud changes from public repo pushes.

## Key Constraints

- The hosted backend is designed for one operator, not multi-tenant SaaS use.
- Lambda has a 15-minute timeout. Long-running SERP work would need async jobs or a container worker.
- DataForSEO is optional; without credentials, competitor analysis uses mock fallback data.
- There is no custom domain, WAF, or Cognito login yet.
