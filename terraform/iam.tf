data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      aws_cloudwatch_log_group.convert_jwt.arn
    ]
  }

  statement {
    actions = [
      "kms:DescribeKey",
      "kms:GenerateDataKey",
      "kms:Decrypt",
    ]

    resources = [
      data.terraform_remote_state.aws_mdekort.outputs.generic_kms_key_arn
    ]
  }

  statement {
    actions = [
      "ssm:GetParameter",
    ]

    resources = [
      aws_ssm_parameter.cloudfront_signer_key.arn
    ]
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name   = "lambda_policy"
  role   = aws_iam_role.iam_for_lambda.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}
