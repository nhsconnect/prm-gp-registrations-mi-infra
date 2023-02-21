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
          "title" : "MI_EVENTS_RECEIVED_THROUGH_API_GATEWAY_COUNT",
          "query" : "SOURCE '${aws_cloudwatch_log_group.access_logs.name}' |  stats count (@message) as all, sum ( status < 299 ) as s_2xx, sum ( status = 400 ) as s_400, sum ( status = 401 ) as s_401, sum ( status = 403 ) as s_403, sum ( status = 404 ) as s_404, sum ( status = 415 ) as s_415, sum ( status > 415 and status < 500 ) as s_416_to_499,  sum ( status > 499 ) as s_5xx by bin (1d) as timestamp | filter httpMethod = 'POST'",
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
          "title" : "MI_EVENTS_RECEIVED_THROUGH_API_GATEWAY_LINE_GRAPH",
          "query" : "SOURCE '${aws_cloudwatch_log_group.access_logs.name}' |  stats count (@message) as all, sum ( status < 299 ) as s_2xx, sum ( status > 399 and status < 499 ) as s_4xx, sum ( status > 499 ) as s_5xx by bin (1d) as timestamp | filter httpMethod = 'POST'",
          "view" : "timeSeries"
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
          "title" : "EXCEPTION_FAILED_REQUEST_COUNT",
          "query" : "SOURCE '${data.aws_ssm_parameter.cloud_watch_log_group.value}' |   stats count(@message) as count by bin(1d) as timestamp | filter strcontains(@message, 'Exception') and strcontains(@message, 'WARN')",
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
          "title" : "LAMBDA_EXECUTIONS_LINE_GRAPH",
          "query" : "SOURCE '${aws_cloudwatch_log_group.event_enrichment_lambda.name}' | SOURCE '${aws_cloudwatch_log_group.s3_event_uploader_lambda.name}' | SOURCE '${aws_cloudwatch_log_group.splunk_cloud_event_uploader_lambda.name}' |  stats count (strcontains(@message, '[LAMBDA_STARTED]')) as all, sum ( strcontains(@message, '[LAMBDA_SUCCESSFUL]')) as LAMBDA_SUCCESSFUL, sum (strcontains(@message, 'LAMBDA_FAILED')) as LAMBDA_FAILED, sum (strcontains(@message, 'LAMBDA_FINISHED')) as LAMBDA_FINISHED by bin (1d) as timestamp",
          "view" : "timeSeries"
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