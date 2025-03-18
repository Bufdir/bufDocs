# Azure CLI Setup and Login Guide

This guide explains how to install the **Azure CLI (`az`)**, log in to Azure,
and verify your authentication.

## 🚀 Step 1: Install Azure CLI

1. Download the Azure CLI installer from:
   [Azure CLI Download](https://aka.ms/installazurecliwindows)
2. Run the installer and follow the setup instructions.
3. After installation, restart your terminal and verify the installation:
   ```sh
   az --version
   ```

## 🔑 Step 2: Log In to Azure

## ⚙️ Step 3: Run scripts

PS:

The table [dbo].[NotFoundHandler.Suggestions] may have a huge amount of records
and should be truncated before export

```
TRUNCATE TABLE [dbo].[NotFoundHandler.Suggestions];
```

1. Insert password to export-script from keyvault
2. Run export
3. Insert password to import-script from keyvault and bacpacname from
   export-script
4. Run import

After import operations are completed, review the sku/pricing tier and scale to
appropriate tier. Databases created are often created with higher pricing tier
to speed up the import.

# Blobs

To finalize a migration from one enviroment to another we copy the blobcontainer
Use https://azure.microsoft.com/en-us/products/storage/storage-explorer to copy
the container from one storage account to another.

1. Clone blob container into a new container named after the database bacpac
2. Copy/Paste blob container from source to destination storageaccount

# Config

After database are created and imported and the blobs are copied, change the
following config

```
blobcontainername = <nameofcopiedcontainer>
EPiServerDB= <connectionstringofthenewdatabase>
```

# Optimizely config

Log into /EPiServer/EPiServer.Cms.UI.Admin/default#/Configurations/ManageSites
and configure the site
