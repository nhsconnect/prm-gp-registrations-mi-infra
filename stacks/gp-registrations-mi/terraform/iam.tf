resource "aws_iam_role" "gp_registrations_mi" {
  name                = "${var.environment}-gp-registrations-mi"
  description         = "Role for gp registrations mi ecs service"
  assume_role_policy  = data.aws_iam_policy_document.ecs_assume.json
  managed_policy_arns = []
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
