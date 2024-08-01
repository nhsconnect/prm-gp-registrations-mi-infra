resource "aws_dynamodb_table" "mi_api_gp_ods" {
  name                        = "${var.environment}_mi_enrichment_practice_ods"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = true

  hash_key = "PracticeOdsCode"

  attribute {
    name = "PracticeOdsCode"
    type = "S"
  }

  tags = {
    Name        = "mi_enrichment_practice_ods"
    Environment = var.environment
  }

  import_table {
    input_format           = "CSV"
    input_compression_type = "NONE"
    s3_bucket_source {
      bucket     = aws_s3_bucket.ods_csv_files.id
      key_prefix = aws_s3_object.initial_gp_ods_csv.key
    }
    input_format_options {
      csv {
        delimiter   = ","
        header_list = ["PracticeOdsCode", "PracticeName", "IcbOdsCode"]
      }
    }
  }
}

resource "aws_iam_policy" "dynamodb_policy_ods_enrichment_lambda" {
  name = "${var.environment}_${aws_dynamodb_table.mi_api_gp_ods.name}_policy"
  path = "/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:PutItem",
        ],
        "Resource" : [
          aws_dynamodb_table.mi_api_gp_ods.arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_policy_bulk_ods_data_lambda" {
  name = "${var.environment}_mi_bulk_ods_policy"
  path = "/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:UpdateItem",
        ],
        "Resource" : [
          aws_dynamodb_table.mi_api_gp_ods.arn
        ]
      }
    ]
  })
}