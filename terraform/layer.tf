// use null_resource to trigger local shell command when the specified files changed, 
//here, the trigger is when the content of the file requirements.txt or the file Makefile changes 
resource "null_resource" "create_dependencies_pandas" {
  provisioner "local-exec" {
    command = "make -C ${path.module}/.. custom-dependencies"
  }

  triggers = {
    requirements_hash = filemd5("${path.module}/../requirements.txt")
    makefile_hash     = filemd5("${path.module}/../Makefile")
  }
}

//zipping the contents of a directory and creating an archive zip file that can be used to upload to s3 and then be used in aws lamdas and when creating lambda layer
data "archive_file" "layer_code" {
  type        = "zip"
  output_path = "${path.module}/../packages/layer/layer.zip"
  source_dir  = "${path.module}/../dependencies"

# comment out depends_on, because want to build the archive layer.zip now
#   depends_on = [null_resource.create_dependencies] 
}

#need iam permission of lambda:CreateLayerVersion, or maybe lambda:DeleteLayerVersion
// creates a Lambda Layer in AWS using the uploaded layer.zip file in s3 bucket
resource "aws_lambda_layer_version" "dependencies" {
  layer_name = "library_layer" 
  s3_bucket  = aws_s3_object.lambda_layer.bucket
  s3_key     = aws_s3_object.lambda_layer.key
  # defines which Python runtimes this layer will be compatible with to avoid any potential error due to runtime version
  compatible_runtimes = ["python3.12"] 
  
}

# #add pndas layer from provided arn
# resource "aws_serverlessapplicationrepository_cloudformation_stack" "aws_sdk_pandas_layer" {
#   name           = "aws-sdk-pandas-layer-py3-12"
#   application_id = "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:12"
#   capabilities = [
#     "CAPABILITY_IAM"
#   ]
# }



