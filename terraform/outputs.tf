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

output "resource_group" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}
