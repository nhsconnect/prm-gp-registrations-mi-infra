resource "aws_dynamodb_table" "mi_api_icb_ods" {
  name                        = "${var.environment}_mi_enrichment_icb_ods"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = true
  hash_key                    = "IcbOdsCode"

  attribute {
    name = "IcbOdsCode"
    type = "S"
  }


  import_table {
    input_format           = "CSV"
    input_compression_type = "NONE"
    s3_bucket_source {
      bucket     = aws_s3_bucket.ods_csv_files.id
      key_prefix = aws_s3_object.initial_icb_ods_csv.key
    }

    input_format_options {
      csv {
        delimiter = ","
      }
    }
  }

  tags = {
    Name        = "mi_enrichment_icb_ods"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "dynamodb_policy_icb_ods_enrichment_lambda" {
  name = "dynamodb_${aws_dynamodb_table.mi_api_icb_ods.name}_enrichment_lambda_policy"
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
          aws_dynamodb_table.mi_api_icb_ods.arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_policy_bulk_icb_ods_data_lambda" {
  name = "dynamodb_${aws_dynamodb_table.mi_api_icb_ods.name}_bulk_update_lambda_policy"
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
          aws_dynamodb_table.mi_api_icb_ods.arn
        ]
      }
    ]
  })
}