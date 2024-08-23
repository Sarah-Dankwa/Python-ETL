# // Creating a terraform IAMS role for the Load lambda function
# resource "aws_iam_role" "load_lambda_role" {
#     name_prefix = "role-${var.load_lambda}"
#     assume_role_policy = <<EOF
#     {
#         "Version": "2012-10-17",
#         "Statement": [
#             {
#                 "Effect": "Allow",
#                 "Action": [
#                     "sts:AssumeRole"
#                 ],
#                 "Principal":{
#                     "Service": [
#                         "lambda.amazonaws.com"
#                     ]
#                 }
#             }
#         ]
#     }
#     EOF
# }

# // Set up terraform IAMS permissions for Lambda - Cloudwatch
# // //The IAM Policy Document specifies the permissions required for load Lambda to access cloudwatch
# data "aws_iam_policy_document" "cw_document_load"{

#     statement {
#       effect = "Allow"
#       actions = ["logs:CreateLogStream","logs:PutLogEvents"]
#       resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.load_lambda}:*",
#                     "arn:aws:logs:eu-west-2:590183674561:log-group:${aws_cloudwatch_log_group.alapin_extract_log_group.name}:*"]
#     }
# }

# //Create the IAM policy using the cloud watch policy document
# resource "aws_iam_policy" "cw_policy_load" {
#     name_prefix = "cw-policy-${var.load_lambda}"
#     policy = data.aws_iam_policy_document.cw_document_load.json
# }
# # Attach the existing cw policy to the transform lambda role
# resource "aws_iam_role_policy_attachment" "cw_policy_attachment_load" {
#     role = aws_iam_role.load_lambda_role.name
#     policy_arn = aws_iam_policy.cw_policy_load.arn
# }

# // Set up terraform IAMS permissions for Lambda - S3
# data "aws_iam_policy_document" "s3_document_load"{
#     statement {

#         effect = "Allow"
#         actions = ["s3:GetObject",
#                    "s3:ListBucket"]

#        resources = [
#             "${aws_s3_bucket.processed_data_bucket.arn}/*",
#             "${aws_s3_bucket.processed_data_bucket.arn}"
#         ]       
#     }

# }

# //Create the IAM policy using the s3 policy document
# resource "aws_iam_policy" "s3_policy_load" {
#     name_prefix = "s3-policy-${var.load_lambda}"
#     description = "load lambda policy for S3 read access "
#     policy = data.aws_iam_policy_document.s3_document_load.json
# }


# # Attach the existing s3 policy to the transform lambda role
# resource "aws_iam_role_policy_attachment" "s3_policy_attachment_load" {
#     role = aws_iam_role.load_lambda_role.name
#     policy_arn = aws_iam_policy.s3_policy_load.arn
  
# }

# //Set up terraform IAMS for Lambda - Secrets manager
# //The IAM Policy Document specifies the permissions required for load Lambda to access AWS secrets manager
# data "aws_iam_policy_document" "secret_manager_document_warehouse"{
#     statement  {
#       actions = [
#         "secretsmanager:GetSecretValue"
#       ]
#       resources = ["arn:aws:secretsmanager:eu-west-2:590183674561:secret:totesys-warehouse-ltGoRO",]
#       effect = "Allow"
#       sid = "AllowSecrets"
#     }
# }

# //Create the IAM policy using the secret manager policy document
# resource "aws_iam_policy" "secret_manager_policy_warehouse" {
#     name_prefix = "secretmanager-policy-${var.load_lambda}"
#     policy = data.aws_iam_policy_document.secret_manager_document_warehouse.json
# }

# # Attach the Policy to the Lambda Role
# resource "aws_iam_role_policy_attachment" "secret_manager_load_policy_attachement" {
#     role = aws_iam_role.extract_lambda_role.name
#     policy_arn = aws_iam_policy.secret_manager_policy_warehouse.arn
  
# }

