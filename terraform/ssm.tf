resource "aws_ssm_parameter" "latest-extract" {
  name  = "latest-extract"
  type  = "String"
  value = ""
}