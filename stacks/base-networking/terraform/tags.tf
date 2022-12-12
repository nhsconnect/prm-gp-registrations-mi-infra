locals {
  common_tags = {
    CreatedBy   = var.repo_name
    Environment = var.environment
    envtype = var.environment
    Team        = var.team
  }
}