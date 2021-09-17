resource "aws_ecr_repository" "gp_registrations_mi" {
  name = "registrations/${var.environment}/gp-registrations-mi/gp-registrations-mi"
  tags = {
    Name      = "GP Registrations MI"
    CreatedBy = var.repo_name
    Team      = var.team
  }
}