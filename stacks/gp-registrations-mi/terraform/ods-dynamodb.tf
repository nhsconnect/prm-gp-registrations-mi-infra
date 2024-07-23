resource "aws_dynamodb_table" "mi-api-ods_dynamodb_table" {
  name                        = "${var.environment}_mi_enrichment_practice_ods"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = false

  hash_key       = "PracticeOdsCode"

  attribute {
    name = "PracticeOdsCode"
    type = "S"
  }

  attribute {
    name = "PracticeName"
    type = "S"
  }

  attribute {
    name = "IcbOdsCode"
    type = "S"
  }

  attribute {
    name = "SupplierName"
    type = "S"
  }

  attribute {
    name = "SDSLastUpdated"
    type = "N"
  }


  tags = {
    Name        = "mi_enrichment_practice_ods"
    Environment = var.environment
  }

}

resource "aws_iam_policy" "dynamodb_policy_ods_enrichment_lambda" {
  name = "${var.environment}_${aws_dynamodb_table.mi-api-ods_dynamodb_table.name}_policy"
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
          aws_dynamodb_table.mi-api-ods_dynamodb_table.arn
        ]
      }

    ]
  })
}