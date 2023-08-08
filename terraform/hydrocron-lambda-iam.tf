#IAM roles

resource "aws_iam_instance_profile" "hydrocron-service-profile" {
  name = "${local.ec2_resources_name}-instance-profile"
  role = aws_iam_role.hydrocron-service-role.name
}

resource "aws_iam_policy_attachment" "hydrocron-service-attach" {
  name       = "${local.ec2_resources_name}-attachment"
  roles      = [aws_iam_role.hydrocron-service-role.id]
  policy_arn = aws_iam_policy.hydrocron-service-policy.arn
}
