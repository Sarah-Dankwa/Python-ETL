variable "extract_lambda" {
  type    = string
  default = "extract"
}

variable "transform_lambda" {
  type    = string
  default = "transform"
}

variable "state_machine_name" {
  type    = string
  default = "totesys-workflow-"
}
