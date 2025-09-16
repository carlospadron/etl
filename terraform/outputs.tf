output "cluster_endpoint" {
  value = aws_rds_cluster.aurora_pg.endpoint
}

output "reader_endpoint" {
  value = aws_rds_cluster.aurora_pg.reader_endpoint
}

output "master_username" {
  value = var.master_username
}

output "master_password" {
  value     = var.master_password
  sensitive = true
}
