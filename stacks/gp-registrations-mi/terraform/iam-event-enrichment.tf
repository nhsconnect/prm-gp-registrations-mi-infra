resource "aws_iam_role" "event_enrichment_lambda_role" {
  name               = "${var.environment}event-enrichment-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.incoming_mi_events_for_event_enrichment_lambda_sqs_read_access.arn,
  ]
}

resource "aws_iam_policy" "incoming_mi_events_for_event_enrichment_lambda_sqs_read_access" {
  name   = "${var.environment}-incoming-mi-events-enrichment-lambda-sqs-read"
  policy = data.aws_iam_policy_document.incoming_mi_events_for_event_enrichment_lambda_sqs_read_access.json
}

data "aws_iam_policy_document" "incoming_mi_events_for_event_enrichment_lambda_sqs_read_access" {
  statement {
    actions = [
      "sqs:GetQueue*",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage"
    ]
    resources = [
      aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda.arn,
    ]
  }
}

