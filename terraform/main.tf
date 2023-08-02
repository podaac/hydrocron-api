# configure the S3 backend for storing state. This allows different
# team members to control and update terraform state.
terraform {
  backend "s3" {
    key    = "services/feature-translation-service/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
  shared_credentials_file = var.credentials
  profile = var.profile

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }
}

locals {
  name        = var.app_name
  environment = var.stage

  account_id = data.aws_caller_identity.current.account_id

  # This is the convention we use to know what belongs to each other
  ec2_resources_name = "service-${local.name}-${local.environment}"

  # Used to refer to the HYDROCRON database resources by the same convention
  hydrocrondb_resource_name = "service-${var.db_app_name}-${local.environment}"

  default_tags = length(var.default_tags) == 0 ? {
    team: "TVA",
    application: local.ec2_resources_name,
    Environment = var.stage
    Version = var.docker_tag
  } : var.default_tags
}

data "aws_caller_identity" "current" {}