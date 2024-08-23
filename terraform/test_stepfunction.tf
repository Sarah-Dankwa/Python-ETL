locals { 
  step_function_definition = templatefile("${path.module}/step_function_definition.json", {
    aws_region        = "${data.aws_region.current.name}",
    account_id        = "${data.aws_caller_identity.current.account_id}",
    sns_topic_arn     = "${data.aws_sns_topic.step_functions_workflow_sns.arn}"
  })
  #second parameters {} means not passing any variables to the JSON file where there is no placeholder for variables
}

resource "aws_sfn_state_machine" "totesys_state_machine" {
  name       = var.state_machine_name
  role_arn   = aws_iam_role.state_machine_role.arn
  definition = local.step_function_definition
}