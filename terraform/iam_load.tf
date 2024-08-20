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

// Set up terraform IAMS permissions for Lambda - Cloudwatch

# Attach the existing cw policy to the transform lambda role
resource "aws_iam_role_policy_attachment" "cw_policy_attachment" {
    role = aws_iam_role.load_lambda_role.name
    policy_arn = aws_iam_policy.cw_policy.arn
}

# Attach the existing s3 policy to the transform lambda role
resource "aws_iam_role_policy_attachment" "s3_policy_attachment_load" {
    role = aws_iam_role.load_lambda_role.name
    policy_arn = aws_iam_policy.s3_policy_extract_load.arn
  
}

//Set up terraform IAMS for Lambda - Secrets manager
//The IAM Policy Document specifies the permissions required for load Lambda to access AWS secrets manager
data "aws_iam_policy_document" "secret_manager_document_warehouse"{
    statement  {
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = ["arn:aws:secretsmanager:eu-west-2:590183674561:secret:totesys-warehouse-ltGoRO",]
      effect = "Allow"
      sid = "AllowSecrets"
    }
}

//Create the IAM policy using the secret manager policy document
resource "aws_iam_policy" "secret_manager_policy_warehouse" {
    name_prefix = "secretmanager-policy-${var.load_lambda}"
    policy = data.aws_iam_policy_document.secret_manager_document_warehouse.json
}

# Attach the Policy to the Lambda Role
resource "aws_iam_role_policy_attachment" "secret_manager_policy_attachement" {
    role = aws_iam_role.extract_lambda_role.name
    policy_arn = aws_iam_policy.secret_manager_policy_warehouse.arn
  
}

