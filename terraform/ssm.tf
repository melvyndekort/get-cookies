resource "tls_private_key" "private_key" {
  algorithm = "RSA"
}

resource "aws_ssm_parameter" "private_key" {
  name  = "/cloudfront/signer/private_key"
  type  = "SecureString"
  value = tls_private_key.private_key.private_key_pem
}

resource "aws_cloudfront_public_key" "public_key" {
  name        = "cloudfront-auth"
  comment     = "Public key for cloudfront_auth"
  encoded_key = tls_private_key.private_key.public_key_pem
}
