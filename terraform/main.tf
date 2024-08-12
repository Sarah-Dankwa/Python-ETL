terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "nc-alapin-project-tf-state"
    key = "nc-alapin-project-tf-state/terraform.tfstate"
    region = "eu-west-2"
  }
}

provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = {
      ProjectName = "Alapin Team Project"
      Team = "Alapin"
      DeployedFrom = "Terraform"
      CostCentre = "DE"
      Environment = "dev"
      RetentionDate = "2024-09-31"
    }
  }
}