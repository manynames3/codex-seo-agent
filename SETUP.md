# Codex SEO Agent Setup

## Step 1 - Install Dependencies

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Step 2 - Google Search Console OAuth

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing project.
3. Go to APIs & Services > Library.
4. Search for "Google Search Console API" and enable it.
5. Go to APIs & Services > Credentials.
6. Click Create Credentials > OAuth client ID.
7. Choose Desktop app.
8. Download the JSON file, rename it `credentials.json`, and place it in this project folder.

## Step 3 - Set `.env`

```bash
cp .env.example .env
```

Edit `.env` and set:

- `GSC_SITE_URL` for your Search Console property.
- Domain property format: `sc-domain:yourdomain.com`
- URL-prefix property format: `https://www.yourdomain.com/`

## Step 4 - First Run

```bash
.venv/bin/python scripts/gap_finder.py
```

A browser window will ask you to authorize with your Google account. After authorization, `token.pickle` is saved so future runs do not need another login.

## Step 5 - Use Codex

Open Codex in this project folder and say:

```text
Run this week's gap analysis
```

Codex will read `AGENTS.md`, use the relevant guide in `workflow-guides/`, run the script, and brief you on findings.

For the complete workflow, say:

```text
Run the full weekly workflow
```

Codex will run gap analysis, competitor intelligence, the weekly content-plan check-in, content planning, and dashboard generation.

## Optional - Install the Reusable Codex Skill

This repository includes an optional installable skill at `codex-skill/seo-intelligence`.

To make it available in any Codex workspace:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex-skill/seo-intelligence "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex, then invoke it with:

```text
Use $seo-intelligence to run the weekly SEO workflow for my site.
```

## Optional - DataForSEO

Sign up at https://dataforseo.com and add credentials to `.env`:

```bash
DATAFORSEO_LOGIN=your@email.com
DATAFORSEO_PASSWORD=yourpassword
```

This unlocks live competitor SERP data. Without it, the competitor script uses mock fallback competitors, so those results should be treated as a workflow demo. Gap analysis and content planning still use Google Search Console impressions as a useful volume proxy.

## Optional - Hosted Low-Cost Lambda Backend

Use this when you want the deployed website to run the SEO workflow instead of running scripts locally.

Deploy the backend:

```bash
./serverless/scripts/deploy-lambda.sh
```

The script creates:

- Lambda Function URL API
- Private S3 reports bucket
- IAM role for Lambda
- SSM SecureString admin token

The admin token is saved locally at:

```text
.local/aws-admin-token.txt
```

Create a Google OAuth **Web application** client in Google Cloud Console, then add the Lambda callback URL as an authorized redirect URI:

```text
https://YOUR_FUNCTION_URL/auth/google/callback
```

Store the downloaded Google web client JSON:

```bash
./serverless/scripts/set-google-client-secret.sh /path/to/google-web-client-secret.json
```

Open the Cloudflare Pages site, paste:

- Lambda Function URL
- Admin token
- Search Console property, for example `sc-domain:example.com`

Then click **Connect Google**, finish OAuth, and run the workflow.

For DataForSEO in Lambda, store optional credentials:

```bash
aws ssm put-parameter --name /codex-seo-agent/dataforseo-login --type SecureString --value "you@example.com" --overwrite
aws ssm put-parameter --name /codex-seo-agent/dataforseo-password --type SecureString --value "password" --overwrite
```
