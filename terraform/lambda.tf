resource "aws_cloudwatch_log_group" "get_cookies" {
  name              = "/aws/lambda/get-cookies"
  retention_in_days = 14
}

resource "aws_lambda_function" "get_cookies" {
  function_name = "get-cookies"
  role          = aws_iam_role.get_cookies.arn
  handler       = "lambda_function.lambda_handler"

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  runtime       = "python3.9"
  architectures = ["arm64"]
  memory_size   = 128
  timeout       = 8

  kms_key_arn = data.aws_kms_key.generic.arn

  environment {
    variables = {
      CLIENT_ID          = aws_cognito_user_pool_client.get_cookies.id
      KEY_ID             = aws_cloudfront_public_key.public_key.id
      JWKS_URI           = "https://${data.terraform_remote_state.cloudsetup.outputs.auth_user_pool_endpoint}/.well-known/jwks.json"
      CLOUDFRONT_PK_PATH = aws_ssm_parameter.private_key.name
    }
  }

  depends_on = [
    aws_iam_role_policy.get_cookies,
    aws_cloudwatch_log_group.get_cookies,
  ]
}

resource "aws_lambda_permission" "get_cookies" {
  statement_id  = "AllowAuthAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_cookies.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*/*"
}
