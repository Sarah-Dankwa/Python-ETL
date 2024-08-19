variable "extract_lambda" {
  type    = string
  default = "extract"
}

variable "transform_lambda" {
  type    = string
  default = "transform"
}

variable "load_lambda" {
  type    = string
  default = "load"
}

variable "state_machine_name" {
  type    = string
  default = "totesys-workflow-"
}

variable "metric_namespace" {
  type = string
  default = "alapin_extract_metric"
}

variable "alarm_name" {
  type = string
  default = "terraform-extract-metric-alarm"
}