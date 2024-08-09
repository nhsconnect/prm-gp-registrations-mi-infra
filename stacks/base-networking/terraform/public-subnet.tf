resource "aws_subnet" "public_a" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 0)
  availability_zone = local.az_names[0]

  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-public-a"
      ApplicationRole = "AwsSubnet"
    }
  )
}

resource "aws_subnet" "public_b" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 1)
  availability_zone = local.az_names[1]

  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-public-b"
      ApplicationRole = "AwsSubnet"
    }
  )
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vpc.id
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-public"
      ApplicationRole = "AwsRouteTable"
    }
  )
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  gateway_id             = aws_internet_gateway.internet_gateway.id
  destination_cidr_block = "0.0.0.0/0"
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  vpc = true

  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-nat"
      ApplicationRole = "AwsEip"
    }
  )
}

resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id

  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi-nat-gateway"
      ApplicationRole = "AwsNatGateway"
    }
  )
}