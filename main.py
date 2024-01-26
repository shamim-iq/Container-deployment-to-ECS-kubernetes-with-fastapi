from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from kubernetes import client, config
import boto3
import os

app = FastAPI()

class KubernetesRequest(BaseModel):
    kubeconfig_path: str
    cluster_name: str
    container_image: str
    port: int

class ECSRequest(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    ecs_cluster_name: str
    container_image: str
    port: int

@app.post("/k8s-deploy")
def deploy_to_kubernetes(request: KubernetesRequest = Body(...)):
    # Validate input
    if not request.kubeconfig_path or not request.cluster_name or not request.container_image or not request.port:
        raise HTTPException(status_code=400, detail="Invalid input. Please provide all required fields.")

    # Set up Kubernetes client configuration using the provided kubeconfig path
    if os.path.isfile(request.kubeconfig_path):
        config.load_kube_config(config_file=request.kubeconfig_path)
    else:
        raise HTTPException(status_code=400, detail="Invalid kubeconfig file path.")

    # Create Kubernetes Deployment object
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name="fastapi-deployment"),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels={"app": "fastapi-app"}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "fastapi-app"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="fastapi-container",
                            image=request.container_image,
                            ports=[client.V1ContainerPort(container_port=request.port)]
                        )
                    ]
                )
            )
        )
    )

    # Deploy to the specified Kubernetes cluster
    try:
        api_instance = client.AppsV1Api()
        api_instance.create_namespaced_deployment(
            namespace="default", body=deployment, pretty=True
        )
        deployment_successful = True
    except Exception as e:
        print(f"Error deploying to Kubernetes: {str(e)}")
        deployment_successful = False

    # Return success or failure response
    if deployment_successful:
        return {"message": "Deployment to Kubernetes successful"}
    else:
        raise HTTPException(status_code=500, detail="Deployment to Kubernetes failed")


@app.post("/ecs-deploy")
def deploy_to_ecs(request: ECSRequest = Body(...)):
    # Validate input
    if not request.aws_access_key_id or not request.aws_secret_access_key or not request.aws_region or not request.ecs_cluster_name or not request.container_image or not request.port:
        raise HTTPException(status_code=400, detail="Invalid input. Please provide all required fields.")

    # Set up AWS credentials
    aws_credentials = {
        'aws_access_key_id': request.aws_access_key_id,
        'aws_secret_access_key': request.aws_secret_access_key,
        'region_name': request.aws_region,
    }

    # Set up ECS client
    ecs_client = boto3.client('ecs', **aws_credentials)

    # Create ECS task definition with hardcoded memory and CPU limits
    task_definition = {
        'containerDefinitions': [
            {
                'name': 'fastapi-nginx-containe',
                'image': request.container_image,
                'portMappings': [{'containerPort': request.port, 'hostPort': request.port}],
                'memory': 512,  # Hardcoded memory limit in MB
                'cpu': 256,  # Hardcoded CPU limit in units
            }
        ],
        'family': 'my-ecs-task',
        'networkMode': 'awsvpc',
        'requiresCompatibilities': ['FARGATE'],
        'cpu': '256',  # Hardcoded task-level CPU limit in units
        'memory': '512',  # Hardcoded task-level memory limit in MB
    }

    response = ecs_client.register_task_definition(**task_definition)

    # Run task on ECS cluster with Fargate launch type
    try:
        response = ecs_client.run_task(
            cluster=request.ecs_cluster_name,
            taskDefinition='my-ecs-task',
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': ["subnet-02e1dcb78d33db279", "subnet-00392ea13243ec893"],  # Specify your subnet IDs
                    'securityGroups': ["sg-0a75dc2b4976cbbfb"],  # Specify your security group IDs
                    'assignPublicIp': 'ENABLED',
                }
            }
        )
        deployment_successful = True
    except Exception as e:
        print(f"Error deploying to ECS: {str(e)}")
        deployment_successful = False

    # Return success or failure response
    if deployment_successful:
        return {"message": "Deployment to ECS successful"}
    else:
        raise HTTPException(status_code=500, detail="Deployment to ECS failed")
