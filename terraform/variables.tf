variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-2"
}

variable "aws_profile" {
  description = "AWS CLI/profile name to use for provider and local-exec commands (optional). If empty, relies on default credential chain or AWS_PROFILE env var."
  type        = string
  default     = ""
}

variable "vpc_id" {
  description = "VPC id where Aurora will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for DB subnet group (at least 2)" 
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to connect to the DB (default: your IP)"
  type        = list(string)
  default     = []
}

variable "db_subnet_group_name" {
  description = "Name for DB subnet group"
  type        = string
  default     = "aurora-subnet-group"
}

variable "cluster_identifier" {
  description = "RDS cluster identifier"
  type        = string
  default     = "etl-aurora-cluster"
}

variable "engine_version" {
  description = "Aurora PostgreSQL engine version"
  type        = string
  default     = "17.4"
}

variable "master_username" {
  description = "Master DB username"
  type        = string
  default     = "masteruser"
}

variable "master_password" {
  description = "Master DB password"
  type        = string
  sensitive   = true
}

variable "primary_database_name" {
  description = "First database created by RDS cluster"
  type        = string
  default     = "source"
}

variable "target_database_name" {
  description = "Second database to create via psql"
  type        = string
  default     = "target"
}

variable "allow_public_access" {
  description = "If true, the writer instance will be created as publicly accessible and the security group will allow access from your public IP if `allowed_cidr_blocks` is empty. Use with caution."
  type        = bool
  default     = true
}

variable "serverless_auto_pause" {
  description = "Enable auto-pause for Aurora Serverless"
  type        = bool
  default     = true
}

variable "serverless_min_capacity" {
  description = "Minimum ACUs for serverless cluster (Aurora Serverless uses capacity units)"
  type        = number
  default     = 2
}

variable "serverless_max_capacity" {
  description = "Maximum ACUs for serverless cluster"
  type        = number
  default     = 8
}

variable "serverless_seconds_until_auto_pause" {
  description = "Seconds of inactivity before auto-pausing"
  type        = number
  default     = 300
}
