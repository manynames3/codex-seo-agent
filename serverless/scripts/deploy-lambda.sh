#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-codex-seo-agent}"
STACK_NAME="${STACK_NAME:-codex-seo-agent-lambda}"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ARTIFACT_BUCKET="${ARTIFACT_BUCKET:-${PROJECT_NAME}-lambda-artifacts-${ACCOUNT_ID}-${REGION}}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="${ROOT_DIR}/.local/lambda-build"
ZIP_PATH="${ROOT_DIR}/.local/${PROJECT_NAME}-lambda.zip"
ADMIN_TOKEN_FILE="${ROOT_DIR}/.local/aws-admin-token.txt"
CODE_KEY="lambda/${PROJECT_NAME}-$(date +%Y%m%d%H%M%S).zip"

mkdir -p "${ROOT_DIR}/.local"

if [[ ! -f "${ADMIN_TOKEN_FILE}" ]]; then
  openssl rand -hex 32 > "${ADMIN_TOKEN_FILE}"
  chmod 600 "${ADMIN_TOKEN_FILE}"
fi

ADMIN_TOKEN="$(cat "${ADMIN_TOKEN_FILE}")"

if ! aws s3api head-bucket --bucket "${ARTIFACT_BUCKET}" >/dev/null 2>&1; then
  if [[ "${REGION}" == "us-east-1" ]]; then
    aws s3api create-bucket --bucket "${ARTIFACT_BUCKET}" --region "${REGION}" >/dev/null
  else
    aws s3api create-bucket \
      --bucket "${ARTIFACT_BUCKET}" \
      --region "${REGION}" \
      --create-bucket-configuration LocationConstraint="${REGION}" >/dev/null
  fi
fi

rm -rf "${BUILD_DIR}" "${ZIP_PATH}"
mkdir -p "${BUILD_DIR}"

python3 -m pip install \
  --platform manylinux2014_x86_64 \
  --target "${BUILD_DIR}" \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  -r "${ROOT_DIR}/serverless/lambda/requirements.txt"

cp "${ROOT_DIR}/serverless/lambda/app.py" "${BUILD_DIR}/app.py"

(
  cd "${BUILD_DIR}"
  zip -qr "${ZIP_PATH}" .
)

aws s3 cp "${ZIP_PATH}" "s3://${ARTIFACT_BUCKET}/${CODE_KEY}" >/dev/null

aws ssm put-parameter \
  --name "/${PROJECT_NAME}/admin-token" \
  --type SecureString \
  --value "${ADMIN_TOKEN}" \
  --overwrite >/dev/null

aws cloudformation deploy \
  --stack-name "${STACK_NAME}" \
  --template-file "${ROOT_DIR}/serverless/infra/template.yaml" \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    ProjectName="${PROJECT_NAME}" \
    LambdaCodeBucket="${ARTIFACT_BUCKET}" \
    LambdaCodeKey="${CODE_KEY}"

aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" \
  --query 'Stacks[0].Outputs' \
  --output table

echo
echo "Admin token saved locally at: ${ADMIN_TOKEN_FILE}"
echo "Do not commit or share this token."
