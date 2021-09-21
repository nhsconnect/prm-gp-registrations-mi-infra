resource "aws_security_group" "inbound_only" {
  name   = "${var.environment}-inbound-only"
  vpc_id = aws_ssm_parameter.vpc_id.value

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-inbound-only"
    }
  )
}

resource "aws_security_group_rule" "inbound_only" {
  type              = "ingress"
  security_group_id = aws_security_group.inbound_only.id
  cidr_blocks       = [aws_ssm_parameter.vpc_cidr_block.value]
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  description       = "TLS from VPC"
}