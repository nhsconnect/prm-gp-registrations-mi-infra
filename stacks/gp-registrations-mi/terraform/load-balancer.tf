data "aws_ssm_parameter" "vpc_id" {
  name = var.vpc_id_param_name
}

data "aws_ssm_parameter" "vpc_cidr_block" {
  name = var.vpc_cidr_block_param_name
}

resource "aws_lb" "nlb" {
  name               = "${var.environment}-gp-registrations-mi-nlb"
  internal           = true
  load_balancer_type = "network"
  subnets            = split(",", data.aws_ssm_parameter.private_subnet_ids.value)

  enable_deletion_protection       = true
  enable_cross_zone_load_balancing = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-nlb"
    }
  )
}

resource "aws_lb_target_group" "nlb" {
  depends_on = [
    aws_lb.nlb
  ]
  name        = "${var.environment}-gp-registrations-mi-nlb-tg"
  port        = 8080
  protocol    = "TCP"
  target_type = "ip"
  vpc_id      = data.aws_ssm_parameter.vpc_id.value
  health_check {
    path = "/_status"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-nlb-tg"
    }
  )
}

resource "aws_lb_listener" "nlb_listener" {
  load_balancer_arn = aws_lb.nlb.id
  port              = 80
  protocol          = "TCP"
  default_action {
    target_group_arn = aws_lb_target_group.nlb.id
    type             = "forward"
  }
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-nlb-listener"
    }
  )
}