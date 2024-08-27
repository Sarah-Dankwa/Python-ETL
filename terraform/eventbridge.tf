module "eventbridge" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false

  rules = {
    crons = {
      description         = "Run state machine every 15 minutes"
      schedule_expression = "cron(*/15 * ? * * *)"
    }
  }

  targets = {
    crons = [
      {
        name            = "${var.state_machine_name}" 
        arn             = "arn:aws:states:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:stateMachine:${var.state_machine_name}"
        attach_role_arn = true
      }
    ]
  }

  sfn_target_arns   = ["arn:aws:states:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:stateMachine:${var.state_machine_name}"]
  attach_sfn_policy = true
}