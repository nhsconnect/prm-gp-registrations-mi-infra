resource "aws_dynamodb_table" "mi-api-icb-ods_dynamodb_table" {
  name                        = "${var.environment}_mi_enrichment_icb_ods"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = false
  hash_key       = "IcbOdsCode"

  attribute {
    name = "IcbOdsCode"
    type = "S"
  }

  attribute {
    name = "IcbName"
    type = "S"
  }

  tags = {
    Name        = "dynamodb-table-1"
    Environment = var.environment
  }

}

resource "aws_iam_policy" "dynamodb_policy_icb_ods_enrichment_lambda" {
  name = "${var.environment}_${aws_dynamodb_table.mi-api-icb-ods_dynamodb_table.name}_policy"
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
          aws_dynamodb_table.mi-api-ods_dynamodb_table.arn
        ]
      }

    ]
  })
}

resource "aws_iam_policy" "dynamodb_policy_bulk_icb_ods_data_lambda" {
  name = "${var.environment}_mi_bulk_${aws_dynamodb_table.mi-api-icb-ods_dynamodb_table.name}_policy"
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
          aws_dynamodb_table.mi-api-icb-ods_dynamodb_table.arn
        ]
      }

    ]
  })
}