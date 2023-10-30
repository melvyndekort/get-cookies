resource "aws_cognito_user_pool_client" "get_cookies" {
  name         = "get_cookies"
  user_pool_id = data.terraform_remote_state.cloudsetup.outputs.auth_user_pool_id

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["email", "openid"]
  supported_identity_providers         = ["COGNITO"]

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "hours"
  }

  access_token_validity  = 24
  id_token_validity      = 24
  refresh_token_validity = 24

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  callback_urls = [
    "https://example.melvyn.dev/callback.html",
    "https://example.melvyn.dev",
    "https://start.mdekort.nl/callback.html",
    "https://start.mdekort.nl"
  ]
}
