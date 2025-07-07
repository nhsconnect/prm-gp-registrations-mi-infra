resource "aws_iam_policy" "registrations_mi_events_access" {
  name   = "regristrations_mi_events_read_policy"
  policy = data.aws_iam_policy_document.registrations_mi_events_access.json
}

data "aws_iam_policy_document" "registrations_mi_events_access" {
  statement {
    effect = "Allow"

    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObjectVersion",
      "s3:DeleteObjectVersionTagging",
      "s3:GetObject",
      "s3:GetObjectAcl",
      "s3:GetObjectAttributes",
      "s3:GetObjectRetention",
      "s3:GetObjectTagging",
      "s3:GetObjectVersion",
      "s3:GetObjectVersionAcl",
      "s3:GetObjectVersionAttributes",
      "s3:GetObjectVersionTagging",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:ListBucketVersions",
      "s3:PutObjectVersionTagging",
      "s3:RestoreObject",
    ]
    resources = [
    "arn:aws:s3:::${var.registrations_mi_event_bucket}/*", "arn:aws:s3:::${var.registrations_mi_event_bucket}"]
  }
}