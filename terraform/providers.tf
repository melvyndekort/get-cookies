terraform {
  required_version = "~> 1.5.0"

  cloud {
    organization = "melvyndekort"

    workspaces {
      name = "get-cookies"
    }
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
