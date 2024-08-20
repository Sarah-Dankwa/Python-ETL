
# # # DEPENDENCY - create step function on console before adding to terraform

# # # Set up a step function that will run the flow of the lambda functions 
# # # and will be invoked via an eventbridge schedular.

# locals {
#   step_function_definition = jsonencode({
#     Comment = "AWS Step Functions state machine",
#     StartAt = "ExtractTaskLambda",
#     States = {
#       "ExtractTaskLambda" = {
#         Type     = "Task",
#         Resource = aws_lambda_function.workflow_tasks_extract.arn,  #lambda function name #aws_lambda_function.workflow_tasks_extract.arn
#         Next     = "TransformTaskLambda"
#       },
#       "TransformTaskLambda" = {
#         Type     = "Task",
#         Resource = aws_lambda_function.workflow_tasks_transform.arn,
#         Next     = "LoadTaskLambda"
#       },
#       "LoadTaskLambda" = {
#         Type     = "Task",
#         Resource = aws_lambda_function.workflow_tasks_load.arn,
#         End      = true
#       }
#     }
#   })
# }

# resource "aws_sfn_state_machine" "totesys_state_machine" {
#   name       = var.state_machine_name
#   role_arn   = aws_iam_role.state_lambda_role.arn
#   definition = local.step_function_definition
# }

