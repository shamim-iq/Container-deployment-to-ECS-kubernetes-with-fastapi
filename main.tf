# ecs_cluster.tf
resource "aws_ecs_cluster" "shamim_cluster" {
  name = "shamim-ecs-cluster"  # Set your desired cluster name
}

#Demo Task
resource "aws_ecs_task_definition" "shamim_task" {
  family                   = "shamim-ecs-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"  # Set your desired CPU units at the task level
  memory                   = "512"  # Set your desired memory in MiB at the task level

  container_definitions = jsonencode([{
    name  = "shamim-container"
    image = "nginx:latest"  # Set your desired container image
    portMappings = [{
      containerPort = 80  # Set the port your container listens on
      hostPort      = 80   # Auto-assign a host port
    }]
    memoryReservation = 256  # Set your desired memory reservation in MiB
    cpu               = 256  # Set your desired CPU units (e.g., 256)
  }])
}

resource "aws_ecs_service" "shamim_service" {
  name            = "shamim-ecs-service"
  cluster         = aws_ecs_cluster.shamim_cluster.id
  task_definition = aws_ecs_task_definition.shamim_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets = [aws_subnet.Project_Pub_subnet-1.id, aws_subnet.Project_Pub_subnet-2.id]  # Specify your subnet IDs
    security_groups = [aws_security_group.Project-public_sg.id]  # Specify your security group IDs
    assign_public_ip = true
  }
}
