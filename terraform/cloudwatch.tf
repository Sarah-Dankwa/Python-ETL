//Creating cloudwatch log metric filter
resource "aws_cloudwatch_log_metric_filter" "error_metric_filter" {
  name           = "Alapin_de_error_metric_filter"
  pattern        = "ERROR"
  log_group_name = aws_cloudwatch_log_group.alapin_log_group.name

  metric_transformation {
    name      = "ErrorCount"
    namespace = var.metric_namespace
    value     = "1"
  }
}

//Creating cloudwatch log group
resource "aws_cloudwatch_log_group" "alapin_log_group" {
  name = "alapin_logs"
}

//Creating cloudwatch metric alarm
resource "aws_cloudwatch_metric_alarm" "alapin_metric_alarm" {
  alarm_name                = var.alarm_name
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "ErrorCount"
  namespace                 = var.metric_namespace
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "This metric monitors ERROR in loggroup"
  # alarm_actions             = ["arn:aws:sns:eu-west-2:590183674561:user-updates-topic"]
  alarm_actions             = [ 
                        "arn:aws:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${data.aws_sns_topic.step_functions_workflow_sns.arn}", 
                        "arn:aws:sns:eu-west-2:590183674561:user-updates-topic"]
  actions_enabled           = true
  insufficient_data_actions = []
}

