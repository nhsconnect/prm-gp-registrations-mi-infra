resource "aws_iam_role" "degrades_message_receiver_lambda" {
  name               = "degrades_message_receiver_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.degrades_message_receiver_lambda_assume_role.json
}

data "aws_iam_policy_document" "degrades_message_receiver_lambda_assume_role" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role_policy_attachment" "degrades_message_receiver_lambda_dynamodb" {
  policy_arn = aws_iam_policy.degrades_message_table_access.arn
  role       = aws_iam_role.degrades_message_receiver_lambda.name
}


resource "aws_iam_role_policy_attachment" "degrades_lambda_sqs_invoke" {
  policy_arn = aws_iam_policy.degrades_lambda_sqs_invoke.arn
  role       = aws_iam_role.degrades_message_receiver_lambda.name
}

resource "aws_iam_policy" "degrades_lambda_sqs_invoke" {
  name   = "degrades_sqs_invoke_policy"
  policy = data.aws_iam_policy_document.degrades_messages_sqs_receiver.json
}

data "aws_iam_policy_document" "degrades_message_receiver_lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["${aws_cloudwatch_log_group.degrades_message_receiver.arn}", "${aws_cloudwatch_log_group.degrades_message_receiver.arn}:*"]
  }
}

resource "aws_iam_policy" "degrades_message_receiver_logging" {
  name        = "degrades_message_receiver_lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.degrades_message_receiver_lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "degrades_message_receiver_logs" {
  role       = aws_iam_role.degrades_message_receiver_lambda.name
  policy_arn = aws_iam_policy.degrades_message_receiver_logging.arn
}