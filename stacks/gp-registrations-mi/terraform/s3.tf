resource "aws_s3_bucket" "mi_output" {
  bucket = "prm-gp-registrations-mi-events-${var.environment}"
  acl    = "private"

  tags = merge(
    local.common_tags,
    {
      Name = "Output from GP Registrations MI API"
    }
  )
}

resource "aws_s3_bucket_public_access_block" "mi_output" {
  bucket = aws_s3_bucket.mi_output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}