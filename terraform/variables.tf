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

variable "client_id" {
  description = "Azure Client ID (Service Principal)"
  type        = string
}

variable "client_secret" {
  description = "Azure Client Secret (Service Principal)"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for VMs"
  type        = string
}


variable "sql_admin" {
  description = "SQL Database login name"
  type        = string
}
variable "sql_password" {
  description = "SQL Database password"
  type        = string
  sensitive   = true
}