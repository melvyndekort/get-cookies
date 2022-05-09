resource "aws_cloudwatch_log_group" "convert_jwt" {
  name              = "/aws/lambda/convert-jwt"
  retention_in_days = 14
}

resource "aws_lambda_function" "convert_jwt" {
  function_name = "convert-jwt"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.lambda_handler"

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  runtime     = "python3.9"
  memory_size = 128

  kms_key_arn = data.terraform_remote_state.aws_mdekort.outputs.generic_kms_key_arn

  environment {
    variables = {
      CLIENT_ID          = ""
      KEY_ID             = "APKARDHTW7OL4SWTL7AQ"
      JWKS_URI           = ""
      CLOUDFRONT_PK_PATH = aws_ssm_parameter.cloudfront_signer_key.name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.convert_jwt,
  ]
}
