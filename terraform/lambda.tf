resource "aws_lambda_function" "convert-jwt" {
  filename      = "lambda.zip"
  function_name = "convert-jwt"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "app.lambdaHandler"

  source_code_hash = filebase64sha256("lambda.zip")

  runtime = "nodejs12.x"
}
