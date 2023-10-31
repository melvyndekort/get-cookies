resource "aws_cloudwatch_log_group" "get_cookies" {
  name              = "/aws/lambda/get-cookies"
  retention_in_days = 7
  kms_key_id        = data.aws_kms_key.generic.arn
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

  layers = [
    "arn:aws:lambda:eu-west-1:901920570463:layer:aws-otel-python-arm64-ver-1-20-0:2",
  ]

  runtime       = "python3.9"
  architectures = ["arm64"]
  memory_size   = 128
  timeout       = 8

  tracing_config {
    mode = "Active"
  }

  kms_key_arn = data.aws_kms_key.generic.arn

  environment {
    variables = {
      CLIENT_ID_LIST          = aws_cognito_user_pool_client.get_cookies.id
      KEY_ID                  = aws_cloudfront_public_key.public_key.id
      JWKS_LIST               = "https://${data.terraform_remote_state.cloudsetup.outputs.auth_user_pool_endpoint}/.well-known/jwks.json"
      CLOUDFRONT_PK_PATH      = aws_ssm_parameter.private_key.name
      AWS_LAMBDA_EXEC_WRAPPER = "/opt/otel-instrument"
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
