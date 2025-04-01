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
  value = [
    azurerm_linux_virtual_machine.vm1.private_ip_address,
    azurerm_linux_virtual_machine.vm2.private_ip_address
  ]
}
