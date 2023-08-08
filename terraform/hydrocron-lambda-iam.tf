#IAM roles

resource "aws_iam_instance_profile" "hydrocron-service-profile" {
  name = "${local.ec2_resources_name}-instance-profile"
  role = aws_iam_role.hydrocron-service-role.name
}

resource "aws_iam_role" "hydrocron-service-role" {
  name = "${local.ec2_resources_name}-service-role"

  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
