terraform {
  required_version = "~> 1.5.0"

  backend "s3" {
    bucket = "mdekort.tfstate"
    key    = "get-cookies.tfstate"
    region = "eu-west-1"
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
