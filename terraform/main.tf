
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

resource "random_pet" "this" {
  length = 2
}

module "dynamodb_table" {
  source = "../../"

  name                        = "my-table-${random_pet.this.id}"
  hash_key                    = "id"
  range_key                   = "title"
  table_class                 = "STANDARD"
  deletion_protection_enabled = false

  attributes = [
    {
      name = "id"
      type = "N"
    },
    {
      name = "title"
      type = "S"
    },
    {
      name = "feature_id"
      type = "N"
    }
  ]

  global_secondary_indexes = [
    {
      name               = "TitleIndex"
      hash_key           = "title"
      range_key          = "feature_id"
      projection_type    = "INCLUDE"
      non_key_attributes = ["id"]
    }
  ]

  tags = {
    Terraform   = "true"
    Environment = "staging"
  }
}


module "disabled_dynamodb_table" {
  source = "../../"

  create_table = false
}