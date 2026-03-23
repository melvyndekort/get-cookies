output "public_key_id" {
  value = aws_cloudfront_public_key.public_key.id
}

output "public_key_pem" {
  value = tls_private_key.private_key.public_key_pem
}
