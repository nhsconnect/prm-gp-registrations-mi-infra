resource "aws_ecr_repository" "gp_registrations_mi" {
  name = "registrations/${var.environment}/gp-registrations-mi/mi-api"
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi"
      ApplicationRole = "AwsEcrRepository"
    }
  )
}

data "aws_iam_policy_document" "ecr_gp_registrations_mi" {
  count      = var.environment == "dev" ? 1 : 0
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [data.aws_ssm_parameter.prod-aws-account-id.value]
    }

    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:DescribeImages",
      "ecr:ListImages",
    ]
  }
}

resource "aws_ecr_repository_policy" "ecr_gp_registrations_mi" {
  count      = var.environment == "dev" ? 1 : 0
  repository = aws_ecr_repository.gp_registrations_mi.name
  policy     = data.aws_iam_policy_document.ecr_gp_registrations_mi.json
}

data "aws_ssm_parameter" "prod-aws-account-id" {
  count      = var.environment == "dev" ? 1 : 0
  name = "/registrations/dev/user-input/prod-aws-account-id"
}