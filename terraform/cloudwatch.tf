//Creating cloudwatch log metric filter
resource "aws_cloudwatch_log_metric_filter" "error_extract_metric_filter" {
  name           = "Alapin_de_extract_error_metric_filter"
  pattern        = "ERROR"
  log_group_name = aws_cloudwatch_log_group.alapin_extract_log_group.name

  metric_transformation {
    name      = "ErrorCount"
    # namespace = "alapin_extract_metric"
    namespace = var.metric_namespace
    value     = "1"
  }
}

//Creating cloudwatch log group
resource "aws_cloudwatch_log_group" "alapin_extract_log_group" {
  name = "alapin_extract.log"
}

//Creating cloudwatch metric alarm
resource "aws_cloudwatch_metric_alarm" "extract_metric_alarm" {
  # alarm_name                = "terraform-extract-metric-alarm"
  alarm_name                = var.alarm_name
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "ErrorCount"
  namespace                 = "alapin_extract_metric"
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "This metric monitors ERROR in loggroup"
  alarm_actions             = ["arn:aws:sns:eu-west-2:590183674561:user-updates-topic"]
  actions_enabled           = true
  insufficient_data_actions = []
}

