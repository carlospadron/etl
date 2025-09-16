Terraform to provision an AWS Aurora PostgreSQL cluster with two databases: `source` and `target`.

What this creates
- An RDS Subnet Group
- A Security Group allowing Postgres access from specified CIDR blocks
- An Aurora PostgreSQL cluster (writer instance)
- The `source` database is created by the cluster on creation
- The `target` database is created by running psql locally via a `local-exec` provisioner

Prerequisites
- AWS credentials configured for Terraform (env vars, shared credentials file, or IAM role). IMPORTANT: avoid using the root account for daily operations. If you only have root credentials, consider creating an IAM user with limited permissions and using that instead.
- `psql` CLI installed locally for the provisioner to create the `target` database

Important notes
- The configuration will, by default, detect your public IP (via https://checkip.amazonaws.com) and restrict the security group to your IP if you don't provide `allowed_cidr_blocks`. This makes it possible to run `psql` locally without a VPN but be aware of potential IP changes (ISP DHCP) which can lock you out.
- The `allow_public_access` variable controls whether the writer instance is publicly accessible. It defaults to `true` in this template to allow you to connect from your laptop; set it to `false` for production.
- The local-exec runs `psql` from where `terraform apply` is run and requires network access to the cluster. If your machine cannot reach the cluster (for example, cluster in private subnets), the provisioner will fail.
- For production usage you should replace the `local-exec` with an automated migration step run from inside the VPC (bastion, Lambda with VPC access, or CI runner inside the network).

Quickstart
1. Edit `terraform/terraform.tfvars` or pass variables when running Terraform. Required variables: `vpc_id`, `subnet_ids`, `master_password`.
2. Initialize and apply:

   terraform init
   terraform apply

3. After apply completes, outputs show the cluster endpoint. Use psql or your client to connect.
