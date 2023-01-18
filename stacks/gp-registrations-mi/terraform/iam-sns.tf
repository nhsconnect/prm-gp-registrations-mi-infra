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

resource "aws_cloudwatch_log_group" "sns_topic_enriched_mi_events" {
  name = "/sns/${var.environment}-${var.enriched_mi_events_sns_topic_name}"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-${var.enriched_mi_events_sns_topic_name}"
    }
  )
  retention_in_days = 60
}