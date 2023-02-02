resource "aws_s3_bucket" "mi_events_output" {
  bucket = "prm-gp-registrations-mi-events-${var.environment}"

  lifecycle {
    prevent_destroy = true
  }

  lifecycle_rule {
    enabled = true
    id      = "expire-mi-objects-after-2-years"

    expiration {
      days = 730
    }
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-prm-gp-registrations-mi-s3-mi-events"
      ApplicationRole = "AwsS3Bucket"
    }
  )
}

resource "aws_s3_bucket_acl" "mi_events_output" {
  bucket = aws_s3_bucket.mi_events_output.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "mi_events_output" {
  bucket = aws_s3_bucket.mi_events_output.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mi_events_output" {
  bucket = aws_s3_bucket.mi_events_output.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "mi_events_output" {
  bucket = aws_s3_bucket.mi_events_output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}