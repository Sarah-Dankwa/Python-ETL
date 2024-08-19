// Creating a terraform IAMS role for Lambda, cloudwatch and eventbridge
resource "aws_iam_role" "lambda_role" {
    name_prefix = "role-${var.extract_lambda}"
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
                        "lambda.amazonaws.com"
                    ]
                }
            }
        ]
    }
    EOF
}

// Set up terraform IAMS permissions for Lambda - Cloudwatch
// //The IAM Policy Document specifies the permissions required for extract Lambda to access cloudwatch
data "aws_iam_policy_document" "cw_document"{
    statement{
        effect = "Allow"
        actions = ["logs:CreateLogGroup"]
        resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
    }
    statement {
      effect = "Allow"
      actions = ["logs:CreateLogStream","logs:PutLogEvents"]
      resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.extract_lambda}:*",
                    "arn:aws:logs:eu-west-2:590183674561:log-group:${aws_cloudwatch_log_group.alapin_extract_log_group.name}:*"]
    }
}

//Create the IAM policy using the cloud watch policy document
resource "aws_iam_policy" "cw_policy" {
    name_prefix = "cw-policy-${var.extract_lambda}"
    policy = data.aws_iam_policy_document.cw_document.json
}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "name" {
    role = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.cw_policy.arn
  
}

//Set up terraform IAMS permissions for Lambda - S3
//The IAM Policy Document specifies the permissions required for Lambda to access s3
data "aws_iam_policy_document" "s3_document"{
    statement {

        effect = "Allow"
        actions = ["s3:PutObject",
                   "s3:GetObject",
                   "s3:ListBucket"]

        resources = [
            "${aws_s3_bucket.ingested_data_bucket.arn}/*",
            "${aws_s3_bucket.ingested_data_bucket.arn}"
        ]       
    }

}

//Create the IAM policy using the s3 policy document
resource "aws_iam_policy" "s3_policy" {
    name_prefix = "s3-policy-${var.extract_lambda}"
    policy = data.aws_iam_policy_document.s3_document.json
}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "s3_policy_attachement" {
    role = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.s3_policy.arn
  
}


//Set up terraform IAMS permissions for Lambda - RDS - Needs a discussion on if we really need it or not
/*data "aws_iam_policy_document" "rds_document"{
    statement {data "aws_iam_policy_document" "s3_document"{

    }

resource "aws_iam_policy" "lambda_rds_policy"{
  name        = "LambdaRDSPolicy"
  policy = data.aws_iam_policy_document.rds_document.json

}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "lambda_rds_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_rds_policy.arn
}
*/

//Set up terraform IAMS for Lamba - Secrets manager
//The IAM Policy Document specifies the permissions required for extract Lambda to access secret manager
data "aws_iam_policy_document" "secret_manager_document"{
    statement  {
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = ["arn:aws:secretsmanager:eu-west-2:590183674561:secret:totesys-database-1iOpWx",]
      effect = "Allow"
      sid = "AllowSecrets"
    }
}

//Create the IAM policy using the secret manager policy document
resource "aws_iam_policy" "secret_manager_policy" {
    name_prefix = "secretmanager-policy-${var.extract_lambda}"
    policy = data.aws_iam_policy_document.secret_manager_document.json
}

# Attach the Policy to the Lambda Role
resource "aws_iam_role_policy_attachment" "secret_manager_policy_attachement" {
    role = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.secret_manager_policy.arn
  
}

//Set up terraform IAM permissions for Cloudwatch - SNS
//The IAM Policy Document specifies the permissions required to create SNS topics and subscriptions
data "aws_iam_policy_document" "cloudwatch_sns_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "sns:Publish"
    ]

    resources = [
      "arn:aws:sns:eu-west-2:590183674561:user-updates-topic" 

    ]
  }
}
//Create the IAM policy using the cloudwatch SNS policy document
resource "aws_iam_policy" "cloudwatch_sns_policy" {
  name        = "CloudWatchSNSPolicy"
  description = "IAM policy to allow CloudWatch to create and manage SNS topics and subscriptions"

  policy = data.aws_iam_policy_document.cloudwatch_sns_policy_document.json
}

// Creating a terraform IAMS role for cloudwatch
resource "aws_iam_role" "cloud_watch_role" {
    name = "cloudwatch_role"
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
                        "cloudwatch.amazonaws.com"
                    ]
                }
            }
        ]
    }
    EOF
}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "cloudwatch_sns_policy_attachment" {
  role       = aws_iam_role.cloud_watch_role.name
  policy_arn = aws_iam_policy.cloudwatch_sns_policy.arn
}

// Creating a terraform IAMS role for step functions state machine
resource "aws_iam_role" "state_lambda_role" {
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

//Set up terraform IAMS for Step Functions using Lambda
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
resource "aws_iam_policy" "stepfunction_lambda_policy" {
  name        = "stepfunctionlambdaPolicy"

  policy = data.aws_iam_policy_document.stepfunctions_lambda_policy_document.json
}

# Attach the Policy to the step functions state machine assuming role
resource "aws_iam_role_policy_attachment" "stepfunction_lambda_policy_attachment" {
  role       = aws_iam_role.state_lambda_role.name
  policy_arn = aws_iam_policy.stepfunction_lambda_policy.arn
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

data "aws_iam_policy_document" "ssm_policy_document" {
	statement {
		actions = [
			"ssm:GetParameter",
            "ssm:PutParameter"
		]
		resources = [
			"arn:aws:ssm:eu-west-2:590183674561:parameter/latest-extract"
		]
	}
}

//Create the IAM policy using the ssm policy document
resource "aws_iam_policy" "ssm_policy" {
    name_prefix = "ssm-${var.extract_lambda}"
    policy = data.aws_iam_policy_document.ssm_policy_document.json
}

# Attach the SSM Policy to the lambda Role
resource "aws_iam_role_policy_attachment" "ssm_attachement" {
    role = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.ssm_policy.arn
  

}