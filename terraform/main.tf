provider "aws" {
  profile = "default"
  region  = vars.region
}

resource "aws_s3_bucket" "gibson" {
  bucket  = "instruments-data-gibson"
  acl     = "private"
}

resource "aws_glacier_vault" "gibson" {
  name = "instruments-raw-gibson"
}

resource "aws_docdb_cluster" "gibson" {
  cluster_identifier = "instruments-gibson-cluster"
  master_username    = vars.docdb_username
  master_password    = vars.docdb_password
}

resource "aws_docdb_cluster_instance" "gibson" {
  identifier         = "instruments-gibson-instance"
  cluster_identifier = aws_docdb_cluster.gibson.id
  instance_class     = vars.docdb_instance
}

resource "aws_instance" "gibson" {
  ami             = vars.amis[vars.region]
  instance_type   = vars.ec2_instance

  provisioner "remote-exec" {
    script = "remote.sh"
  }
}
