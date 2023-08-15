
# SSM Parameter values
data "aws_ssm_parameter" "hydrocron-db-user" {
  name = "${local.hydrocrondb_resource_name}-user"
}

data "aws_ssm_parameter" "hydrocron-db-user-pass" {
  name = "${local.hydrocrondb_resource_name}-user-pass"
}

data "aws_ssm_parameter" "hydrocron-db-host" {
  name = "${local.hydrocrondb_resource_name}-host"
}

data "aws_ssm_parameter" "hydrocron-db-name" {
  name = "${local.hydrocrondb_resource_name}-name"
}

data "aws_ssm_parameter" "hydrocron-db-sg" {
  name = "${local.hydrocrondb_resource_name}-sg"
}


resource "aws_api_gateway_deployment" "hydrocron-api-gateway-deployment" {
  rest_api_id = aws_api_gateway_rest_api.hydrocron-api-gateway.id
  stage_name  = "default"
  depends_on = [aws_api_gateway_rest_api.hydrocron-api-gateway]
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.hydrocron-api-gateway.body
    ]))
  }
}

resource "aws_lambda_function" "hydrocron_api_lambda" {
  function_name = "${local.ec2_resources_name}-function"
  filename = "${path.module}/../dist/${local.name}-${local.version}.zip"
  source_code_hash = filebase64sha256("${path.module}/../dist/${local.name}-${local.version}.zip")
  role          = aws_iam_role.hydrocron-service-role.arn
  timeout       = 5
  handler       = "hydrocronapi.controllers.timeseries.lambda_handler"
  runtime       = "python3.8"

  vpc_config {
    subnet_ids = var.private_subnets
    security_group_ids = [var.default_vpc_sg]
  }

  environment {
    variables = {
      DB_HOST=data.aws_ssm_parameter.hydrocron-db-host.value
      DB_NAME=data.aws_ssm_parameter.hydrocron-db-name.value
      DB_USERNAME=data.aws_ssm_parameter.hydrocron-db-user.value
      DB_PASSWORD_SSM_NAME=data.aws_ssm_parameter.hydrocron-db-user-pass.name
    }
  }

  tags = var.default_tags
}

resource "aws_lambda_permission" "allow_hydrocron" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hydrocron_api_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.hydrocron-api-gateway.execution_arn}/*/*/*"
}




#  API Gateway
resource "aws_api_gateway_rest_api" "hydrocron-api-gateway" {
  name        = "${local.ec2_resources_name}-api-gateway"
  description = "API to access Hydrocron"
  body        = templatefile(
                  "${path.module}/api-specification-templates/hydrocron_aws_api.yml",
                  {
                    hydrocronapi_lambda_arn = aws_lambda_function.hydrocron_api_lambda.invoke_arn
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

resource "aws_cloudwatch_log_group" "hydrocron-api-gateway-logs" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.hydrocron-api-gateway.id}/${aws_api_gateway_deployment.hydrocron-api-gateway-deployment.stage_name}"
  retention_in_days = 60
}

output "url" {
  value = "${aws_api_gateway_deployment.hydrocron-api-gateway-deployment.invoke_url}/api"
}

resource "aws_ssm_parameter" "hydrocron-api-url" {
  name  = "hydrocron-api-url"
  type  = "String"
  value = aws_api_gateway_deployment.hydrocron-api-gateway-deployment.invoke_url
  overwrite = true
}
