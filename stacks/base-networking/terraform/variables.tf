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

variable "vpc_cidr" {
  type        = string
  description = "CIDR block to assign VPC"
}

variable "private_cidr_offset" {
  type        = number
  description = "CIDR address offset to begin creating private subnets at"
  default     = 100
}

variable "mi_output_bucket_write_access_policy" {
  type        = string
  description = "MI Output S3 bucket write access only IAM policy"
}