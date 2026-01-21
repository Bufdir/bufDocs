# Automatisering av Monitorering for Secrets og Sertifikater

For å sikre at alle moduler i Bufdirno-økosystemet har konsistent overvåking av secrets og sertifikater, anbefales det å automatisere oppsettet fremfor manuelle steg i Azure Portal. Dette reduserer faren for menneskelige feil og sikrer at nye moduler automatisk blir inkludert.

## 1. Infrastruktur som kode (IaC)

Den mest effektive måten å automatisere på er å inkludere monitoreringsressurser i samme Terraform- eller Bicep-filer som definerer infrastrukturen.

### Bicep Eksempel: Key Vault Diagnostic Settings
Dette sikrer at alle Key Vault-hendelser (inkludert utløp) sendes til Log Analytics.

```bicep
resource kvDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'toLogAnalytics'
  scope: keyVault
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'AuditEvent'
        enabled: true
      }
    ]
  }
}
```

### Terraform Eksempel: Log Search Alert for utløp
Dette automatiserer oppsettet av varsling for alle secrets som utløper om mindre enn 30 dager.

```hcl
resource "azurerm_monitor_scheduled_query_rules_alert" "secret_expiry_alert" {
  name                = "KV-Secret-Near-Expiry"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  action {
    action_group = [azurerm_monitor_action_group.prio1.id]
  }

  data_source_id = azurerm_log_analytics_workspace.main.id
  description    = "Varsler når en secret i Key Vault nærmer seg utløpsdato"
  enabled        = true
  query          = <<-QUERY
    AzureDiagnostics
    | where ResourceProvider == "MICROSOFT.KEYVAULT"
    | where OperationName == "SecretNearExpiry"
    | project TimeGenerated, Resource, ResultSignature, requestUri_s
    QUERY
  severity    = 1
  frequency   = 1440 # Én gang i døgnet
  window_size = 1440
  trigger {
    operator  = "GreaterThan"
    threshold = 0
  }
}
```

### Terraform: Komplett Automatiseringspakke

For en helhetlig automatisering av Application Insights, Alarmer og Event Grid-overvåking av Key Vault, bruk den ferdige Terraform-modulen og utrullingsskriptet:

1.  **Terraform-modul**: Ligger i `./terraform/`. Den setter opp:
    *   Application Insights koblet til Log Analytics.
    *   Action Group for e-postvarsling.
    *   Log Search Alert for secrets som snart utløper.
    *   Event Grid System Topic og Subscription for Key Vault-hendelser.
2.  **Utrullingsskript**: Ligger i `./scripts/deploy-monitoring.ps1`. Dette skriptet forenkler prosessen ved å hente nødvendige ID-er og kjøre Terraform.

Se `./terraform/main.tf` for detaljer om ressursene som opprettes.

## 2. Håndtering av Miljøer

For å bruke automatiseringsskriptene i andre miljøer enn prod (f.eks. test eller dev), støtter både Terraform-modulen og PowerShell-skriptet en `environment` parameter.

### Bruk i andre miljøer:
- **PowerShell**: Bruk `-Environment` flagget.
  ```powershell
  ./scripts/deploy-monitoring.ps1 -ResourceGroup "rg-test" -Environment "test" ...
  ```
- **Terraform**: Bruk variabel-filer (`.tfvars`) for hvert miljø.
  ```bash
  terraform apply -var-file="test.tfvars"
  ```

Dette sikrer at ressursene får riktige navn (f.eks. `bufdirno-test-ai`) og havner i riktig ressursgruppe.

## 3. Azure Policy (Governance)

Azure Policy kan brukes til å "tvinge" frem monitorering på alle ressurser i et abonnement.

- **Policy: "Configure Diagnostic Settings for Key Vault to Log Analytics"**: Denne innebygde policyen sørger for at alle Key Vaults automatisk kobles til Log Analytics ved opprettelse.
- **Custom Policy**: Man kan lage en policy som krever at alle secrets *må* ha en `exp` (expiry) tag satt før de kan lagres.

## 3. Automatisert utrulling med PowerShell

Hvis man har mange eksisterende ressurser som mangler overvåking, kan man bruke et skript for å massepåføre innstillinger.

```powershell
# Finn alle Key Vaults i abonnementet
$kvs = Get-AzKeyVault

foreach ($kv in $kvs) {
    Write-Host "Setter opp overvåking for $($kv.VaultName)..."
    
    # Aktiver Diagnostic Settings
    Set-AzDiagnosticSetting -ResourceId $kv.ResourceId `
                            -WorkspaceId "/subscriptions/.../resourceGroups/.../providers/Microsoft.OperationalInsights/workspaces/felles-log-analytics" `
                            -Enabled $true `
                            -Category "AuditEvent"
}
```

## 4. Automatisert fornyelse (Auto-rotation)

For å fjerne behovet for manuell overvåking og forhindre nedetid, bør man implementere automatisert fornyelse der det er teknisk mulig. Dette dekker:

- **Managed Identities**: Fjerner behovet for Client Secrets for tilgang til Azure-ressurser.
- **Key Vault Rotation Policies**: Automatisk rotasjon av passord og API-nøkler.
- **Azure Managed Certificates**: Automatisk fornyelse av SSL-sertifikater.

Se den detaljerte [veiledningen for auto-rotasjon](./auto-rotasjon-veiledning.md) for konkrete implementasjonssteg og kodeeksempler.

## Oppsummering av fordeler
1. **Konsistens**: Alle moduler følger samme standard.
2. **Skalerbarhet**: Nye moduler er overvåket fra dag én.
3. **Sikkerhet**: Reduserer "blindsoner" i infrastrukturen.
