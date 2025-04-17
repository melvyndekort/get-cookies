data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "get_cookies" {
  name = "get_cookies"
  path = "/lambda/"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "get_cookies" {
  statement {
    actions = [
      "kms:DescribeKey",
      "kms:GenerateDataKey",
      "kms:Decrypt",
    ]

    resources = [
      data.aws_kms_key.generic.arn
    ]
  }

  statement {
    actions = [
      "ssm:GetParameter",
    ]

    resources = [
      aws_ssm_parameter.private_key.arn
    ]
  }

  statement {
    actions = [
      "s3:GetObject",
    ]

    resources = [
      data.terraform_remote_state.cloudsetup.outputs.s3_otel_config_arn
    ]
  }
}

resource "aws_iam_role_policy" "get_cookies" {
  name   = "get_cookies"
  role   = aws_iam_role.get_cookies.id
  policy = data.aws_iam_policy_document.get_cookies.json
}
