resource "aws_ssm_parameter" "private_subnet_id" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/private-subnet-id"
  type  = "String"
  value = aws_subnet.private.id
  tags  = local.common_tags
}
