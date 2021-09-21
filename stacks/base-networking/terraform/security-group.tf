resource "aws_security_group" "inbound_only" {
  name   = "${var.environment}-inbound-only"
  vpc_id = aws_vpc.vpc.id

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
  cidr_blocks       = [aws_vpc.vpc.cidr_block]
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  description       = "TLS from VPC"
}