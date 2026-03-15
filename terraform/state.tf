data "terraform_remote_state" "tf_aws" {
  backend = "s3"

  config = {
    bucket = "mdekort-tfstate-075673041815"
    key    = "tf-aws.tfstate"
    region = "eu-west-1"
  }
}

data "terraform_remote_state" "tf_cognito" {
  backend = "s3"

  config = {
    bucket = "mdekort-tfstate-075673041815"
    key    = "tf-cognito.tfstate"
    region = "eu-west-1"
  }
}
