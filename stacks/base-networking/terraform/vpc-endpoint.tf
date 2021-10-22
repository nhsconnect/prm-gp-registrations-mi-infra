data "aws_region" "current" {}

data "aws_ssm_parameter" "mi_output_bucket_write_access_policy" {
  name = var.mi_output_bucket_write_access_policy
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.vpc.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"
  policy = data.aws_ssm_parameter.mi_output_bucket_write_access_policy.value

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
    }
  )
}

resource "aws_vpc_endpoint_route_table_association" "vpc_endpoint_association" {
  route_table_id  = aws_route_table.private.id
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
}
