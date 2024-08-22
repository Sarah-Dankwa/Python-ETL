// Creating a terraform IAMS role for step functions state machine 
resource "aws_iam_role" "state_machine_role" {
    name_prefix = "role-${var.state_machine_name}"
    assume_role_policy = <<EOF
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sts:AssumeRole"
                ],
                "Principal":{
                    "Service": [
                        "states.amazonaws.com"
                    ]
                }
            }
        ]
    }
    EOF
}

//Set up terraform IAMS for Step Functions using Lambda - only need one state machine for the entire ETL process
data "aws_iam_policy_document" "stepfunctions_lambda_policy_document" {
    statement {
            effect= "Allow"
            actions= [
                "lambda:InvokeFunction",
                "lambda:CreateLayerVersion",
                "lambda:DeleteLayerVersion"
            ]
            resources = [
                "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.extract_lambda}",
                "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.transform_lambda}",
                "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.load_lambda}"
            ]
        }
}

//Create the IAM policy using the Step functions - Lambda policy document
resource "aws_iam_policy" "step_function_lambda_policy" {
  name_prefix = "step_function-policy-${var.extract_lambda}-${var.transform_lambda}-${var.load_lambda}"
  policy = data.aws_iam_policy_document.stepfunctions_lambda_policy_document.json
}

# Attach the Policy to the step functions state machine assuming role
resource "aws_iam_role_policy_attachment" "step_function_lambda_policy_attachment" {
  role       = aws_iam_role.state_machine_role.name
  policy_arn = aws_iam_policy.step_function_lambda_policy.arn
}

// Creating a terraform IAMS role for eventbridge
resource "aws_iam_role" "event_bridge_role" {
    name = "eventbridge_step_function_role"
    assume_role_policy = <<EOF
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sts:AssumeRole"
                ],
                "Principal":{
                    "Service": [
                        "events.amazonaws.com"
                    ]
                }
            }
        ]
    }
    EOF
}


//Set up terraform IAMS for Eventbridge using Step Functions - one eventbridge for entire project(ETL)
data "aws_iam_policy_document" "eventbridge_step_functions_policy_document" {
    statement {
            actions= [
             "states:StartExecution"
             ]
            resources= [
                # "arn:aws:events:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:event-bus/*" #needs to update with step function name instead of *
                "arn:aws:states:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:stateMachine:${var.state_machine_name}"
            ]
            effect= "Allow"
        }

}


//Create the IAM policy using the Eventbridge - Step Functions policy document
resource "aws_iam_policy" "eventbridge_step_function_policy" {
  name        = "EventBridgeStepFunctionPolicy"
  policy = data.aws_iam_policy_document.eventbridge_step_functions_policy_document.json
}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "eventbridge_step_function_policy_attachment" {
  role       = aws_iam_role.event_bridge_role.name
  policy_arn = aws_iam_policy.eventbridge_step_function_policy.arn

}
