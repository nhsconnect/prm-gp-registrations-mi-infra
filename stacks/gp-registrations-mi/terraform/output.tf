resource "aws_ssm_parameter" "mi_output_bucket_write_access_policy" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/mi-output-bucket-write-access-policy"
  type  = "String"
  value = aws_iam_policy.mi_output_bucket_write_access.policy
  tags  = local.common_tags
}