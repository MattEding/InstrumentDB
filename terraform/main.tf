provider "aws" {
  region  = var.region
}

# resource "aws_docdb_cluster" "gibson" {
#   cluster_identifier = "instruments-gibson-cluster"
#   master_username    = var.docdb_username
#   master_password    = var.docdb_password
# }

# resource "aws_docdb_cluster_instance" "gibson" {
#   identifier         = "instruments-gibson-instance"
#   cluster_identifier = aws_docdb_cluster.gibson.id
#   instance_class     = var.docdb_instance
# }

resource "aws_security_group" "ssh_inbound" {
  name = var.instance_name

  ingress {
    from_port   = var.ssh_port
    to_port     = var.ssh_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # need for `wget` and `apt-get`
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "webscraper" {
  ami                    = var.ami
  instance_type          = var.ec2_instance
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.ssh_inbound.id]

  tags = {
    Name = var.instance_name
  }

  connection {
    type        = "ssh"
    host        = aws_instance.webscraper.public_ip
    user        = var.ssh_user
    port        = var.ssh_port
    private_key = file(var.private_key)
    timeout     = "1m30s"
  }

  provisioner "remote-exec" {
    inline = ["touch test2.txt"]
  }
}
