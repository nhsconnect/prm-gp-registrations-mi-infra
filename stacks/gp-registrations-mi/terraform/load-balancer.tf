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
  security_groups    = [aws_security_group.inbound_only.id]
  subnets            = aws_ssm_parameter.public_subnet_ids.value

  enable_deletion_protection = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-alb"
    }
  )
}

resource "aws_lb_target_group" "alb" {
  name     = "${var.environment}-gp-registrations-mi-alb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_ssm_parameter.vpc_id.value
}

resource "aws_alb_listener" "http_listener" {
  load_balancer_arn = aws_lb.alb.id
  port              = 80
  protocol          = "HTTP"
 
  default_action {
    target_group_arn = aws_alb_target_group.alb.id
    type             = "forward"
  }
}