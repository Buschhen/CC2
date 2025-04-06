terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "terraformstateds"
    container_name       = "tfstate"
    key                  = "main.tfstate"
  }
}
