# DEPENDENCY - create step function on console before adding to terraform

# Set up a step function that will run the flow of the lambda functions 
# and will be invoked via an eventbridge schedular.

locals {
  step_function_definition = jsonencode({
    Comment = "A simple AWS Step Functions state machine",
    StartAt = "LambdaFunction1",
    States = {
      LambdaFunction1 = {
        Type     = "Task",
        Resource = var.lambda_function_1_arn,
        Next     = "LambdaFunction2"
      },
      LambdaFunction2 = {
        Type     = "Task",
        Resource = var.lambda_function_2_arn,
        End      = true
      }
    }
  })
}

resource "aws_sfn_state_machine" "my_state_machine" {
  name       = "my-state-machine"
  role_arn   = aws_iam_role.step_function_role.arn
  definition = local.step_function_definition
}