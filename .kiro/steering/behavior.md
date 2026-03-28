# get-cookies

> For global standards, way-of-workings, and pre-commit checklist, see `~/.kiro/steering/behavior.md`

## Role

Python developer and AWS engineer.

## What This Does

Serverless authentication solution that converts JWT tokens (from Cognito) to AWS CloudFront signed cookies. Deployed as a Lambda behind API Gateway.

## Lambda Deployment Pattern

Terraform creates the Lambda with dummy code and `ignore_changes` on `source_code_hash`. Actual code is deployed via `make build` (packages with dependencies for arm64) then Terraform or manual deploy.

## Repository Structure

- `get_cookies/` — Lambda handler source (JWT validation, cookie signing)
- `tests/` — Test suite (uses moto, requests-mock)
- `terraform/` — Lambda, API Gateway, IAM, Cognito integration, CloudWatch, KMS, SSM
- `Makefile` — `install`, `test`, `build`, `init`, `apply`, `decrypt`, `encrypt`

## Terraform Details

- Backend: S3 key in `mdekort-tfstate-075673041815`
- Secrets: KMS context `target=convert-jwt`

## Related Repositories

- `~/src/melvyndekort/tf-cognito` — Cognito user pool this Lambda validates against
- `~/src/melvyndekort/tf-cloudflare` — DNS for the API endpoint
