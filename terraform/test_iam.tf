# State Machine Role
resource "aws_iam_role" "state_machine_role" {
  name_prefix = "role-${var.state_machine_name}"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "states.amazonaws.com"
        }
      }
    ]
  }
  EOF
}

# Step Functions and Lambda Policy
data "aws_iam_policy_document" "stepfunctions_lambda_policy_document" {
  statement {
    effect   = "Allow"
    actions  = ["lambda:InvokeFunction", "lambda:CreateLayerVersion", "lambda:DeleteLayerVersion"]
    resources = [
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.extract_lambda}",
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.transform_lambda}",
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.load_lambda}"
    ]
  }
}

resource "aws_iam_policy" "step_function_lambda_policy" {
  name_prefix = "step_function-policy-${var.state_machine_name}"
  policy      = data.aws_iam_policy_document.stepfunctions_lambda_policy_document.json
}

resource "aws_iam_role_policy_attachment" "step_function_lambda_policy_attachment" {
  role       = aws_iam_role.state_machine_role.name
  policy_arn = aws_iam_policy.step_function_lambda_policy.arn
}

#####################################################################################################
# EventBridge Role
resource "aws_iam_role" "event_bridge_role" {
  name = "eventbridge_step_function_role"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "events.amazonaws.com"
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


#####################################################################################################
# CloudWatch Role

resource "aws_iam_role" "cloud_watch_role" {
  name = "cloudwatch_role"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "cloudwatch.amazonaws.com"
        }
      }
    ]
  }
  EOF
}

# CloudWatch SNS Policy for Notifications
data "aws_iam_policy_document" "cloudwatch_sns_policy_document" {
  statement {
    effect = "Allow"
    actions = ["sns:Publish"]
    resources = [
      "arn:aws:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:user-updates-topic",
      # "arn:aws:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_sns_topic.step_functions_workflow_sns.arn}"
      "${data.aws_sns_topic.step_functions_workflow_sns.arn}"
    ]
  }
}


//Create the IAM policy using the cloudwatch SNS policy document
resource "aws_iam_policy" "cloudwatch_sns_policy" {
  name        = "CloudWatchSNSPolicy"
  description = "IAM policy to allow CloudWatch to create and manage SNS topics and subscriptions"
  policy = data.aws_iam_policy_document.cloudwatch_sns_policy_document.json
}

# Attach the Policy to the cloudwatch Role
resource "aws_iam_role_policy_attachment" "cloudwatch_sns_policy_attachment" {
  role       = aws_iam_role.cloud_watch_role.name
  policy_arn = aws_iam_policy.cloudwatch_sns_policy.arn
}

# Attach the sns Policy to the state machine Role
resource "aws_iam_role_policy_attachment" "step_functions_sns_policy_attachment" {
  role       = aws_iam_role.state_machine_role.name
  policy_arn = aws_iam_policy.cloudwatch_sns_policy.arn
}

#####################################################################################################
#####################################################################################################
# Extract Lambda Role

resource "aws_iam_role" "extract_lambda_role" {
  name_prefix = "role-${var.extract_lambda}"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        }
      }
    ]
  }
  EOF
}


# ==========================================
# CloudWatch Logs Policy for Extract Lambda
# ==========================================

//The IAM Policy Document specifies the permissions required for extract Lambda to access cloudwatch
data "aws_iam_policy_document" "cw_document_extract" {
  statement {
    effect   = "Allow"
    actions  = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.alapin_log_group.name}:*"]
  }
}

// Set up terraform IAMS permissions for Lambda - Cloudwatch
resource "aws_iam_policy" "cw_policy_extract" {
  name_prefix = "cw-policy-${var.extract_lambda}"
  policy      = data.aws_iam_policy_document.cw_document_extract.json
}

# Attach the CW Policy to the Extract Role
resource "aws_iam_role_policy_attachment" "cw_policy_attachment_extract" {
  role       = aws_iam_role.extract_lambda_role.name
  policy_arn = aws_iam_policy.cw_policy_extract.arn
}


