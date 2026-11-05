locals {
  # Authentik OAuth2 provider/application "get-cookies" (authentik.mdekort.nl),
  # replacing the Cognito user pool client previously used here. Both the
  # client_id and the JWKS URL are public (no secret), so they're inlined
  # rather than sourced from a secrets store.
  authentik_client_id = "gR3DorO9O4wDWC5HPNzENVrPVPzfjcHaJVqfhZM9"
  authentik_jwks_url  = "https://authentik.mdekort.nl/application/o/get-cookies/jwks/"
}

data "archive_file" "empty_lambda" {
  type        = "zip"
  output_path = "lambda.zip"

  source {
    filename = "get_cookies/handler.py"
    content  = <<EOF
def handle(event, context):
  raise NotImplementedError
EOF
  }
}

resource "aws_lambda_function" "get_cookies" {
  function_name = "get-cookies"
  role          = aws_iam_role.get_cookies.arn
  handler       = "get_cookies.handler.handle"

  filename         = data.archive_file.empty_lambda.output_path
  source_code_hash = data.archive_file.empty_lambda.output_base64sha256

  runtime       = "python3.12"
  architectures = ["arm64"]
  memory_size   = 128
  timeout       = 8

  kms_key_arn = data.aws_kms_key.generic.arn

  environment {
    variables = {
      CLIENT_ID_LIST     = local.authentik_client_id
      KEY_ID             = aws_cloudfront_public_key.public_key.id
      JWKS_LIST          = local.authentik_jwks_url
      CLOUDFRONT_PK_PATH = aws_ssm_parameter.private_key.name
      ALLOWED_ORIGINS    = var.allowed_origins
    }
  }

  depends_on = [
    aws_iam_role_policy.get_cookies,
    aws_cloudwatch_log_group.get_cookies,
  ]

  lifecycle {
    ignore_changes = [source_code_hash]
  }
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "aws_lambda_permission" "get_cookies" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_cookies.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/${aws_api_gateway_method.api.http_method}${aws_api_gateway_resource.api.path}"
}
