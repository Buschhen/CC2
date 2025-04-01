# Azure region (location)
variable "location" {
  description = "Azure region for resource deployment"
  type        = string
  default     = "westeurope"
}

# Resource group name
variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "ai-search-rg"
}

# VM admin username
variable "admin_username" {
  description = "Admin username for the Linux virtual machines"
  type        = string
  default     = "azureuser"
}

# Path to your public SSH key
variable "ssh_public_key_path" {
  description = "Path to the SSH public key file"
  type        = string
  default     = "~/.ssh/azure_p.pub"
}
