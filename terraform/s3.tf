resource "aws_s3_bucket" "internal" {
   bucket = "${local.ec2_resources_name}-internal"
  force_destroy = true
}

resource "aws_s3_bucket" "public" {
   bucket = "${local.ec2_resources_name}-public"
  force_destroy = true
}

resource "aws_s3_bucket" "private" {
   bucket = "${local.ec2_resources_name}-private"
  force_destroy = true
}

resource "aws_s3_bucket" "protected" {
   bucket = "${local.ec2_resources_name}-protected"
  force_destroy = true
}
