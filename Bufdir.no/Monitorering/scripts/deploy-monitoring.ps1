<#
.SYNOPSIS
    Setter opp automatisk monitorering for en Bufdirno-modul.
    
.DESCRIPTION
    Dette skriptet automatiserer utrullingen av Terraform-modulen for Application Insights,
    alarmer og Event Grid-overvåking av Key Vault.

.EXAMPLE
    .\deploy-monitoring.ps1 -ResourceGroup "rg-bufdirno-prod" -KeyVaultId "/subscriptions/.../keyVaults/kv-prod"

.EXAMPLE
    .\deploy-monitoring.ps1 -ResourceGroup "rg-bufdirno-test" -KeyVaultId "/subscriptions/.../keyVaults/kv-test" -Environment "test" -AlertEmails "test@example.com"
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory=$true)]
    [string]$KeyVaultId,

    [Parameter(Mandatory=$false)]
    [string]$Environment = "prod",

    [Parameter(Mandatory=$false)]
    [string[]]$AlertEmails = @("vakt@bufdir.no")
)

$TerraformPath = "../terraform"

# Sjekk om Terraform er installert
if (!(Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Error "Terraform er ikke installert. Vennligst installer Terraform før du kjører dette skriptet."
    exit
}

# Hent Log Analytics Workspace ID fra Ressursgruppen (antar det finnes en standard)
Write-Host "Henter Log Analytics Workspace..." -ForegroundColor Cyan
$law = Get-AzOperationalInsightsWorkspace | Where-Object { $_.ResourceGroupName -eq $ResourceGroup } | Select-Object -First 1

if ($null -eq $law) {
    Write-Error "Fant ikke Log Analytics Workspace i ressursgruppen $ResourceGroup. Vennligst opprett en først."
    exit
}

# Forbered Terraform variabler
$lawId = $law.ResourceId
$emailsJson = ConvertTo-Json $AlertEmails -Compress

# Kjør Terraform
Push-Location $TerraformPath

Write-Host "Initialiserer Terraform..." -ForegroundColor Cyan
terraform init

Write-Host "Planlegger endringer..." -ForegroundColor Cyan
terraform plan -var="resource_group_name=$ResourceGroup" `
               -var="log_analytics_workspace_id=$lawId" `
               -var="key_vault_id=$KeyVaultId" `
               -var="environment=$Environment" `
               -var="alert_email_addresses=$emailsJson" `
               -out=tfplan

Write-Host "Ønsker du å utføre disse endringene? (y/n)" -ForegroundColor Yellow
$confirm = Read-Host
if ($confirm -eq 'y') {
    terraform apply tfplan
    Write-Host "Monitorering er satt opp!" -ForegroundColor Green
} else {
    Write-Host "Utrulling avbrutt." -ForegroundColor Red
}

Pop-Location
