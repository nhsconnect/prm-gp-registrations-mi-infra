resource "aws_iam_role" "degrades_daily_summary_lambda" {
  name               = "degrades_daily_summary_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.degrades_daily_summary_lambda_assume_role.json
}

data "aws_iam_policy_document" "degrades_daily_summary_lambda_assume_role" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}

# Cloudwatch Logging
data "aws_iam_policy_document" "degrades_daily_summary_lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["${aws_cloudwatch_log_group.degrades_daily_summary.arn}", "${aws_cloudwatch_log_group.degrades_daily_summary.arn}:*"]
  }
}

resource "aws_iam_policy" "degrades_daily_summary_logging" {
  name   = "degrades_daily_summary_lambda_logging_policy"
  policy = data.aws_iam_policy_document.degrades_daily_summary_lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "degrades_daily_summary_logging" {
  role       = aws_iam_role.degrades_daily_summary_lambda.name
  policy_arn = aws_iam_policy.degrades_daily_summary_logging.arn
}

# Degrades DynamoDB Access
resource "aws_iam_role_policy_attachment" "degrades_daily_summary_degrades_message_table_access" {
  policy_arn = aws_iam_policy.degrades_message_table_access.arn
  role       = aws_iam_role.degrades_daily_summary_lambda.name
}

# S3 Registrations MI Event
resource "aws_iam_role_policy_attachment" "degrades_daily_summary_registrations_mi_event_access" {
  policy_arn = aws_iam_policy.registrations_mi_events_access.arn
  role       = aws_iam_role.degrades_daily_summary_lambda.name
}