variable "region" {}

variable "amis" {
  type = "map"
}

variable "ec2_instance" {
  default = "t2.micro"
}

variable "docdb_instance" {
  default = "db.r5.large"
}

variable "docdb_username" {}

variable "docdb_password" {}