# ==========================================
# S3 Policy for Extract Lambda
# ==========================================

//The IAM Policy Document specifies the permissions required for Lambda to access s3
data "aws_iam_policy_document" "s3_document_extract"{
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
resource "aws_iam_policy" "s3_policy_extract" {
    name_prefix = "s3-policy-${var.extract_lambda}"
    description = "extract lambda policy for S3 read/write access "
    policy = data.aws_iam_policy_document.s3_document_extract.json
}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "s3_policy_attachment_extract" {
    role = aws_iam_role.extract_lambda_role.name
    policy_arn = aws_iam_policy.s3_policy_extract.arn
  
}



# ==========================================
# Secrets Manager Policy for Extract Lambda
# ==========================================


data "aws_iam_policy_document" "secret_manager_extract_document" {
  statement {
    effect   = "Allow"
    actions  = ["secretsmanager:GetSecretValue"]
    resources = [
      "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:totesys-database-1iOpWx"
    ]
    sid = "AllowSecrets"
  }
}

//Create the IAM policy using the secret manager policy document
resource "aws_iam_policy" "secret_manager_policy_extract" {
  name_prefix = "secretmanager-policy-${var.extract_lambda}"
  policy      = data.aws_iam_policy_document.secret_manager_extract_document.json
}


# Attach the Policy to the Lambda Role
resource "aws_iam_role_policy_attachment" "secret_manager_extract_policy_attachment" {
  role       = aws_iam_role.extract_lambda_role.name
  policy_arn = aws_iam_policy.secret_manager_policy_extract.arn
}


# ===============================
# SSM Policy for Extract Lambda
# ===============================

data "aws_iam_policy_document" "ssm_policy_document_extract" {
  statement {
    actions   = ["ssm:GetParameter", "ssm:PutParameter"]
    effect    = "Allow"
    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/latest-extract"
    ]
  }
}

//Create the IAM policy using the ssm policy document for Extract Lambda
resource "aws_iam_policy" "ssm_policy_extract" {
  name_prefix = "ssm-${var.extract_lambda}"
  policy      = data.aws_iam_policy_document.ssm_policy_document_extract.json
}


# Attach the SSM Policy to the Extract lambda Role
resource "aws_iam_role_policy_attachment" "ssm_policy_attachment_extract" {
  role       = aws_iam_role.extract_lambda_role.name
  policy_arn = aws_iam_policy.ssm_policy_extract.arn
}


#####################################################################################################
#####################################################################################################
# Transform Lambda Role


// Creating a terraform IAMS role for transform Lambda
resource "aws_iam_role" "transform_lambda_role" {
    name_prefix = "role-${var.transform_lambda}"
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


# ==========================================
# CloudWatch Logs Policy for Transform Lambda
# ==========================================


//The IAM Policy Document specifies the permissions required for transform Lambda to access cloudwatch
data "aws_iam_policy_document" "cw_document_transform" {
  statement {
    effect   = "Allow"
    actions  = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.alapin_log_group.name}:*"
    ]
  }
}

//Create the IAM policy using the cloud watch policy document for transform lambda
resource "aws_iam_policy" "cw_policy_transform" {
    name_prefix = "cw-policy-${var.transform_lambda}"
    policy = data.aws_iam_policy_document.cw_document_transform.json
}


# Attach the existing cw policy to the transform lambda role
resource "aws_iam_role_policy_attachment" "cw_policy_attachment_transform" {
    role = aws_iam_role.transform_lambda_role.name
    policy_arn = aws_iam_policy.cw_policy_transform.arn
}

# ==========================================
# S3 Policy for Transform Lambda
# ==========================================


// create policy document of using processed_data_bucket in aws s3
data "aws_iam_policy_document" "s3_document_transform"{
    statement {

        effect = "Allow"
        actions = ["s3:PutObject",
                   "s3:GetObject",
                   "s3:ListBucket",
                   "s3:DeleteObject"]

        resources = [
            "${aws_s3_bucket.processed_data_bucket.arn}/*",
            "${aws_s3_bucket.processed_data_bucket.arn}",
            "${aws_s3_bucket.ingested_data_bucket.arn}/*",
            "${aws_s3_bucket.ingested_data_bucket.arn}"
        ]       
    }

}


