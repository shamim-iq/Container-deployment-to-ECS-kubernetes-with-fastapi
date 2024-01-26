# Container Deployment to ECS and Kubernetes with FastAPI

## Overview

This project demonstrates deploying containers on Kubernetes (Minikube) using a FastAPI application. Follow the steps below to set up and deploy containers.

## Step-by-Step Guide

1. **Launch an EC2 Instance:**
    - Launch a "t2.medium" Ubuntu instance with 15GB storage.

2. **Update and Clone Repository:**
    - SSH into the instance and run the following commands:
      ```bash
      sudo apt update && sudo apt upgrade -y
      git clone https://github.com/shamim-iq/Container-deployment-to-ECS-kubernetes-with-fastapi.git
      cd Container-deployment-to-ECS-kubernetes-with-fastapi
      ```

3. **Install Dependencies:**
    - Install the below-mentioned dependencies:
        - python3
        - python3-pip
        - kubectl
        - docker
        - minikube
        - aws-cli
        - terraform

4. **Relogin to the Instance:**
    - Exit and Log back into the instance to use docker commands without "sudo".

5. **Start Minikube:**
    - Run the following command to start Minikube:
      ```bash
      minikube start --driver=docker
      ```

6. **Create IAM Role and Configure AWS CLI:**
    - Create an IAM role with necessary permissions for Terraform and ECS.
    - Generate "AWS Access Key ID" and "AWS Secret Access Key" and run:
      ```bash
      aws configure
      ```

7. **Install Python Requirements:**
    - Run the following command to install Python requirements:
      ```bash
      pip install -r requirements.txt
      ```

8. **Run FastAPI Application:**
    - Run the FastAPI application in the background:
      ```bash
      nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
      ```

9. **Set Kubeconfig Path:**
    - Set the Kubeconfig path as an environment variable:
      ```bash
      export kubeconfig_path=/home/ubuntu/.kube/config
      ```

10. **Deploy to Minikube:**
    - Run the following command to deploy to Minikube:
      ```bash
      curl -X POST "http://<instance_public_ip>:8000/k8s-deploy" -H "Content-Type: application/json" -d '{
              "kubeconfig_path": "/home/ubuntu/.kube/config",
              "cluster_name": "minikube",
              "region": "local",
              "container_image": "nginx:latest",
              "port": 80
          }'
      ```

11. **Validate Minikube Deployment:**
    - Run the following command to validate successful deployment:
      ```bash
      kubectl get pods
      ```

12. **Initialize Terraform:**
    - Run the following commands to initialize Terraform:
      ```bash
      terraform init
      ```

13. **Deploy ECS Cluster:**
    - Run the following commands to deploy ECS cluster and infrastructure:
      ```bash
      terraform apply -auto-approve
      ```

14. **Deploy to ECS:**
    - Run the following command to deploy to ECS:
      ```bash
      curl -X POST "http://<instance_public_ip>:8000/ecs-deploy" -H "Content-Type: application/json" -d '{
              "aws_access_key_id": "<your_access_key_id>",
              "aws_secret_access_key": "<your_secret_access_key_id>",
              "aws_region": "us-east-1",
              "ecs_cluster_name": "<ecs_cluster_name>",
              "container_image": "nginx:latest",
              "port": 80
          }'
      ```

15. **Access Deployed Container:**
    - Navigate to the AWS ECS Console and locate the task associated with your ECS cluster.
    - Access the deployed container using the Fargate public IP associated with the task.

## Tips:

- Install "net-tools" and run "netstat -nptl" to check active ports.
- Store the ".kube/config" file in a secure location.
- Validate Terraform code using "terraform validate" before deploying.
- Use "terraform plan" to review deployable resources before applying changes.
