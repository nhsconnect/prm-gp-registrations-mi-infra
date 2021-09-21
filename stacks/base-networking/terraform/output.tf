resource "aws_ssm_parameter" "private_subnet_ids" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/private-subnet-ids"
  type  = "StringList"
  value = join(",", [aws_subnet.private_a.id, aws_subnet.private_b.id])
  tags  = local.common_tags
}
