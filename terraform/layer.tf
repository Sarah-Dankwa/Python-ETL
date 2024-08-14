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

