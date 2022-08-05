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

variable "private_subnet_ids_param_name" {
  type        = string
  description = "List of private subnet IDs"
}

variable "vpc_id_param_name" {
  type        = string
  description = "VPC ID"
}

variable "vpc_cidr_block_param_name" {
  type        = string
  description = "VPC CIDR block"
}

variable "ecs_cluster_arn_param_name" {
  type        = string
  description = "ECS cluster arn"
}

variable "apigee_ips_param_name" {
  type        = string
  description = "Apigee IPs"
}

variable "retention_period_in_days" {
  type        = number
  default     = 120
  description = "The number of days for cloudwatch logs retention period"
}

locals {
  api_stage_name = "${var.environment}-env"
}

variable "splunk_cloud_url_param_name" {
  type        = string
  description = "SSM param containing splunk cloud url to send MI events to"
}

variable "splunk_cloud_api_token_param_name" {
  type        = string
  description = "SSM param containing splunk cloud api token to send MI events to"
}