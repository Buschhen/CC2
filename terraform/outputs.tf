output "load_balancer_public_ip" {
  description = "Public IP address of the Load Balancer"
  value       = azurerm_public_ip.lb_ip.ip_address
}

output "vm1_name" {
  description = "Name of the first virtual machine"
  value       = azurerm_linux_virtual_machine.vm1.name
}

output "vm2_name" {
  description = "Name of the second virtual machine"
  value       = azurerm_linux_virtual_machine.vm2.name
}

output "vm1_private_ip" {
  description = "Private IP address of VM1"
  value       = azurerm_network_interface.nic1.private_ip_address
}

output "vm2_private_ip" {
  description = "Private IP address of VM2"
  value       = azurerm_network_interface.nic2.private_ip_address
}

output "resource_group" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "bastion_ip" {
  value = azurerm_public_ip.bastion_public_ip.ip_address
}

output "app_vm_ips" {
  value = jsonencode([
    azurerm_linux_virtual_machine.vm1.private_ip_address,
    azurerm_linux_virtual_machine.vm2.private_ip_address
  ])
}

# output "sql_env_vars" {
#   value = <<EOT
# # SQL_SERVER=${azurerm_mssql_server.main.name}.database.windows.net
# # SQL_DATABASE=${azurerm_mssql_database.documents.name}
# # SQL_USERNAME=${var.sql_admin}
# # SQL_PASSWORD=${var.sql_password}
# EOT

#   sensitive = true
# }

# output "blob_env_vars" {
#   value = <<EOT
# AZURE_CONNECTION_STRING=${azurerm_storage_account.docs.primary_connection_string}
# BLOB_CONTAINER_NAME=documents
# EOT
#   sensitive = true
# }

# output "sql_server_name" {
#   value = azurerm_mssql_server.main.name
# }

# output "sql_server_fqdn" {
#   value = azurerm_mssql_server.main.fully_qualified_domain_name
# }

# output "sql_database_name" {
#   value = azurerm_mssql_database.documents.name
# }

# output "sql_admin_login" {
#   value = azurerm_mssql_server.main.administrator_login
# }

# output "sql_admin_password" {
#   value     = var.sql_password
#   sensitive = true
# }

# output "sqlalchemy_connection_string" {
#   value = "mssql+pyodbc://${azurerm_mssql_server.main.administrator_login}:${var.sql_password}@${azurerm_mssql_server.main.fully_qualified_domain_name}/${azurerm_mssql_database.documents.name}?driver=ODBC+Driver+17+for+SQL+Server"
#   sensitive = true
# }

output "azure_blob_connection_string" {
  value     = azurerm_storage_account.docs.primary_connection_string
  sensitive = true
}

output "storage_container_name" {
  value = azurerm_storage_container.pdfs.name
}
