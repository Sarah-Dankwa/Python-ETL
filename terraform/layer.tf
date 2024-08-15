resource "null_resource" "create_dependencies_pandas" {
  provisioner "local-exec" {
    command = "make -C ${path.module}/.. custom-dependencies"
  }

  triggers = {
    requirements_hash = filemd5("${path.module}/../requirements.txt")
    makefile_hash     = filemd5("${path.module}/../Makefile")
  }
}

data "archive_file" "layer_code" {
  type        = "zip"
  output_path = "${path.module}/../packages/layer/layer.zip"
  source_dir  = "${path.module}/../dependencies"

#   depends_on = [null_resource.create_dependencies] 
}

#need iam permission of lambda:CreateLayerVersion, or maybe lambda:DeleteLayerVersion
resource "aws_lambda_layer_version" "dependencies" {
  layer_name = "pandas_library_layer" 
  s3_bucket  = aws_s3_object.lambda_layer.bucket
  s3_key     = aws_s3_object.lambda_layer.key
}

# #add pndas layer from provided arn
# resource "aws_serverlessapplicationrepository_cloudformation_stack" "aws_sdk_pandas_layer" {
#   name           = "aws-sdk-pandas-layer-py3-12"
#   application_id = "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:12"
#   capabilities = [
#     "CAPABILITY_IAM"
#   ]
# }



