# Database:

1. dotnet tool restore
2. dotnet ef database update -p .\Infrastructure\Infrastructure.csproj -s .\Api\Api.csproj

#KeyVault:

AzureKeyVaultEnabled = true/false
AzureKeyVaultName = keyvaultnavn

##Lokalt:
Sett følgende enviroment-variabler
- AZURE_CLIENT_ID": <app-reg-som-har-tilgang-til-keyvault>,
- AZURE_TENANT_ID": <tenantid>,
- AZURE_CLIENT_SECRET": <hemmelig>

f.eks :
setx AZURE_TENANT_ID "1234-abc"


Du kan også skru av key-vault og bruke user-secrets isteden

##Azure:
Bruk KeyVault med managed identity

##Andre miljøer
Sett følgende enviroment-variabler
- AZURE_CLIENT_ID": <app-reg-som-har-tilgang-til-keyvault>,
- AZURE_TENANT_ID": <tenantid>,
- AZURE_CLIENT_SECRET": <hemmelig>

# CI/CD with Nuke
 Nuke is a .NET tool used in the repository pipeline for automate build, test and deployment processes.
 It allows the pipeline logic to be debugged locally before deployment to Azure DevOps. The output from Nuke is a .yml file
 that is executed by the pipeline where Nuke logic runs as an .NET console application.

 ## Getting started
 1. Install the Nuke .NET tool
	```powershell
	dotnet tool install Nuke.GlobalTool --global
	```
 ## Run Nuke locally
 Nuke provides developers with the ability to debug the pipeline on their local environment before deploying it to Azure DevOps. 
 It's important to note that certain targets/steps within the pipeline are protected against local executions. 
 This safeguard is in place to prevent deployments to environments that should only be updated through pipeline execution on Azure DevOps.

When new targets are added or when specific Azure DevOps logic is modified, Nuke must be executed locally to regenerate the `azure-pipelines.yml` file. 
This can be accomplished in several ways, for example, by running the following command from the root of the repository: `nuke --help`.

To run the pipeline locally, you can initiate it by executing the following command from the repository's root: `nuke`. 
When running it locally, secrets are retrieved from the encrypted file `parameters.local.json` rather than the pipeline itself. 
You'll be prompted to enter a password for decrypting these secrets.

Important Note: When invoking Nuke, the `azure-pipelines.yml` file is regenerated, which means any manual changes made to the file will be overwritten
 
 ## Debugging
 The pipeline logic can be debugged locally, just like any other .NET project.
	
 ## Manual changes to azure-piplines.yml
 When Nuke is executed locally, an azure-pipelines.yml file will be automatically generated. Since Nuke does not replace .yml files, 
 developers still need to relate to these files. This means that some logic may need to be added manually for the sake of effectiveness and visual clarity
 in the pipeline.

The following items have been added to the project's .yml file:
 - `NuGetAuthenticate@1` task.
 - Condition for running the `PublishImage` and `DeployImage` jobs. These conditions are not necessary for functional reasons but rather
   for visualization in Azure DevOps to indicate weather the jobs has been executed or not.
 
 ## Additional information
 For more information about Nuke and its functionality, visit the official website: https://nuke.build/.
