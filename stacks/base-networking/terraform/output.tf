resource "aws_ssm_parameter" "private_subnet_ids" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/private-subnet-ids"
  type  = "StringList"
  value = join(",", [aws_subnet.private_a.id, aws_subnet.private_b.id])
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-private-subnet-ids"
      ApplicationRole = "AwsSsmParameter"
    }
  )
}

resource "aws_ssm_parameter" "vpc_id" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/vpc-id"
  type  = "String"
  value = aws_vpc.vpc.id
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-vpc-id"
      ApplicationRole = "AwsSsmParameter"
    }
  )
}

resource "aws_ssm_parameter" "vpc_cidr_block" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/base-networking/vpc-cidr-block"
  type  = "String"
  value = var.vpc_cidr
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-vpc-cidr-block"
      ApplicationRole = "AwsSsmParameter"
    }
  )
}
