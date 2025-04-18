resource "aws_api_gateway_rest_api" "api" {
  name = "get-cookies"
}

data "aws_iam_policy_document" "api" {
  statement {
    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = ["execute-api:Invoke"]

    resources = ["${aws_api_gateway_rest_api.api.execution_arn}/*"]

    condition {
      test     = "IpAddress"
      variable = "aws:SourceIp"

      values = local.cloudflare_ips
    }
  }
}

resource "aws_api_gateway_rest_api_policy" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  policy      = data.aws_iam_policy_document.api.json
}

resource "aws_api_gateway_resource" "api" {
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "cookies"
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "api" {
  http_method   = "GET"
  authorization = "NONE" #tfsec:ignore:aws-api-gateway-no-public-access
  resource_id   = aws_api_gateway_resource.api.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_integration" "api" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.api.id
  http_method             = aws_api_gateway_method.api.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_cookies.invoke_arn
}

resource "aws_api_gateway_deployment" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.api,
      aws_api_gateway_method.api,
      aws_api_gateway_integration.api,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id        = aws_api_gateway_deployment.api.id
  rest_api_id          = aws_api_gateway_rest_api.api.id
  stage_name           = "prod"
  xray_tracing_enabled = true
}

resource "aws_api_gateway_base_path_mapping" "api" {
  api_id      = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.prod.stage_name
  domain_name = data.terraform_remote_state.cloudsetup.outputs.api_mdekort_domain_name
}
