resource "aws_sns_topic" "enriched_mi_events" {
  name = "${var.environment}-gp-registrations-mi-enriched-mi-events-sns-topic"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sns-topic"
    }
  )
}