resource "aws_apigatewayv2_api" "convert_jwt" {
  name          = "convert-jwt"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "convert_jwt" {
  api_id           = aws_apigatewayv2_api.convert_jwt.id
  integration_type = "AWS"

  connection_type           = "INTERNET"
  content_handling_strategy = "CONVERT_TO_TEXT"
  description               = "Convert a JWT token to a Cloudfront signed cookie"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.convert_jwt.invoke_arn
  passthrough_behavior      = "WHEN_NO_MATCH"
}

data "aws_route53_zone" "melvyn_dev" {
  name = "melvyn.dev"
}

resource "aws_acm_certificate" "auth" {
  domain_name       = "auth.melvyn.dev"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "auth_cert_validate" {
  for_each = {
    for dvo in aws_acm_certificate.auth.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.melvyn_dev.zone_id
}

resource "aws_apigatewayv2_domain_name" "auth" {
  domain_name = "auth.melvyn.dev"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.auth.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_route53_record" "auth" {
  name    = aws_apigatewayv2_domain_name.auth.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.melvyn_dev.zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.auth.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.auth.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}