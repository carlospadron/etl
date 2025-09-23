terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
  # Use profile if provided, otherwise rely on environment/default chain
  dynamic "profile" {
    for_each = var.aws_profile != "" ? [var.aws_profile] : []
    content {
      profile = profile.value
    }
  }
}

data "http" "my_ip" {
  url = "https://checkip.amazonaws.com/"
}

resource "aws_db_subnet_group" "aurora_subnets" {
  name       = var.db_subnet_group_name
  subnet_ids = var.subnet_ids
  tags = {
    Name = "aurora-subnet-group"
  }
}

resource "aws_security_group" "aurora_sg" {
  name        = "aurora-postgres-sg"
  description = "Allow Postgres access"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = length(var.allowed_cidr_blocks) > 0 ? var.allowed_cidr_blocks : [chomp(data.http.my_ip.body) + "/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_rds_cluster" "aurora_pg" {
  cluster_identifier      = var.cluster_identifier
  engine                  = "aurora-postgresql"
  engine_version          = var.engine_version
  database_name           = var.primary_database_name
  master_username         = var.master_username
  master_password         = var.master_password
  db_subnet_group_name    = aws_db_subnet_group.aurora_subnets.name
  vpc_security_group_ids  = [aws_security_group.aurora_sg.id]
  
  # Engine mode serverless for Aurora Serverless v2 (requires supported engine version)
  engine_mode = "serverless"

  scaling_configuration {
    auto_pause               = var.serverless_auto_pause
    min_capacity            = var.serverless_min_capacity
    max_capacity            = var.serverless_max_capacity
    seconds_until_auto_pause = var.serverless_seconds_until_auto_pause
  }

  skip_final_snapshot = true

  tags = {
    Name = "aurora-pg-cluster"
  }
}

// Aurora Serverless does not require cluster instances managed here. Instances are managed by serverless.

resource "null_resource" "create_target_db" {
  # Wait for the cluster endpoint to be available
  depends_on = [aws_rds_cluster.aurora_pg]

  provisioner "local-exec" {
    command = <<'EOT'
#!/usr/bin/env bash
set -euo pipefail

ENDPOINT="${aws_rds_cluster.aurora_pg.endpoint}"
USER="${var.master_username}"
PASS="${var.master_password}"
DB="${var.primary_database_name}"
TARGET="${var.target_database_name}"

export PGPASSWORD="${var.master_password}"

echo "Waiting for ${ENDPOINT}:5432 to accept connections..."
for i in {1..30}; do
  if pg_isready -h "${ENDPOINT}" -p 5432 -U "${USER}" -d "${DB}" >/dev/null 2>&1; then
    echo "Postgres is ready"
    break
  fi
  echo "still waiting... ($i)"
  sleep 10
done

echo "Creating target database if not exists"
psql -h "${ENDPOINT}" -U "${USER}" -p 5432 -d "${DB}" -c "CREATE DATABASE \"${TARGET}\";" || true
EOT
    interpreter = ["/bin/bash", "-c"]
    environment = {
      PGPASSWORD = var.master_password
      # forward AWS profile for aws CLI calls executed by local-exec when set
      AWS_PROFILE = var.aws_profile
      AWS_SDK_LOAD_CONFIG = "1"
    }
  }
}
