resource "aws_s3_bucket" "mi_output" {
  bucket = "prm-gp-registrations-mi-events-${var.environment}"
  acl    = "private"

  lifecycle {
    prevent_destroy = true
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Output from GP Registrations MI API"
    }
  )
}

resource "aws_s3_bucket_acl" "mi_output" {
  bucket = aws_s3_bucket.mi_output.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "mi_output" {
  bucket = aws_s3_bucket.mi_output.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_kms_key" "mi_output" {
  description             = "Key used to encrypt MI bucket objects"
  deletion_window_in_days = 10
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mi_output" {
  bucket = aws_s3_bucket.mi_output.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mi_output.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "mi_output" {
  bucket = aws_s3_bucket.mi_output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}