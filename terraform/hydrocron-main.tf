# API Gateway
resource "aws_api_gateway_rest_api" "hydrocron-api-gateway" {
  name        = "${local.ec2_resources_name}-api-gateway"
  description = "API to access Hydrocron"
  body        = templatefile(
                  "${path.module}/api-specification-templates/hydrocron_aws_api.yml",
                  {
                    vpc_id = var.vpc_id
                  })
  parameters = {
    "basemap" = "split"
  }
  endpoint_configuration {
    types = ["PRIVATE"]
  }
  lifecycle {
    prevent_destroy = true
  }
}
