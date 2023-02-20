resource "aws_ssm_parameter" "mi_api_cloudwatch_dashboard_url" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/cloudwatch-dashboard-url"
  type  = "String"
  value = "console.aws.amazon.com/cloudwatch/home#dashboards:name=${aws_cloudwatch_dashboard.mi_api.dashboard_name}"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-cloudwatch-dashboard-url"
      ApplicationRole = "AwsSsmParameter"
    }
  )
}
