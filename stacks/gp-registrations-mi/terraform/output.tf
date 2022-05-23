resource "aws_ssm_parameter" "mi_output_bucket_name" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/output-bucket-name"
  type  = "String"
  value = aws_s3_bucket.mi_output.bucket
  tags  = local.common_tags
}