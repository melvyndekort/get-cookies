resource "aws_apigatewayv2_api" "auth" {
  name          = "AuthAPI"
  protocol_type = "HTTP"

  cors_configuration {
    allow_methods = ["GET", "OPTIONS"]
    allow_origins = [
      "https://example.melvyn.dev",
    ]
  }
}

resource "aws_apigatewayv2_integration" "auth" {
  api_id                 = aws_apigatewayv2_api.auth.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.convert_jwt.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "auth" {
  api_id    = aws_apigatewayv2_api.auth.id
  route_key = "GET /auth"
  target    = "integrations/${aws_apigatewayv2_integration.auth.id}"
}

resource "aws_cloudwatch_log_group" "auth" {
  name              = "/aws/apigateway/AuthAPI"
  retention_in_days = 14
}

resource "aws_apigatewayv2_stage" "auth" {
  api_id      = aws_apigatewayv2_api.auth.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.auth.arn
    format = jsonencode({
  "requestId":               "$context.requestId",
  "extendedRequestId":       "$context.extendedRequestId",
  "ip":                      "$context.identity.sourceIp",
  "caller":                  "$context.identity.caller",
  "user":                    "$context.identity.user",
  "requestTime":             "$context.requestTime",
  "httpMethod":              "$context.httpMethod",
  "resourcePath":            "$context.resourcePath",
  "routeKey":                "$context.routeKey",
  "status":                  "$context.status",
  "protocol":                "$context.protocol",
  "responseLength":          "$context.responseLength",
  "integrationErrorMessage": "$context.integrationErrorMessage"
})
  }
}

resource "aws_apigatewayv2_domain_name" "api" {
  domain_name = "api.melvyn.dev"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate_validation.api.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "auth" {
  api_id      = aws_apigatewayv2_api.auth.id
  domain_name = aws_apigatewayv2_domain_name.api.id
  stage       = aws_apigatewayv2_stage.auth.id
}
