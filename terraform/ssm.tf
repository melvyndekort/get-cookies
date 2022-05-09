resource "aws_ssm_parameter" "cloudfront_signer_key" {
  name  = "/cloudfront/signer_key"
  type  = "SecureString"
  value = local.secrets.cloudfront.signer_key
}
