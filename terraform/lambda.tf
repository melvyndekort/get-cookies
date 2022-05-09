resource "aws_lambda_function" "test_lambda" {
  filename      = "lambda.zip"
  function_name = "lambda_function_name"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "index.test"

  source_code_hash = filebase64sha256("lambda.zip")

  runtime = "nodejs12.x"
}
