resource "aws_cloudwatch_dashboard" "mi_api" {
  dashboard_name = "${var.environment}-gp-registrations-mi-events-dashboard"
  dashboard_body = jsonencode({
    "start" : "-P3D"
    "widgets" : [
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "MI_EVENTS_RECEIVED_COUNT",
          "query" : "SOURCE '${data.aws_ssm_parameter.cloud_watch_log_group.value}' |  stats count(message) as count by bin(1d) as timestamp | filter strcontains(message, 'Incoming request')",
          "view" : "table"
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "SUCCESSFUL_MI_EVENTS_RECEIVED_READY_FOR_ENRICHMENT_COUNT",
          "query" : "SOURCE '${data.aws_ssm_parameter.cloud_watch_log_group.value}' |  stats count(message) as count by bin(1d) as timestamp | filter strcontains(message, 'Successfully sent message')",
          "view" : "table"
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "INVALID_REQUESTS_COUNT",
          "query" : "SOURCE '${data.aws_ssm_parameter.cloud_watch_log_group.value}' |  stats count(message) as count by bin(1d) as timestamp | filter strcontains(message, 'Invalid')",
          "view" : "table"
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "Non-info logs (errors, warnings, system)",
          "query" : "SOURCE '${data.aws_ssm_parameter.cloud_watch_log_group.value}' | fields @timestamp, message, @message | filter level != 'INFO'",
          "view" : "table"
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "Error logs",
          "query" : "SOURCE '${data.aws_ssm_parameter.cloud_watch_log_group.value}' | fields @timestamp, message, @message | filter level == 'ERROR'",
          "view" : "table"
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "All log messages",
          "query" : "SOURCE '${data.aws_ssm_parameter.cloud_watch_log_group.value}' | fields @timestamp, message, @message",
          "view" : "table",
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "Event enrichment lambda - Error count",
          "query" : "SOURCE '${aws_cloudwatch_log_group.event_enrichment_lambda.name}' |  stats count(@message) as count by bin(1d) as timestamp | filter strcontains(@message, '[ERROR]')",
          "view" : "table",
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "Event enrichment lambda - Error logs",
          "query" : "SOURCE '${aws_cloudwatch_log_group.event_enrichment_lambda.name}' | fields @timestamp, @message | filter strcontains(@message, '[ERROR]')",
          "view" : "table",
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "S3 event uploader lambda - Error count",
          "query" : "SOURCE '${aws_cloudwatch_log_group.s3_event_uploader_lambda.name}' |  stats count(@message) as count by bin(1d) as timestamp | filter strcontains(@message, '[ERROR]')",
          "view" : "table",
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "S3 event uploader lambda - Error logs",
          "query" : "SOURCE '${aws_cloudwatch_log_group.s3_event_uploader_lambda.name}' | fields @timestamp, @message | filter strcontains(@message, '[ERROR]')",
          "view" : "table",
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "Splunk cloud event uploader lambda - Error count",
          "query" : "SOURCE '${aws_cloudwatch_log_group.splunk_cloud_event_uploader_lambda.name}' |  stats count(@message) as count by bin(1d) as timestamp | filter strcontains(@message, '[ERROR]')",
          "view" : "table",
        }
      },
      {
        "type" : "log",
        "width" : 12,
        "height" : 6,
        "properties" : {
          "period" : 120
          "region" : data.aws_region.current.name,
          "title" : "Splunk cloud event uploader lambda - Error logs",
          "query" : "SOURCE '${aws_cloudwatch_log_group.splunk_cloud_event_uploader_lambda.name}' | fields @timestamp, @message | filter strcontains(@message, '[ERROR]')",
          "view" : "table",
        }
      },
    ]
  })
}