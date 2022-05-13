resource "aws_cloudwatch_log_group" "convert_jwt" {
  name              = "/aws/lambda/convert-jwt"
  retention_in_days = 14
}

resource "aws_lambda_function" "convert_jwt" {
  function_name = "convert-jwt"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "index.handler"

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  runtime       = "nodejs16.x"
  architectures = ["arm64"]
  memory_size   = 128
  timeout       = 8

  kms_key_arn = data.aws_kms_key.generic.arn

  environment {
    variables = {
      CLIENT_ID          = "3ka58ejnvmq7q79tkttduq36aj"
      KEY_ID             = "APKARDHTW7OL4SWTL7AQ"
      JWKS_URI           = "https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_0yX8E3r8e/.well-known/jwks.json"
      CLOUDFRONT_PK_PATH = aws_ssm_parameter.cloudfront_signer_key.name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.convert_jwt,
  ]
}

resource "aws_lambda_permission" "convert_jwt" {
  statement_id  = "AllowAuthAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.convert_jwt.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.auth.execution_arn}/*/*/*"
}
