variable "app_name" {default = "hydrocron-api"}
variable "db_app_name" {default = "hydrocron-db"}
variable "stage" {}
variable "credentials" {}
variable "profile" { }
variable "vpc_id" {}
variable "private_subnets" {}
variable "docker_tag" {}
variable "default_vpc_sg" {}

variable "default_tags" {
  type = map(string)
  default = {}
}