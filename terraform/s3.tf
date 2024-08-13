resource "aws_s3_bucket" "ingested_data_bucket" {
  bucket_prefix = "nc-de-totesys-ingested-data-"
}

resource "aws_s3_bucket" "processed_data_bucket" {
  bucket_prefix = "nc-de-totesys-processed-data-"
}