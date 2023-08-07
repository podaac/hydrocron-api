resource "aws_s3_bucket" "internal" {
   bucket = "${local.ec2_resources_name}-internal"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "internal-acl" {
   bucket = aws_s3_bucket.internal.id
   acl = "private"
}

resource "aws_s3_bucket" "public" {
   bucket = "${local.ec2_resources_name}-public"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "public-acl" {
   bucket = aws_s3_bucket.public.id
   acl = "private"
}

resource "aws_s3_bucket" "private" {
   bucket = "${local.ec2_resources_name}-private"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "private-acl" {
   bucket = aws_s3_bucket.private.id
   acl = "private"
}

resource "aws_s3_bucket" "protected" {
   bucket = "${local.ec2_resources_name}-protected"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "protected-acl" {
   bucket = aws_s3_bucket.protected.id
   acl = "private"
}