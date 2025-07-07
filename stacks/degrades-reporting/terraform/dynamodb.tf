resource "aws_dynamodb_table" "degrades_message_table" {
  name         = "${var.degrades_message_table}_${var.environment}"
  hash_key     = "Timestamp"
  range_key    = "MessageId"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "Timestamp"
    type = "N"
  }
  attribute {
    name = "MessageId"
    type = "S"
  }
}

data "aws_iam_policy_document" "degrades_message_table_access" {
  statement {
    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:ConditionCheckItem",
      "dynamodb:PutItem",
      "dynamodb:DescribeTable",
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:UpdateItem"
    ]
    resources = ["${aws_dynamodb_table.degrades_message_table.arn}"]
  }
}

resource "aws_iam_policy" "degrades_message_table_access" {
  name   = "degrades_message_table_access_policy"
  policy = data.aws_iam_policy_document.degrades_message_table_access.json
}