provider "aws" {
    profile = "default"
    region  = vars.region
}

resource "aws_s3_bucket" "gibson" {
    bucket  = "..."
    acl     = "private"

    tags = {
        Name = "gibson jsons"
    }
}

resource "aws_glacier_vault" "gibson" {
    name = "gibson htmls"
}

resource "aws_instance" "gibson" {
    ami             = vars.amis[vars.region]
    instance_type   = "t2.mirco"
    depends_on      = [
        aws_s3_bucket.gibson,
        aws_glacier_vault.gibson,
    ]

    provisioner "remote-exec" {
        script = "gibson_provisioner.sh"
    }

    # provisioner "local-exec" {
    #     command = "echo ${aws_instance.gibson.public_ip} > gibson_ip_address.txt"
    # }
}

resource "aws_eip" "ip" {
    vpc         = true
    instance    = aws_instance.gibson.id
}
