resource "aws_ssm_parameter" "private_subnet_ids" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/private-subnet-ids"
  type  = "StringList"
  value = join(",", [aws_subnet.private_a.id, aws_subnet.private_b.id])
  tags  = local.common_tags
}

resource "aws_ssm_parameter" "public_subnet_ids" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/public-subnet-ids"
  type  = "StringList"
  value = join(",", [aws_subnet.public_a.id, aws_subnet.public_b.id])
  tags  = local.common_tags
}

resource "aws_ssm_parameter" "vpc_id" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/vpc-id"
  type  = "String"
  value = aws_vpc.vpc.id
  tags  = local.common_tags
}

resource "aws_ssm_parameter" "vpc_cidr_block" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/vpc-cidr-block"
  type  = "String"
  value = var.vpc_cidr
  tags  = local.common_tags
}