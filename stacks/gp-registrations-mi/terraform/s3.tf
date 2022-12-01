resource "aws_s3_bucket" "mi_events" {
  bucket = "prm-gp-registrations-mi-events-${var.environment}"

  lifecycle {
    prevent_destroy = true
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-prm-gp-registrations-mi-s3-mi-events"
    }
  )
}

resource "aws_s3_bucket_acl" "mi_events" {
  bucket = aws_s3_bucket.mi_events.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "mi_events" {
  bucket = aws_s3_bucket.mi_events.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mi_events" {
  bucket = aws_s3_bucket.mi_events.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}