#!/bin/bash

# Ensure EULA is accepted before installation
export ACCEPT_EULA=Y

# Download and install Microsoft ODBC Driver 18 for SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Update package lists and install ODBC driver
sudo apt-get update
sudo apt-get install -y msodbcsql18

# Verify driver installation
odbcinst -q -d
