terraform {
  required_version = "~> 1.10"

  backend "s3" {
    bucket       = "mdekort.tfstate"
    key          = "get-cookies.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.8.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 3.4.0"
    }
  }
}

provider "aws" {}

provider "tls" {}
