resource "aws_vpc" "Project-VPC" {
  cidr_block = var.cidr_block
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = var.vpc_name
  }
}

resource "aws_subnet" "Project_Pub_subnet-1" {
  vpc_id                  = aws_vpc.Project-VPC.id
  cidr_block              = var.public_subnet_cidr-1
  availability_zone       = "us-east-1a"  # Replace with your desired AZ
  map_public_ip_on_launch = true
  tags = {
    Name = "Project_Pub_subnet-1"
  }
}

resource "aws_subnet" "Project_Pub_subnet-2" {
  vpc_id                  = aws_vpc.Project-VPC.id
  cidr_block              = var.public_subnet_cidr-2
  availability_zone       = "us-east-1b"  # Replace with your desired AZ
  map_public_ip_on_launch = true
  tags = {
    Name = "Project_Pub_subnet-2"
  }
}

resource "aws_internet_gateway" "Project_igw" {
  vpc_id = aws_vpc.Project-VPC.id
  tags = {
    Name = "Project-IGW"
  }
}

resource "aws_route_table" "Project_Pub_subnets_rt" {
  vpc_id = aws_vpc.Project-VPC.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.Project_igw.id
  }

  tags = {
    Name = "Project-Public-Subnets-RT"
  }
}

resource "aws_route_table_association" "Project_Pub_subnet-1_association" {
  subnet_id      = aws_subnet.Project_Pub_subnet-1.id
  route_table_id = aws_route_table.Project_Pub_subnets_rt.id
}

resource "aws_route_table_association" "Project_Pub_subnet-2_association" {
  subnet_id      = aws_subnet.Project_Pub_subnet-2.id
  route_table_id = aws_route_table.Project_Pub_subnets_rt.id
}

resource "aws_security_group" "Project-public_sg" {
  name        = "Project-Public-SG"
  description = "Security group for ECS service"
  vpc_id      = aws_vpc.Project-VPC.id

  # ingress {
  #   from_port = 22
  #   to_port   = 22
  #   protocol  = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  ingress {
  from_port   = 0
  to_port     = 0
  protocol    = "-1"
  cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
