resource "aws_dynamodb_table" "mi_api_icb_ods" {
  name                        = "${var.environment}_mi_enrichment_icb_ods"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = false
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
      key_prefix = aws_s3_object.initial_icb_ods.key
    }

    input_format_options {
      csv {
        delimiter   = ","
        header_list = ["IcbOdsCode", "IcbName"]
      }
    }
  }

  tags = {
    Name        = "mi_enrichment_icb_ods"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "dynamodb_policy_icb_ods_enrichment_lambda" {
  name = "${var.environment}_${aws_dynamodb_table.mi_api_icb_ods.name}_policy"
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
  name = "${var.environment}_mi_bulk_${aws_dynamodb_table.mi_api_icb_ods.name}_policy"
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
          aws_dynamodb_table.mi_api_icb_ods.arn
        ]
      }
    ]
  })
}