terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}
##todo nic into one with count

provider "azurerm" {
  features {}

  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
  subscription_id = var.subscription_id


}
# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# Virtual Network and Subnet
resource "azurerm_virtual_network" "main" {
  name                = "vnet-main"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "main" {
  name                 = "subnet-main"
  address_prefixes     = ["10.0.1.0/24"]
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name

  service_endpoints = ["Microsoft.Storage"]
}

# NSG
resource "azurerm_network_security_group" "web_nsg" {
  name                = "web-nsg"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

    security_rule {
    name                       = "AllowHTTP80"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowSSH"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}
# Associate the Network Security Group to the subnet
resource "azurerm_subnet_network_security_group_association" "assoc" {
  subnet_id                 = azurerm_subnet.main.id
  network_security_group_id = azurerm_network_security_group.web_nsg.id
}

resource "azurerm_network_security_group" "bastion_nsg" {
  name                = "bastion-nsg"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*" # or restrict to your IP for better security
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface_security_group_association" "bastion_nic_nsg" {
  network_interface_id      = azurerm_network_interface.bastion_nic.id
  network_security_group_id = azurerm_network_security_group.bastion_nsg.id
}



# Public IP for Load Balancer
resource "azurerm_public_ip" "lb_ip" {
  name                = "lb-public-ip"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# Load Balancer
resource "azurerm_lb" "main" {
  name                = "web-lb"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"

  frontend_ip_configuration {
    name                 = "PublicIPAddress"
    public_ip_address_id = azurerm_public_ip.lb_ip.id
  }
}

resource "azurerm_lb_backend_address_pool" "pool" {
  name                = "backend-pool"
  loadbalancer_id     = azurerm_lb.main.id
}

resource "azurerm_lb_probe" "http" {
  name                = "http-probe"
  loadbalancer_id     = azurerm_lb.main.id
  protocol            = "Http"
  port                = 8080
  request_path        = "/"
  interval_in_seconds = 5
  number_of_probes    = 2
}

resource "azurerm_lb_rule" "http" {
  name                           = "http-rule"
  loadbalancer_id                = azurerm_lb.main.id
  protocol                       = "Tcp"
  frontend_port                  = 80
  backend_port                   = 8080
  frontend_ip_configuration_name = "PublicIPAddress"
  backend_address_pool_ids        = [azurerm_lb_backend_address_pool.pool.id]
  probe_id                       = azurerm_lb_probe.http.id
}

# Web Server NICs
resource "azurerm_network_interface" "nic1" {
  name                = "nic-1"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_network_interface" "nic2" {
  name                = "nic-2"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Add NICs to backend pool
resource "azurerm_network_interface_backend_address_pool_association" "nic1_assoc" {
  network_interface_id    = azurerm_network_interface.nic1.id
  ip_configuration_name   = "internal"
  backend_address_pool_id = azurerm_lb_backend_address_pool.pool.id
}

resource "azurerm_network_interface_backend_address_pool_association" "nic2_assoc" {
  network_interface_id    = azurerm_network_interface.nic2.id
  ip_configuration_name   = "internal"
  backend_address_pool_id = azurerm_lb_backend_address_pool.pool.id
}

# Linux VMs
resource "azurerm_linux_virtual_machine" "vm1" {
  name                = "web-vm-1"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  size                = "Standard_B1s"
  admin_username      = var.admin_username
  network_interface_ids = [azurerm_network_interface.nic1.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}

resource "azurerm_linux_virtual_machine" "vm2" {
  name                = "web-vm-2"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  size                = "Standard_B1s"
  admin_username      = var.admin_username
  network_interface_ids = [azurerm_network_interface.nic2.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}



resource "azurerm_linux_virtual_machine" "bastion" {
  name                = "bastion"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  size                = "Standard_B1s"
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.bastion_nic.id
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }
}

resource "azurerm_public_ip" "bastion_public_ip" {
  name                = "bastion-ip"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "bastion_nic" {
  name                = "bastion-nic"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "bastion-nic-config"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.bastion_public_ip.id
  }
}


##############

resource "azurerm_storage_account" "docs" {
  name                     = "docstorage${random_id.rand.hex}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  public_network_access_enabled = true

  network_rules {
    default_action             = "Deny"
    virtual_network_subnet_ids = [azurerm_subnet.main.id]
    bypass                     = ["AzureServices"]
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_container" "pdfs" {
  name                  = "documents"
  storage_account_id  = azurerm_storage_account.docs.id
  container_access_type = "private"
}

# resource "azurerm_mssql_server" "main" {
#   name                         = "sqlserver-${random_id.rand.hex}"
#   resource_group_name          = azurerm_resource_group.main.name
#   location                     = "northeurope"
#   version                      = "12.0"
#   administrator_login          = var.sql_admin
#   administrator_login_password = var.sql_password
#   public_network_access_enabled = true

#   minimum_tls_version = "1.2"
# }

# resource "azurerm_mssql_database" "documents" {
#   name       = "documentsdb"
#   server_id  = azurerm_mssql_server.main.id
#   sku_name   = "Basic"
#   max_size_gb = 2
#   zone_redundant = false
# }

resource "random_id" "rand" {
  byte_length = 2
}


resource "local_file" "secrets_env" {
  content = format(
    <<EOT
SQLALCHEMY_CONNECTION_STRING="mssql+pyodbc://%s:%s@%s/%s?driver=ODBC+Driver+17+for+SQL+Server"
AZURE_BLOB_CONNECTION_STRING="%s"
STORAGE_CONTAINER_NAME="%s"
EOT
    ,
    azurerm_storage_account.docs.primary_connection_string,
    azurerm_storage_container.pdfs.name
  )

  filename = "../env.txt"
}