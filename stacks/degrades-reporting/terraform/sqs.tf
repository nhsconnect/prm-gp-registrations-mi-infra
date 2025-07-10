resource "aws_sqs_queue" "degrades_messages" {
  name = "${var.environment}_${var.degrades_message_queue}"

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.degrades_messages_deadletter.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "degrades_messages_deadletter" {
  name = "${var.environment}_${var.degrades_message_queue}_dlq"
}

resource "aws_sqs_queue_redrive_allow_policy" "degrades_message_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.degrades_messages_deadletter.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.degrades_messages.arn]
  })
}

data "aws_iam_policy_document" "degrades_messages_sqs_receiver" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:DeleteMessage"
    ]
    resources = ["${aws_sqs_queue.degrades_messages.arn}", "${aws_sqs_queue.degrades_messages_deadletter.arn}"]
  }
}