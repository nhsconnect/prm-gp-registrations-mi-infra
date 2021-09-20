variable "environment" {
  type        = string
  description = "Uniquely identities each deployment, i.e. dev, prod."
}

variable "team" {
  type        = string
  default     = "Registrations"
  description = "Team owning this resource"
}

variable "repo_name" {
  type        = string
  default     = "prm-gp-registrations-mi-infra"
  description = "Name of this repository"
}

variable "gp_registrations_mi_repo_param_name" {
  type        = string
  description = "Docker repository of the gp registrations MI API"
}

variable "execution_role_arn_param_name" {
  type        = string
  description = "SSM parameter containing ecs execution role arn"
}

variable "gp_registrations_mi_image_tag" {
  type        = string
  description = "Docker image tag of the gp registrations MI API"
}

variable "log_group_param_name" {
  type        = string
  description = "Cloudwatch log group for gp registrations MI API"
}