resource "aws_ecr_repository" "gp_registrations_mi" {
  name = "registrations/${var.environment}/gp-registrations-mi/mi-api"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
      ApplicationRole = "AwsEcrRepository"
    }
  )
}
