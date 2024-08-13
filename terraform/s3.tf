resource "aws_s3_bucket" "ingested_data_bucket" {
  bucket_prefix = "nc-de-totesys-ingested-data-"
}

resource "aws_s3_bucket" "processed_data_bucket" {
  bucket_prefix = "nc-de-totesys-processed-data-"
}

resource "aws_s3_bucket" "code_bucket" {
  bucket_prefix = "nc-de-totesys-code-"
}

#need permission of uploading objects; s3:PutObject
resource "aws_s3_object" "lambda_layer" {
  bucket = aws_s3_bucket.code_bucket.bucket
  key    = "layer/layer.zip"
  source = data.archive_file.layer_code.output_path
  
  etag   = filemd5(data.archive_file.layer_code.output_path)

  depends_on = [ data.archive_file.layer_code ]
  
}