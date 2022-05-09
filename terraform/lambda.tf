resource "aws_lambda_function" "convert-jwt" {
  filename      = "lambda.zip"
  function_name = "convert-jwt"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = filebase64sha256("lambda.zip")

  runtime = "python3.9"
}
