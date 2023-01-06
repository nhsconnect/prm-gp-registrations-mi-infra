resource "aws_ssm_parameter" "cloudwatch_log_group_name" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/cloudwatch-log-group-name"
  type  = "String"
  value = aws_cloudwatch_log_group.gp_registrations_mi.name
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
      ApplicationRole = "AwsSsmParameter"
    }
  )
}

resource "aws_ssm_parameter" "execution_role_arn" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/ecs-execution-role-arn"
  type  = "String"
  value = aws_iam_role.ecs_execution.arn
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
      ApplicationRole = "AwsSsmParameter"
    }
  )
}

resource "aws_ssm_parameter" "ecs_cluster_arn" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/ecs-cluster/ecs-cluster-arn"
  type  = "String"
  value = aws_ecs_cluster.gp_registrations_mi_cluster.arn
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
      ApplicationRole = "AwsSsmParameter"
    }
  )
}
