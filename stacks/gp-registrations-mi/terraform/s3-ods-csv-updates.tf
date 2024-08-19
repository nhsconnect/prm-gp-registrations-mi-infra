resource "aws_s3_bucket" "ods_csv_files" {
  bucket        = "${var.environment}-ods-csv-files"
  force_destroy = true

  tags = {
    Name        = "${var.environment}-ods-csv-files"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ods_csv_files" {
  bucket = aws_s3_bucket.ods_csv_files.id

  rule {
    id     = "expire-ods-csv-after-3-months"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_public_access_block" "ods_csv_files" {
  bucket = aws_s3_bucket.ods_csv_files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "ods_csv_files" {
  bucket = aws_s3_bucket.ods_csv_files.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_ownership_controls" "ods_csv_files" {
  bucket = aws_s3_bucket.ods_csv_files.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "ods_csv_files" {
  bucket     = aws_s3_bucket.ods_csv_files.id
  acl        = "private"
  depends_on = [aws_s3_bucket_ownership_controls.ods_csv_files]
}

resource "aws_iam_policy" "ods_csv_files_data_policy" {
  name = "${aws_s3_bucket.ods_csv_files.bucket}_get_document_data_policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject",
          "s3:PutObject",
        ],
        "Resource" : ["${aws_s3_bucket.ods_csv_files.arn}/*"]
      }
    ]
  })
}

resource "aws_s3_object" "initial_gp_ods_csv" {
  bucket = aws_s3_bucket.ods_csv_files.id
  key    = "init/initial-gps-ods-csv"
  source = "./initial_full_gps_ods.csv"
  lifecycle {
    ignore_changes = all
  }
}


resource "aws_s3_object" "initial_icb_ods_csv" {
  bucket = aws_s3_bucket.ods_csv_files.id
  key    = "init/initial-icb-ods-csv"
  source = "./initial_full_icb_ods.csv"
  lifecycle {
    ignore_changes = all
  }
}