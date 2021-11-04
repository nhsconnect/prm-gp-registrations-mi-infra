data "aws_ssm_parameter" "apigee_ips" {
  name = var.apigee_ips_param_name
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

resource "aws_security_group_rule" "mi_container_inbound_vpc" {
  type              = "ingress"
  security_group_id = aws_security_group.gp_registrations_mi_container.id
  from_port         = 8080
  to_port           = 8080
  cidr_blocks       = [data.aws_ssm_parameter.vpc_cidr_block.value]
  protocol          = "tcp"
  description       = "Allow inbound traffic from VPC since NLB does not have security groups"
}

resource "aws_security_group_rule" "mi_container_outbound" {
  type              = "egress"
  security_group_id = aws_security_group.gp_registrations_mi_container.id
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  description       = "Allow all outbound"
}