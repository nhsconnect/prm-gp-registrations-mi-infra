resource "aws_s3_bucket" "ods-csv-files-bucket" {
  bucket        = "${terraform.workspace}-ods-csv-files"
  force_destroy = true

  tags = {
    Name        = "${terraform.workspace}-ods-csv-files"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "mi_events_lifecycle" {
  bucket = aws_s3_bucket.mi_events_output.id

  rule {
    id = "expire-ods-csv-after-3-months"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_public_access_block" "ods-csv-files-bucket_output" {
  bucket = aws_s3_bucket.ods-csv-files-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "mi_events_output" {
  bucket = aws_s3_bucket.ods-csv-files-bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership" {
  bucket = aws_s3_bucket.ods-csv-files-bucket.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket     = aws_s3_bucket.ods-csv-files-bucket.id
  acl        = "private"
}

resource "aws_iam_policy" "s3_ods_csv_document_data_policy" {
  name = "${terraform.workspace}_${aws_s3_bucket.ods-csv-files-bucket.bucket}_get_document_data_policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject",
          "s3:PutObject",
        ],
        "Resource" : ["${aws_s3_bucket.ods-csv-files-bucket}/*"]
      }
    ]
  })
}
