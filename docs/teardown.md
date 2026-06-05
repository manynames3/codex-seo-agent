# Teardown

Use this when the hosted demo is no longer needed.

## 1. Delete CloudFormation Stack

```bash
aws cloudformation delete-stack --stack-name codex-seo-agent-lambda
aws cloudformation wait stack-delete-complete --stack-name codex-seo-agent-lambda
```

If deletion fails because S3 buckets contain objects, empty buckets first.

## 2. Empty And Delete Artifact Bucket

The deploy script creates an artifact bucket named like:

```text
codex-seo-agent-lambda-artifacts-ACCOUNT-REGION
```

Empty and delete it:

```bash
aws s3 rm s3://BUCKET_NAME --recursive
aws s3api delete-bucket --bucket BUCKET_NAME
```

## 3. Delete SSM Parameters

```bash
aws ssm delete-parameter --name /codex-seo-agent/admin-token
aws ssm delete-parameter --name /codex-seo-agent/google-client-secret-json
aws ssm delete-parameter --name /codex-seo-agent/google-token-json
aws ssm delete-parameter --name /codex-seo-agent/dataforseo-login
aws ssm delete-parameter --name /codex-seo-agent/dataforseo-password
```

Some optional parameters may not exist.

## 4. Delete Cloudflare Pages Project

```bash
wrangler pages project delete codex-seo-agent
```

## 5. Delete Local Generated Files

```bash
rm -rf .local .venv reports/* drafts/*
```

## Notes

- The public GitHub repository is not deleted by this teardown.
- Google OAuth app cleanup happens in Google Cloud Console.
- DataForSEO account cleanup happens outside AWS.
