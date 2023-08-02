#----- Fargate Task Execution Role --------
resource "aws_iam_role" "fargate_task_execution_role" {
  name                 = "${local.ec2_resources_name}-fargate-task-execution-role"
  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  tags                 = local.default_tags
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}


resource "aws_iam_role_policy" "fargate_policy" {
  name = "${local.ec2_resources_name}-fargate-policy"
  role = aws_iam_role.fargate_task_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "ssm:GetParameter",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "ssm:GetParameters"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket*"
        ]
        Resource = [
          "arn:aws:s3:::podaac-services-${var.stage}-deploy",
          "arn:aws:s3:::podaac-services-${var.stage}-deploy/*"
        ]
      }
    ]
  })
}

#----- Fargate Task Role--------
resource "aws_iam_role" "ecs_task_role" {
  name                 = "${local.ec2_resources_name}-fargate-task-role"
  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  tags                 = local.default_tags
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name = "${local.ec2_resources_name}-fargate-task-role-policy"
  role = aws_iam_role.ecs_task_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:Get*",
          "s3:List*"
        ]
        Resource = [
          "arn:aws:s3:::podaac-services-${var.stage}-deploy",
          "arn:aws:s3:::podaac-services-${var.stage}-deploy/*"
        ]
      }
    ]
  })
}


#----- CloudWatch Events - Role Management--------
resource "aws_iam_role" "cloudwatch_events_role" {
  name                 = "${local.ec2_resources_name}-fargate-task-events"
  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  tags                 = local.default_tags
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}

data "aws_iam_policy_document" "cloudwatch_events_role_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "cloudwatch_events_role_run_task" {
  name   = "${aws_ecs_task_definition.fargate_task.family}-events-ecs"
  role   = aws_iam_role.cloudwatch_events_role.id
  policy = data.aws_iam_policy_document.cloudwatch_events_role_run_task_policy.json
}

data "aws_iam_policy_document" "cloudwatch_events_role_run_task_policy" {
  statement {
    effect    = "Allow"
    actions   = ["ecs:RunTask"]
    resources = ["arn:aws:ecs:${var.region}:${data.aws_caller_identity.current.account_id}:task-definition/${aws_ecs_task_definition.fargate_task.family}:*"]

    condition {
      test     = "StringLike"
      variable = "ecs:cluster"
      values   = [aws_ecs_cluster.fargate_cluster.arn]
    }
  }
}

resource "aws_iam_role_policy" "cloudwatch_events_role_pass_role" {
  name   = "${aws_ecs_task_definition.fargate_task.family}-events-ecs-pass-role"
  role   = aws_iam_role.cloudwatch_events_role.id
  policy = data.aws_iam_policy_document.cloudwatch_events_role_pass_role_policy.json
}

data "aws_iam_policy_document" "cloudwatch_events_role_pass_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["iam:PassRole"]

    resources = [
      aws_iam_role.fargate_task_execution_role.arn,
      aws_iam_role.ecs_task_role.arn,
    ]
  }
}
