data "aws_lb" "alb" {
  name = var.load_balancer_name
}


data "aws_security_group" "alb_sg" {
  name = var.load_balancer_sg_name
}

data "aws_acm_certificate" "issued" {
  domain = local.certificate_name
}

resource "aws_lb_listener" "hydrocron_api_alb_listener" {
  load_balancer_arn = data.aws_lb.alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = data.aws_acm_certificate.issued.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fargate_service_tg.arn
  }
}

resource "aws_lb_target_group" "fargate_service_tg" {
  name        = "${local.ec2_resources_name}-tg"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.default.id

  health_check {
    path    = "/hydrocron/api/session/user"
    matcher = "200-299"
  }
}
