
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

#Security Groups

## Application Lambda Security Group
resource "aws_security_group" "service-app-sg" {
  description = "controls access to the lambda Application"
  vpc_id = var.vpc_id
  name   = "${local.ec2_resources_name}-sg"

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
}

## Allow ingress from the lambda security group to the database security group
resource "aws_security_group_rule" "allow_app_in" {
  type        = "ingress"
  security_group_id = data.aws_ssm_parameter.hydrocron-db-sg.value
  protocol    = "tcp"
  from_port   = 3306
  to_port     = 3306
  source_security_group_id = aws_security_group.service-app-sg.id
}

# Lambda Function for the last stable pre-1.0 release of the API. This function is intended to be temprorary
# and should be removed once clients have moved off of this version (primarily, earthdata search client)
resource "aws_lambda_function" "hydrocron_api_lambda_0_2_1" {
  function_name = "${local.ec2_resources_name}-0_2_1"
  role          = aws_iam_role.hydrocron-service-role.arn
  package_type = "Image"
  image_uri     = "${local.account_id}.dkr.ecr.us-west-2.amazonaws.com/podaac/podaac-cloud/podaac-hydrocron:0.2.1"
  timeout       = 5

  vpc_config {
    subnet_ids = var.private_subnets
    security_group_ids = [aws_security_group.service-app-sg.id]
  }

  environment {
    variables = {
      DB_HOST=data.aws_ssm_parameter.hydrocron-db-host.value
      DB_NAME=data.aws_ssm_parameter.hydrocron-db-name.value
      DB_USERNAME=data.aws_ssm_parameter.hydrocron-db-user.value
      DB_PASSWORD_SSM_NAME=data.aws_ssm_parameter.hydrocron-db-user-pass.name
    }
  }

  tags = merge(local.default_tags, {
        "Version": "0.2.1"
    })
}

resource "aws_lambda_permission" "allow_hydrocron_0_2_1" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hydrocron_api_lambda_0_2_1.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.hydrocron-api-gateway.execution_arn}/*/*/*"
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

resource "aws_lambda_function" "hydrocron_api_lambdav1" {
  function_name = "${local.ec2_resources_name}-function"
  role          = aws_iam_role.hydrocron-service-role.arn
  package_type = "Image"
  image_uri     = "${local.account_id}.dkr.ecr.us-west-2.amazonaws.com/${var.docker_tag}"
  timeout       = 5

  vpc_config {
    subnet_ids = var.private_subnets
    security_group_ids = [aws_security_group.service-app-sg.id]
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
  function_name = aws_lambda_function.hydrocron_api_lambdav1.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.hydrocron-api-gateway.execution_arn}/*/*/*"
}




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

#########################
# CodeBuild functionality
#########################

#CodeBuild IAM role

resource "aws_iam_role" "hydrocron-codebuild-iam" {
  name = "hydrocron-codebuild"

  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "hydrocron-codebuild-policy" {
  role = aws_iam_role.hydrocron-codebuild-iam.name


  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudWatchLogsPolicy",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "ssm:GetParameters",
                "ssm:GetParameter"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "CodeCommitPolicy",
            "Effect": "Allow",
            "Action": [
                "codecommit:GitPull"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "S3GetObjectPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:List*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "S3PutObjectPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterfacePermission",
                "ec2:CreateNetworkInterface",
                "ec2:DescribeDhcpOptions",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeVpcs"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws:codebuild:us-west-2:206226843404:project/*"
            ],
            "Action": [
                "codebuild:StartBuild",
                "codebuild:BatchGetBuilds",
                "codebuild:BatchGetProjects"
            ]
        }
    ]
}
POLICY
}

#CodeBuild Project

resource "aws_codebuild_project" "hydrocron" {
  name          = "Hydrocron"
  description   = "Hydrocron Postman Testing"
  build_timeout = "60"
  service_role  = aws_iam_role.hydrocron-codebuild-iam.arn

  artifacts {
    packaging = "NONE"
    name = "hydrocron-reports"
    namespace_type = "BUILD_ID"
    encryption_disabled = false
    location = "podaac-services-${var.stage}-deploy"
    path = "internal/hydrocron/test-reports"
    type = "S3"
  }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode = false
    image = "aws/codebuild/standard:3.0"
    type = "LINUX_CONTAINER"
  }

  logs_config {
    cloudwatch_logs {
      status = "ENABLED"
      group_name = "codeBuild"
      stream_name = "Hydrocron"
    }

    s3_logs {
      status = "DISABLED"
    }
  }

  source {
    insecure_ssl = false
    type = "S3"
    location = "podaac-services-${var.stage}-deploy/internal/hydrocron/"
  }

  vpc_config {
    vpc_id = var.vpc_id

    subnets = var.private_subnets

    security_group_ids = [
      aws_security_group.service-app-sg.id
    ]
  }
}