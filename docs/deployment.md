# Deployment

## Frontend

The frontend is a user-facing interface in `public/index.html` plus a same-origin Pages Function proxy in `functions/api/[[path]].js`.

- Hosted on Cloudflare Pages.
- Git-integrated with the public GitHub repository.
- Pushes to `main` trigger frontend deployment.
- Pages secrets provide the backend URL and backend access key to the proxy.

Manual deploy command if needed:

```bash
wrangler pages deploy public --project-name codex-seo-agent --branch main
```

## Backend

The backend is deployed with CloudFormation and a Lambda zip artifact:

```bash
./serverless/scripts/deploy-lambda.sh
```

The script:

1. Generates or reuses `.local/aws-admin-token.txt`.
2. Installs Lambda dependencies into `.local/lambda-build`.
3. Zips the Lambda package.
4. Uploads the zip to an artifact S3 bucket.
5. Stores the admin token in SSM SecureString.
6. Deploys `serverless/infra/template.yaml`.
7. Prints CloudFormation outputs.

After the backend exists, configure the Cloudflare Pages Function proxy:

```bash
printf '%s' 'https://YOUR_FUNCTION_URL' | npx wrangler pages secret put BACKEND_URL --project-name codex-seo-agent
npx wrangler pages secret put BACKEND_ADMIN_TOKEN --project-name codex-seo-agent < .local/aws-admin-token.txt
```

## Google OAuth Setup

Create a Google OAuth Web application client. Add:

```text
https://YOUR_FUNCTION_URL/auth/google/callback
```

as an authorized redirect URI.

Store the downloaded JSON:

```bash
./serverless/scripts/set-google-client-secret.sh /path/to/google-web-client-secret.json
```

## Deployment Discipline

- Frontend deploys automatically from GitHub.
- Backend deployment is explicit and local because it mutates AWS resources and writes secrets.
- CloudFormation is the source of truth for backend infrastructure.
- Cloudflare Pages secrets are required for the browser UI to run reports without exposing backend details.

## Validation Before Deploy

```bash
python3 -m py_compile scripts/*.py serverless/lambda/app.py
bash -n serverless/scripts/*.sh
aws cloudformation validate-template --template-body file://serverless/infra/template.yaml
```
