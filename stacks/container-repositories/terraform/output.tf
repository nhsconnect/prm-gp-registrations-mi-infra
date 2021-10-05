resource "aws_ssm_parameter" "gp_registrations_mi" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/ecr/url/mi-api"
  type  = "String"
  value = aws_ecr_repository.gp_registrations_mi.repository_url
  tags  = local.common_tags
}
