data "aws_sns_topic" "step_functions_workflow_sns" {
  name = "totesys-workflow-step-functions-notifications"

}

# another way to reference to "aws_sns_topic.step_functions_workflow_notifications.arn" using output
# output "sns_topic_arn" {
#   value = data.aws_sns_topic.step_functions_workflow_notifications.arn
# }

resource "aws_sns_topic_subscription" "step_function_email_subscription"{
  topic_arn = data.aws_sns_topic.step_functions_workflow_sns.arn
  protocol  = "email"
  endpoint  = "hanawang346@gmail.com"
}