# Terraform-modul for Monitorering av Key Vault og App Insights

Denne modulen automatiserer oppsettet av monitorering for Bufdirno-ressurser i Azure. Den inkluderer Application Insights, varsling via e-post (Action Groups), alarmer for utløpende secrets i Key Vault, og Event Grid-integrasjon.

## Ressurser som opprettes

1.  **Application Insights**: Koblet til en eksisterende Log Analytics Workspace.
2.  **Action Group**: En gruppe for mottakere av varsler (e-post).
3.  **Log Search Alert**: En alarm som kjører daglig og sjekker etter secrets i Key Vault som nærmer seg utløpsdato (`SecretNearExpiry`).
4.  **Event Grid System Topic & Subscription**: Lytter på hendelser fra Key Vault (`SecretNearExpiry` og `SecretExpired`) for å muliggjøre automatisert håndtering eller utvidet varsling.

## Forutsetninger

-   **Terraform** (v1.0+)
-   **Azure CLI** (innlogget med `az login`)
-   Eksisterende **Log Analytics Workspace** (ID trengs som input).
-   Eksisterende **Key Vault** (ID trengs som input).

## Variabler

| Navn | Type | Beskrivelse | Standard |
| :--- | :--- | :--- | :--- |
| `project_name` | `string` | Navn på prosjektet (brukes som prefiks for ressurser) | `bufdirno` |
| `environment` | `string` | Miljø (f.eks. `prod`, `test`, `dev`) | `prod` |
| `location` | `string` | Azure region | `Norway East` |
| `resource_group_name` | `string` | Navnet på ressursgruppen der overvåkingen skal ligge | - |
| `log_analytics_workspace_id` | `string` | Resource ID til eksisterende Log Analytics Workspace | - |
| `key_vault_id` | `string` | Resource ID til Key Vault som skal overvåkes | - |
| `alert_email_addresses` | `list(string)` | Liste over e-postadresser som skal motta varsler | `[]` |

## Bruk

### Alternativ 1: Bruk utrullingsskriptet (Anbefalt)
Det er laget et PowerShell-skript som forenkler utrullingen ved å hente nødvendige ID-er automatisk. Skriptet støtter miljøvalg via `-Environment` parameteren.

```powershell
# For prod (standard)
./scripts/deploy-monitoring.ps1 -ResourceGroupName "rg-bufdirno-prod" -KeyVaultName "kv-bufdirno-prod" -Emails "admin@example.com"

# For test
./scripts/deploy-monitoring.ps1 -ResourceGroupName "rg-bufdirno-test" -KeyVaultName "kv-bufdirno-test" -Environment "test" -Emails "test-varsling@example.com"
```

### Alternativ 2: Manuelt med Terraform
Hvis du vil kjøre Terraform manuelt for ulike miljøer, anbefales det å bruke `.tfvars`-filer for å holde konfigurasjonene separert.

1.  Initialiser:
    ```bash
    terraform init
    ```

2.  Opprett en miljøspesifikk fil, f.eks. `test.tfvars`:
    ```hcl
    project_name               = "bufdirno"
    environment                = "test"
    resource_group_name        = "rg-test"
    log_analytics_workspace_id = "/subscriptions/.../workspaces/log-test"
    key_vault_id               = "/subscriptions/.../vaults/kv-test"
    alert_email_addresses      = ["test-varsling@bufdir.no"]
    ```

3.  Planlegg og kjør med variabel-filen:
    ```bash
    terraform plan -var-file="test.tfvars" -out=test.tfplan
    terraform apply test.tfplan
    ```

## Håndtering av Miljøer (Best Practice)
For å bruke dette i flere miljøer (dev, test, prod):
- **Variabler**: Bruk `environment` variabelen aktivt. Den brukes som prefiks/suffiks på ressursnavn for å unngå kollisjoner.
- **Backend**: Ved bruk i en CI/CD pipeline (f.eks. GitHub Actions eller Azure DevOps), bør du konfigurere en "remote backend" (Azure Storage Account) for Terraform state, og bruke forskjellige state-filer eller "workspaces" for hvert miljø.

## Outputs

-   `application_insights_instrumentation_key`: Nøkkel for å koble applikasjoner til App Insights.
-   `application_insights_connection_string`: Connection string for App Insights (anbefalt fremfor instrumentation key).
-   `action_group_id`: ID-en til Action Group-en som ble opprettet.
