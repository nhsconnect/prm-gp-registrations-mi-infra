resource "aws_iam_role" "gp_registrations_mi" {
  name               = "${var.environment}-gp-registrations-mi"
  description        = "Role for gp registrations mi ecs service"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  managed_policy_arns = [
    aws_iam_policy.mi_output_bucket_write_access.arn,
  ]
}

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = [
    "sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "mi_output_bucket_write_access" {
  name   = "${aws_s3_bucket.mi_output.bucket}-write"
  policy = data.aws_iam_policy_document.mi_output_bucket_write_access.json
}

data "aws_iam_policy_document" "mi_output_bucket_write_access" {
  statement {
    sid = "WriteObjects"

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.mi_output.bucket}/*"
    ]
  }
}