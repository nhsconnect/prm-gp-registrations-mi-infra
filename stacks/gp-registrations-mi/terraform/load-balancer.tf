data "aws_ssm_parameter" "public_subnet_ids" {
  name = var.public_subnet_ids_param_name
}

data "aws_ssm_parameter" "vpc_id" {
  name = var.vpc_id_param_name
}

data "aws_ssm_parameter" "vpc_cidr_block" {
  name = var.vpc_cidr_block_param_name
}

resource "aws_lb" "alb" {
  name               = "${var.environment}-gp-registrations-mi-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.mi_alb.id]
  subnets            = split(",", data.aws_ssm_parameter.public_subnet_ids.value)

  enable_deletion_protection = false

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-alb"
    }
  )
}

resource "aws_lb_target_group" "alb" {
  name        = "${var.environment}-gp-registrations-mi-lb-tg"
  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_ssm_parameter.vpc_id.value
  health_check {
    path = "/actuator/health"
  }
}

resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.alb.id
  port              = 443
  protocol          = "HTTPS"

  certificate_arn = aws_acm_certificate_validation.gp-registrations-mi-cert-validation.certificate_arn

  default_action {
    target_group_arn = aws_lb_target_group.alb.id
    type             = "forward"
  }
}

resource "aws_acm_certificate" "gp-registrations-mi-cert" {
  domain_name = "dev-gp-registrations-mi-alb-783279340.eu-west-2.elb.amazonaws.com"

  validation_method = "DNS"

  tags = {
    CreatedBy   = var.repo_name
    Environment = var.environment
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "gp-registrations-mi-cert-validation" {
  certificate_arn = aws_acm_certificate.gp-registrations-mi-cert.arn
}