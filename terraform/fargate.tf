


resource "random_string" "session_cookie_secret" {
  length  = 16
  special = true
}

resource "aws_ssm_parameter" "session_cookie_secret" {
  name      = "${local.ec2_resources_name}-session-cookie-secret"
  type      = "SecureString"
  value     = random_string.session_cookie_secret.result
  tags      = local.default_tags
  overwrite = true
}

resource "aws_ssm_parameter" "earth_data_login_password" {
  name      = "${local.ec2_resources_name}-earth-data-login-password"
  type      = "SecureString"
  value     = var.EARTH_DATA_LOGIN_PASSWORD
  tags      = local.default_tags
  overwrite = true
}

resource "aws_security_group" "hydrocron_api" {
  name        = "${local.ec2_resources_name}-sg"
  description = "Control traffic for the hydrocron-api api"
  vpc_id      = data.aws_vpc.default.id

  ingress = [
    {
      description      = "From ALB"
      from_port        = 8080
      to_port          = 8080
      protocol         = "tcp"
      security_groups  = []
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      self : false
    }
  ]

  egress = [
    {
      description      = "Outbound traffic"
      prefix_list_ids  = []
      security_groups  = []
      self             = false
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  ]

  tags = local.default_tags
}


#----- AWS ECS Cluster--------
resource "aws_ecs_cluster" "fargate_cluster" {
  name = "${local.ec2_resources_name}-fargate-cluster"
  tags = local.default_tags
}

#----- ECS  Services--------
resource "aws_cloudwatch_log_group" "fargate_task_log_group" {
  name              = "${local.ec2_resources_name}-fargate-worker"
  retention_in_days = var.logs_retention_days
  tags              = local.default_tags
}

#----- Fargate Task Definition --------
resource "aws_ecs_task_definition" "fargate_task" {
  family                   = "${local.ec2_resources_name}-fargate-task"
  requires_compatibilities = ["FARGATE"]
  container_definitions = jsonencode([
    {
      name    = "${local.ec2_resources_name}-fargate-task"
      image   = var.hydrocron_api_docker_image
      command = ["/bin/bash", "-c", "node mysql/setup-db.js && docker/docker-start-command"]
      secrets = [
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = "${aws_ssm_parameter.db_user_pass.arn}"
        },
        {
          name      = "DATABASE_ADMIN_PASSWORD"
          valueFrom = "${aws_ssm_parameter.db_admin_pass.arn}"
        },
        {
          name  = "EARTH_DATA_LOGIN_PASSWORD"
          valueFrom = "${aws_ssm_parameter.earth_data_login_password.arn}"
        },
        {
          name  = "SESSION_COOKIE_SECRET"
          valueFrom = "${aws_ssm_parameter.session_cookie_secret.arn}"
        }
      ]
      environment = [
        {
          name  = "DATABASE_HOST"
          value = "${aws_ssm_parameter.db_host.value}"
        },
        {
          name  = "DATABASE_PORT"
          value = "3306"
        },
        {
          name  = "DATABASE_NAME"
          value = "${aws_ssm_parameter.db_name.value}"
        },
        {
          name  = "DATABASE_USERNAME"
          value = "${aws_ssm_parameter.db_user.value}"
        },
        {
          name  = "DATABASE_ADMIN"
          value = "${aws_ssm_parameter.db_admin.value}"
        },
        {
          name  = "EARTH_DATA_LOGIN_CLIENT_ID"
          value = "${var.EARTH_DATA_LOGIN_CLIENT_ID}"
        },
        {
          name  = "EARTH_DATA_LOGIN_AUTH_CODE_REQUEST_URI"
          value = "${var.earth_data_login_base_url}/oauth/authorize"
        },
        {
          name  = "EARTH_DATA_LOGIN_TOKEN_REQUEST_URI"
          value = "${var.earth_data_login_base_url}/oauth/token"
        },
        {
          name  = "EARTH_DATA_LOGIN_TOKEN_REFRESH_URI"
          value = "${var.earth_data_login_base_url}/oauth/token"
        },
        {
          name  = "EARTH_DATA_LOGIN_USER_INFO_URI"
          value = "${var.earth_data_login_base_url}"
        },
        {
          name  = "L2SS_SUBSET_SUBMIT_REQUEST_URI"
          value = "${var.l2ss_base_url}/subset/submit"
        },
        {
          name  = "L2SS_SUBSET_STATUS_REQUEST_URI"
          value = "${var.l2ss_base_url}/subset/status"
        },
        {
          name  = "HARMONY_BASE_URL"
          value = "${var.harmony_base_url}"
        },
        {
          name  = "SECURE_COOKIE"
          value = "true"
        },
        {
          name  = "LIST_OF_AUTHORIZED_CORS_REQUESTER_ORIGINS"
          value = "${var.LIST_OF_AUTHORIZED_CORS_REQUESTER_ORIGINS}"
        },
        {
          name  = "NUM_PROXY_SERVERS_FOR_API"
          value = "1"
        }
      ]
      portMappings = [{
        containerPort = 8080
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-region"        = "us-west-2"
          "awslogs-group"         = "${aws_cloudwatch_log_group.fargate_task_log_group.name}"
          "awslogs-stream-prefix" = "${aws_cloudwatch_log_group.fargate_task_log_group.name}"
        }
      }
    }
  ])

  network_mode = "awsvpc"
  cpu          = var.task_cpu
  memory       = var.task_memory

  execution_role_arn = aws_iam_role.fargate_task_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  tags               = local.default_tags
}

resource "aws_ecs_service" "hydrocron_api" {
  name            = "${local.ec2_resources_name}-ecs-service"
  cluster         = aws_ecs_cluster.fargate_cluster.arn
  task_definition = aws_ecs_task_definition.fargate_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets         = data.aws_subnets.private.ids
    security_groups = [aws_ssm_parameter.db_sg.value, aws_security_group.hydrocron_api.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fargate_service_tg.arn
    container_name   = "${local.ec2_resources_name}-fargate-task"
    container_port   = 8080
  }

  tags = local.default_tags

  depends_on = [
    aws_ecs_cluster.fargate_cluster
  ]
}
