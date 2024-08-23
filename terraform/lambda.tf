# Set up lambda block in terraform to 
# point to local code file and add layers or enviroment variables where needed.

// create zip file function.zip in extract folder by packaging a Python script extract.py into a zip file 
data "archive_file" "extract_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/extract/function.zip"
  source_file = "${path.module}/../src/extract.py"
}

// create zip file function.zip in transform folder by packaging a Python script transform.py into a zip file 
data "archive_file" "transform_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/transform/function.zip"
  source_file = "${path.module}/../src/transform.py"
}

// create zip file function.zip in load folder by packaging a Python script load.py into a zip file 
data "archive_file" "load_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/load/function.zip"
  source_file = "${path.module}/../src/load.py"
}

// create lambda function with name 'extact' using the zip file 'extract/function.zip' uploaded in s3 bucket
resource "aws_lambda_function" "workflow_tasks_extract" {

  # Defines the lambda function's name in aws, which is used as identifier for lambda functions
  function_name    = var.extract_lambda  
  
  # This ensures the Lambda function code will only be updated if the hash of the ZIP file changes
  source_code_hash = data.archive_file.extract_lambda.output_base64sha256

  #Specifies the IAM role that the extract Lambda function will assume when it runs, where there is attached permissions of using other resources
  role             = aws_iam_role.extract_lambda_role.arn

  # Define the entry point of the Lambda function 'extract', which is 'lambda_handler()' inside 'extract.py' 
  handler          = "${var.extract_lambda}.lambda_handler"  
  runtime          = "python3.12"
  timeout          = 120
  
  #Specifies the location of the 'extract/function.zip' uploaded in s3 and use it to create aws lambda function 'extract'
  s3_bucket        = aws_s3_bucket.code_bucket.bucket   
  s3_key           = "${var.extract_lambda}/function.zip"
  
  # specify layers for the aws lambda function; 
  # the first is custom Lambda layer created in terraform, 
  # the second is an existing AWS Lambda Layer for Pandas, 
  # specifically for Python 3.12, source from AWS sdk for pandas, AWS Lambda Managed Layers, 
  layers           = [aws_lambda_layer_version.dependencies.arn,
                      "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:12"]
  
  # ensure the Lambda function won't be deployed until the lambda code and lambda layers are available in S3
  depends_on = [aws_s3_object.lambda_code, aws_s3_object.lambda_layer]

  # Lambda function has environment variables that can be used in lambda function
  environment {
    variables = {
      DATA_INGESTED_BUCKET_NAME = aws_s3_bucket.ingested_data_bucket.id
      SNS_TOPIC_ARN              = data.aws_sns_topic.step_functions_workflow_sns.arn
      KEY_NAME = "ingested_data"
    } 
  }
  # Lambda function has a logging configuration defined as follows
  logging_config {
    log_format = "JSON"
    log_group = aws_cloudwatch_log_group.alapin_extract_log_group.name
    application_log_level = "INFO"
    system_log_level = "DEBUG"

  }
}

// create lambda function with name 'tranform' using the zip file 'transform/function.zip' uploaded in s3 bucket
resource "aws_lambda_function" "workflow_tasks_transform" {
  # defines the lambda function's name in aws, which is used as identifier for lambda functions
  function_name    = var.transform_lambda
  source_code_hash = data.archive_file.transform_lambda.output_base64sha256

  #Specifies the IAM role that the transform Lambda function will assume when it runs, where there is attached permissions of using other resources
  role             = aws_iam_role.transform_lambda_role.arn

  # define the entry point of the Lambda function 'transform', which is 'lambda_handler()' inside 'transform.py' 
  handler          = "${var.transform_lambda}.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120

  #Specifies the location of the 'transform/function.zip' uploaded in s3 and use it to create aws lambda function 'transform'
  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.transform_lambda}/function.zip"
  
  # specify layers for the aws lambda function
  layers           = [aws_lambda_layer_version.dependencies.arn,
                      "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:12"] 
   
  # ensure the Lambda function won't be deployed until the lambda code and lambda layers are available in S3
  depends_on = [aws_s3_object.lambda_code, aws_s3_object.lambda_layer]
  
  # Lambda function has environment variables that can be used in lambda function
  environment {
    variables = {
      DATA_PROCESSED_BUCKET_NAME = aws_s3_bucket.processed_data_bucket.id
      SNS_TOPIC_ARN              = data.aws_sns_topic.step_functions_workflow_sns.arn
      KEY_NAME = "processed_data"
    } 
  }
  

  # Lambda function has a logging configuration defined as follows
  logging_config {
    log_format = "JSON"
    log_group = aws_cloudwatch_log_group.alapin_extract_log_group.name
    application_log_level = "INFO"
    system_log_level = "DEBUG"

  }
}

// create lambda function with name 'load' using the zip file 'load/function.zip' uploaded in s3 bucket
resource "aws_lambda_function" "workflow_tasks_load" {
  function_name    = var.load_lambda
  source_code_hash = data.archive_file.load_lambda.output_sha256
  role             = aws_iam_role.load_lambda_role.arn
  handler          = "${var.load_lambda}.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120


  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.load_lambda}/function.zip"
  
  layers           = [aws_lambda_layer_version.dependencies.arn,
                      "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:12"]


  depends_on = [aws_s3_object.lambda_code]
 
  environment {
    variables = {
      DATA_PROCESSED_BUCKET_NAME = aws_s3_bucket.processed_data_bucket.id
      SNS_TOPIC_ARN              = data.aws_sns_topic.step_functions_workflow_sns.arn
    } 
  }

   logging_config {
    log_format = "JSON"
    log_group = aws_cloudwatch_log_group.alapin_extract_log_group.name
    application_log_level = "INFO"
    system_log_level = "DEBUG"

  }

}