//Create the IAM policy using the s3 policy document for transform lambda assuming role
resource "aws_iam_policy" "s3_policy_transform" {
    name_prefix = "s3-policy-${var.transform_lambda}"
    description = "transform lambda policy for S3 read/write access "
    policy = data.aws_iam_policy_document.s3_document_transform.json
}


# Attach the Policy to the transform lambda assuming role
resource "aws_iam_role_policy_attachment" "s3_policy_attachment_transform" {
    role = aws_iam_role.transform_lambda_role.name
    policy_arn = aws_iam_policy.s3_policy_transform.arn

}

#####################################################################################################
#####################################################################################################
# Load Lambda Role

// Creating a terraform IAMS role for the Load lambda function
resource "aws_iam_role" "load_lambda_role" {
    name_prefix = "role-${var.load_lambda}"
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

# ==========================================
# CloudWatch Logs Policy for Load Lambda
# ==========================================


//The IAM Policy Document specifies the permissions required for load Lambda to access cloudwatch
data "aws_iam_policy_document" "cw_document_load"{

    statement {
      effect = "Allow"
      actions = ["logs:CreateLogStream","logs:PutLogEvents"]
      resources = [
        "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.alapin_log_group.name}:*"
      ]
    }
}

//Create the IAM policy using the cloud watch policy document for load lambda
resource "aws_iam_policy" "cw_policy_load" {
    name_prefix = "cw-policy-${var.load_lambda}"
    policy = data.aws_iam_policy_document.cw_document_load.json
}

# Attach the existing cw policy to the load lambda role
resource "aws_iam_role_policy_attachment" "cw_policy_attachment_load" {
    role = aws_iam_role.load_lambda_role.name
    policy_arn = aws_iam_policy.cw_policy_load.arn
}


# ==========================================
# S3 Policy for Load Lambda
# ==========================================


//The IAM Policy Document specifies the permissions required for load Lambda to access S3
data "aws_iam_policy_document" "s3_document_load"{
    statement {

        effect = "Allow"
        actions = ["s3:GetObject",
                   "s3:ListBucket",
                   "s3:DeleteObject"]

       resources = [
            "${aws_s3_bucket.processed_data_bucket.arn}/*",
            "${aws_s3_bucket.processed_data_bucket.arn}"
        ]       
    }

}


//Create the IAM policy using the s3 policy document for load lambda
resource "aws_iam_policy" "s3_policy_load" {
    name_prefix = "s3-policy-${var.load_lambda}"
    description = "load lambda policy for S3 read access "
    policy = data.aws_iam_policy_document.s3_document_load.json
}


# Attach the existing s3 policy to the load lambda role
resource "aws_iam_role_policy_attachment" "s3_policy_attachment_load" {
    role = aws_iam_role.load_lambda_role.name
    policy_arn = aws_iam_policy.s3_policy_load.arn
  
}


# ==========================================
# Secrets Manager Policy for Load Lambda
# ==========================================



//The IAM Policy Document specifies the permissions required for load Lambda to access AWS secrets manager
data "aws_iam_policy_document" "secret_manager_document_warehouse"{
    statement  {
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = ["arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:totesys-warehouse-ltGoRO",]
      effect = "Allow"
      sid = "AllowSecrets"
    }
}


//Create the IAM policy using the secret manager policy document for load lambda
resource "aws_iam_policy" "secret_manager_policy_warehouse" {
    name_prefix = "secretmanager-policy-${var.load_lambda}"
    policy = data.aws_iam_policy_document.secret_manager_document_warehouse.json
}


# Attach the Policy to the load lambda Role
resource "aws_iam_role_policy_attachment" "secret_manager_load_policy_attachement" {
    role = aws_iam_role.load_lambda_role.name
    policy_arn = aws_iam_policy.secret_manager_policy_warehouse.arn
  
}

