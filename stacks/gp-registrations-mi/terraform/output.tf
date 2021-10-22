resource "aws_ssm_parameter" "mi_output_bucket_arn" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/mi-output-bucket-arn"
  type  = "String"
  value = aws_s3_bucket.mi_output.arn
  tags  = local.common_tags
}