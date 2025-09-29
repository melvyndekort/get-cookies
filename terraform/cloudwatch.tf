resource "aws_cloudwatch_log_group" "get_cookies" {
  name              = "/aws/lambda/get-cookies"
  retention_in_days = 3

  tags = {
    Environment = "production"
    Application = "get-cookies"
  }
}
