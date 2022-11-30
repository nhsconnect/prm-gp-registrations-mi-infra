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

resource "aws_sqs_queue_policy" "incoming_enriched_mi_events_for_s3_uploader" {
  queue_url = aws_sqs_queue.incoming_mi_events_for_s3_uploader.id
  policy    = data.aws_iam_policy_document.sqs_queue_incoming_enriched_mi_events.json
}

data "aws_iam_policy_document" "sqs_queue_incoming_enriched_mi_events" {
  statement {
    effect = "Allow"

    actions = [
      "sqs:SendMessage"
    ]

    principals {
      identifiers = ["sns.amazonaws.com"]
      type        = "Service"
    }

    resources = [
      aws_sqs_queue.incoming_mi_events_for_s3_uploader.arn,
    ]

    condition {
      test     = "ArnEquals"
      values   = [aws_sns_topic.enriched_events_topic.arn]
      variable = "aws:SourceArn"
    }
  }
}

