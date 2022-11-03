variable "enriched_mi_events_sns_topic_name" {
  default = "gp-registrations-mi-enriched-mi-events-sns-topic"
}

resource "aws_sns_topic" "enriched_mi_events" {
  name = "${var.environment}-${enriched_mi_events_sns_topic_name}"
  sqs_failure_feedback_role_arn = aws_iam_policy.sns_topic_enriched_mi_events_log_access.arn
  sqs_success_feedback_role_arn = aws_iam_policy.sns_topic_enriched_mi_events_log_access.arn

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sns-topic"
    }
  )
}