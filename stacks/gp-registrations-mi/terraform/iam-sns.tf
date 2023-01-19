resource "aws_iam_policy" "enriched_mi_events_sns_publish_access" {
  name   = "${var.environment}-enriched-mi-events-sns-publish-access"
  policy = data.aws_iam_policy_document.sns_publish.json
}

data "aws_iam_policy_document" "sns_publish" {
  statement {
    actions = [
      "sns:Publish",
      "sns:GetTopicAttributes"
    ]
    resources = [
      aws_sns_topic.enriched_events_topic.arn
    ]
  }
}

#Cloudwatch - SNS topic
resource "aws_iam_role" "sns_topic_enriched_mi_events_cloudwatch_log_access_role" {
  name               = "${var.environment}-sns-topic-enriched-mi-events-cloudwatch-log-access-role"
  assume_role_policy = data.aws_iam_policy_document.sns_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.sns_topic_enriched_mi_events_log_access.arn,
  ]
}

data "aws_iam_policy_document" "sns_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "sns_topic_enriched_mi_events_log_access" {
  name   = "${var.environment}-sns-topic-enriched-mi-events-cloudwatch-log-access"
  policy = data.aws_iam_policy_document.sns_topic_enriched_mi_events_cloudwatch_log_access.json
}

data "aws_iam_policy_document" "sns_topic_enriched_mi_events_cloudwatch_log_access" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:PutMetricFilter",
      "logs:PutRetentionPolicy"
    ]
    resources = [
      "*",
    ]
  }
}
