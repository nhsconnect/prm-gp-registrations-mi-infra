resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 0)
  availability_zone = local.az_names[0]

  tags = merge(
  local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-public"
    }
  )
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vpc.id
  tags = merge(
  local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-public"
    }
  )
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  gateway_id             = aws_internet_gateway.internet_gateway.id
  destination_cidr_block = "0.0.0.0/0"
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

//TODO: Do we need this?
//resource "aws_eip" "nat" {
//  vpc = true
//
//  tags = merge(
//  local.common_tags,
//    {
//      Name = "${var.environment}-gp-registrations-mi-nat"
//    }
//  )
//}
//
//resource "aws_nat_gateway" "nat_gateway" {
//  allocation_id = aws_eip.nat.id
//  subnet_id     = aws_subnet.public.id
//
//  tags = merge(
//  local.common_tags,
//    {
//      Name = "${var.environment}-gp-registrations-mi"
//    }
//  )
//}