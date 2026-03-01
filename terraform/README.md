# Terraform Infrastructure for ETL Project

Terraform to provision an AWS Aurora PostgreSQL cluster with two databases: `source` and `target`.

## What this creates
- An RDS Subnet Group
- A Security Group allowing Postgres access from specified CIDR blocks
- An Aurora PostgreSQL Serverless cluster
- The `source` database is created by the cluster on creation
- The `target` database is created by running psql locally via a `local-exec` provisioner

## Prerequisites
- [Terraform](https://www.terraform.io/downloads) >= 1.0
- AWS credentials configured for Terraform (env vars, shared credentials file, or IAM role). IMPORTANT: avoid using the root account for daily operations. If you only have root credentials, consider creating an IAM user with limited permissions and using that instead.
- [PostgreSQL client tools](https://www.postgresql.org/download/) (`psql`) installed locally for the provisioner to create the `target` database
- A VPC with at least 2 subnets in different availability zones

## Important notes
- The configuration will, by default, detect your public IP (via https://checkip.amazonaws.com) and restrict the security group to your IP if you don't provide `allowed_cidr_blocks`. This makes it possible to run `psql` locally without a VPN but be aware of potential IP changes (ISP DHCP) which can lock you out.
- The `allow_public_access` variable controls whether the writer instance is publicly accessible. It defaults to `true` in this template to allow you to connect from your laptop; set it to `false` for production.
- The local-exec runs `psql` from where `terraform apply` is run and requires network access to the cluster. If your machine cannot reach the cluster (for example, cluster in private subnets), the provisioner will fail.
- For production usage you should replace the `local-exec` with an automated migration step run from inside the VPC (bastion, Lambda with VPC access, or CI runner inside the network).

## Quickstart

### 1. Configure Variables

Copy the example variables file and edit it with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and provide:
- Your VPC ID
- At least 2 subnet IDs in different availability zones
- A strong master password

Required variables: `vpc_id`, `subnet_ids`, `master_password`.

### 2. Initialize and apply:

```bash
terraform init
terraform apply
```

### 3. View connection details

After apply completes, outputs show the cluster endpoint:

```bash
terraform output
```

### 4. Seed Data (Optional)

After the infrastructure is created, you can seed the database with data:

```bash
# Get the database endpoint from Terraform output
DB_ENDPOINT=$(terraform output -raw cluster_endpoint)
DB_USER=$(terraform output -raw master_username)
DB_PASSWORD=$(terraform output -raw master_password)

# Run the seeding script
DB_ENDPOINT="$DB_ENDPOINT" \
DB_USER="$DB_USER" \
DB_PASSWORD="$DB_PASSWORD" \
SOURCE_DB="source" \
CSV_FILE="/path/to/osopenuprn_202502.csv" \
./seed-database.sh
```

## Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region | `eu-west-2` | No |
| `aws_profile` | AWS CLI profile | `""` | No |
| `vpc_id` | VPC ID | - | Yes |
| `subnet_ids` | List of subnet IDs | - | Yes |
| `allowed_cidr_blocks` | CIDR blocks for access | Your IP | No |
| `master_username` | Master DB username | `masteruser` | No |
| `master_password` | Master DB password | - | Yes |
| `primary_database_name` | Source database name | `source` | No |
| `target_database_name` | Target database name | `target` | No |
| `serverless_min_capacity` | Min ACUs | `2` | No |
| `serverless_max_capacity` | Max ACUs | `8` | No |

See `variables.tf` for complete list of variables.

## Using with Makefile

From the project root directory, you can use the Makefile:

```bash
# Initialize Terraform
make terraform-init

# Plan changes
make terraform-plan

# Apply changes
make terraform-apply

# Show outputs
make terraform-output

# Destroy infrastructure
make terraform-destroy
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will permanently delete the Aurora cluster and all data.
