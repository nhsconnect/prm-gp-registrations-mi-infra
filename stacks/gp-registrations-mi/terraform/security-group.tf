resource "aws_security_group" "mi_alb" {
  name   = "${var.environment}-mi-alb"
  vpc_id = data.aws_ssm_parameter.vpc_id.value
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-alb"
    }
  )
}

resource "aws_security_group_rule" "alb_outbound" {
  type              = "egress"
  security_group_id = aws_security_group.mi_alb.id
  source_security_group_id = aws_security_group.gp_registrations_mi_container.id
  from_port         = 8080
  to_port           = 8080
  protocol          = "tcp"
  description       = "Allow alb to talk to the container"
}

resource "aws_security_group" "gp_registrations_mi_container" {
  name   = "${var.environment}-gp-registrations-mi-container"
  vpc_id = data.aws_ssm_parameter.vpc_id.value
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-container"
    }
  )
}

resource "aws_security_group_rule" "mi_container_inbound" {
  type                     = "ingress"
  security_group_id        = aws_security_group.gp_registrations_mi_container.id
  source_security_group_id = aws_security_group.mi_alb.id
  from_port                = 0
  to_port                  = 8080
  protocol                 = "tcp"
  description              = "Allow inbound traffic from load balancer"
}

resource "aws_security_group_rule" "mi_container_outbound" {
  type                     = "egress"
  security_group_id        = aws_security_group.gp_registrations_mi_container.id
  cidr_blocks              = ["0.0.0.0/0"]
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  description              = "Allow all outbound"
}