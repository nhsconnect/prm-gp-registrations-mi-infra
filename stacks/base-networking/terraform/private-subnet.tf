resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, var.private_cidr_offset)
  availability_zone       = local.az_names[0]
  map_public_ip_on_launch = false
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-private"

    }
  )
}

// TODO: Connect private to public subnet
//resource "aws_route" "private" {
//  route_table_id         = aws_route_table.private.id
////  nat_gateway_id         = aws_nat_gateway.nat_gateway.id
//  destination_cidr_block = "0.0.0.0/0"
//}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name        = "${var.environment}-gp-registrations-mi-private"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}