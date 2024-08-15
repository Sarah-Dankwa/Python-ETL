# Set up lambda block in terraform to 
# point to local code file and add layers or enviroment variables where needed.

data "archive_file" "extract_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/extract/function.zip"
  source_file = "${path.module}/../src/extract.py"
}

data "archive_file" "transform_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/transform/function.zip"
  source_file = "${path.module}/../src/transform.py"
}

data "archive_file" "load_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/load/function.zip"
  source_file = "${path.module}/../src/load.py"
}

resource "aws_lambda_function" "workflow_tasks_extract" {
  function_name    = var.extract_lambda
  source_code_hash = data.archive_file.extract_lambda.output_base64sha256
  role             = aws_iam_role.lambda_role.arn
  handler          = "${var.extract_lambda}.lambda_handler"
  runtime          = "python3.12"
  timeout          = 60

  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.extract_lambda}/function.zip"
  
  layers           = [aws_lambda_layer_version.dependencies.arn]

  depends_on = [aws_s3_object.lambda_code, aws_s3_object.lambda_layer]

  environment {
    variables = {
      DATA_INGESTED_BUCKET_NAME = aws_s3_bucket.ingested_data_bucket.id
    # DATA_PROCESSED_BUCKET_NAME = aws_s3_bucket.processed_data_bucket.id

      KEY_NAME = "ingested_data"
    } 
  }

  logging_config {
    log_format = "JSON"
    log_group = aws_cloudwatch_log_group.alapin_extract_log_group.name
    application_log_level = "INFO"
    system_log_level = "DEBUG"

  }
}

resource "aws_lambda_function" "workflow_tasks_transform" {
  function_name    = var.transform_lambda
  source_code_hash = data.archive_file.transform_lambda.output_base64sha256
  role             = aws_iam_role.lambda_role.arn
  handler          = "${var.transform_lambda}.lambda_handler"
  runtime          = "python3.12"

  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.transform_lambda}/function.zip"

  depends_on = [aws_s3_object.lambda_code]

  environment {
    variables = {
      DATA_PROCESSED_BUCKET_NAME = aws_s3_bucket.processed_data_bucket.id
      KEY_NAME = "processed_data"
    } 
  }

   logging_config {
    log_format = "JSON"
    log_group = aws_cloudwatch_log_group.alapin_extract_log_group.name
    application_log_level = "INFO"
    system_log_level = "DEBUG"

  }
}

resource "aws_lambda_function" "workflow_tasks_load" {
  function_name    = var.load_lambda
  source_code_hash = data.archive_file.load_lambda.output_sha256
  role             = aws_iam_role.lambda_role.arn
  handler          = "${var.load_lambda}.lambda_handler"
  runtime          = "python3.12"

  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.load_lambda}/function.zip"

  depends_on = [aws_s3_object.lambda_code]

  environment {
    variables = {
      DATA_PROCESSED_BUCKET_NAME = aws_s3_bucket.processed_data_bucket.id
    } 
  }

   logging_config {
    log_format = "JSON"
    log_group = aws_cloudwatch_log_group.alapin_extract_log_group.name
    application_log_level = "INFO"
    system_log_level = "DEBUG"

  }

}
