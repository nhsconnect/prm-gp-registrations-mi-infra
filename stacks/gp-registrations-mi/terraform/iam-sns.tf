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

