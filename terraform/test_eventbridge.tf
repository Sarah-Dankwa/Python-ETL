resource "aws_cloudwatch_event_rule" "trigger_step_function" {
  name        = "TriggerStepFunctionRule"
  description = "EventBridge rule to trigger Step Functions"
  event_pattern = jsonencode({"source" = ["custom.test"]})
#   event_pattern = jsonencode({
#     "detail-type" = [
#       "AWS API Call via CloudTrail"
#     ],
#     "source" = ["aws.s3"], 

#     "detail" = {
#         "eventName" = ["PutObject"],
#         "requestParameters" = { 
#             "bucketName" = [aws_s3_bucket.ingested_data_bucket.bucket] 
#         }
#     }
#   })

}

resource "aws_cloudwatch_event_target" "step_function_target" {
  rule      = aws_cloudwatch_event_rule.trigger_step_function.name
  target_id = "StepFunctionTarget"
  arn       = aws_sfn_state_machine.totesys_state_machine.arn
  role_arn  = aws_iam_role.event_bridge_role.arn
}
