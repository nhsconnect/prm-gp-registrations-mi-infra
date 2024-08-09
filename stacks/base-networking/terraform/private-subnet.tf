resource "aws_subnet" "private_a" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, var.private_cidr_offset)
  availability_zone       = local.az_names[0]
  map_public_ip_on_launch = false
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-private-a"
      ApplicationRole = "AwsSubnet"
    }
  )
}

resource "aws_subnet" "private_b" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, var.private_cidr_offset + 1)
  availability_zone       = local.az_names[1]
  map_public_ip_on_launch = false
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-private-b"
      ApplicationRole = "AwsSubnet"
    }
  )
}

resource "aws_route" "private" {
  route_table_id         = aws_route_table.private.id
  nat_gateway_id         = aws_nat_gateway.nat_gateway.id
  destination_cidr_block = "0.0.0.0/0"
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.vpc.id
  tags = merge(
    local.common_tags, {
      Name            = "${var.environment}-gp-registrations-mi-private"
      ApplicationRole = "AwsRouteTable"
    }
  )
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}
