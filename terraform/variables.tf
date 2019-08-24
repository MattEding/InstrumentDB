# ---------------------------------------------------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# Define these secrets as environment variables
# ---------------------------------------------------------------------------------------------------------------------

# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY

# ---------------------------------------------------------------------------------------------------------------------
# REQUIRED PARAMETERS
# You must provide a value for each of these parameters.
# ---------------------------------------------------------------------------------------------------------------------

# variable "docdb_username" {
#   description = ""
# }

# variable "docdb_password" {
#   description = ""
# }

# ---------------------------------------------------------------------------------------------------------------------
# OPTIONAL PARAMETERS
# These parameters have reasonable defaults.
# ---------------------------------------------------------------------------------------------------------------------

variable "region" {
  description = "The AWS region to deploy into"
  default     = "us-east-2"
}

variable "instance_name" {
  description = "The Name tag to set for the EC2 Instance."
  default     = "remote-exec-test"
}

variable "security_group_name" {
  description = "The name set for the Security Group."
  default     = "ssh_inbound"
}

variable "ssh_port" {
  description = "The port the EC2 Instance should listen on for SSH requests."
  default     = 22
}

variable "ssh_user" {
  description = "SSH user name to use for remote exec connections."
  default     = "ubuntu"
}

variable "ami" {
  description = "Amazon Machine Image for the EC2 Instance."
  default     = "ami-05c1fa8df71875112"
}

variable "ec2_instance" {
  description = "The EC2 Instance type."
  default     = "t2.micro"
}

# variable "docdb_instance" {
#   description = "DocumentDB instance type"
#   default     = "db.r5.large"
# }

variable "key_pair_name" {
  description = "The EC2 Key Pair to associate with the EC2 Instance for SSH access."
  default     = "aws_key"
}

variable "private_key" {
  description = "The EC2 Key Pair file path."
  default     = "~/.ssh/aws_key.pem"
}
