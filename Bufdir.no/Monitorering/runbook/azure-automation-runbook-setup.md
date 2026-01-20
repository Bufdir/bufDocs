# Oppsett av Runbooks i Azure

I Azure kan "runbooks" referere til to ting: manuelle prosedyrer (dokumentasjon) eller automatiserte skript (Azure Automation). For Bufdirno anbefaler vi en kombinasjon.

## 1. Manuelle Runbooks (Dokumentasjon)
Dette er Markdown-filer som ligger i kodebasen. Disse "settes opp" i Azure ved å lenke til dem fra varsler (Alerts).

### Slik kobler du en Markdown-runbook til et varsel:
1. Gå til **Azure Monitor** -> **Alerts**.
2. Finn det relevante varselet og velg **Edit**.
3. Under seksjonen **Details**, bruk feltet **Custom properties** eller legg lenken direkte i **Description**.
4. Lim inn URL-en til runbooken (f.eks. til GitHub/Azure DevOps eller der dokumentasjonen er publisert).
5. Når varselet trigges, vil lenken være direkte tilgjengelig for den som mottar varselet.

---

## 2. Automatiserte Runbooks (Azure Automation)
Hvis du ønsker at Azure skal utføre en handling automatisk (f.eks. restarte en App Service eller tømme en kø), bruker du **Azure Automation Account**.

### Slik setter du opp en automatisert runbook:

#### Steg 1: Opprett Azure Automation Account
1. Søk etter **Automation Accounts** i Azure Portal.
2. Opprett en ny konto (velg samme region som resten av infrastrukturen).
3. Sørg for at den har en **Managed Identity** (system-assigned) for å få tilgang til ressursene.

#### Steg 2: Opprett selve Runbooken
1. Inne i Automation Account, gå til **Runbooks** -> **Create a runbook**.
2. Gi den et navn (f.eks. `Restart-Newsletter-Api`).
3. Velg **Runbook type**: `PowerShell` (anbefalt) eller `Python`.
4. Velg **Runtime version**: `7.2` (for PowerShell).

#### Steg 3: Skriv koden
Her er et eksempel på en PowerShell-runbook som restarter en App Service:

```powershell
param (
    [Parameter (Mandatory=$false)]
    [object] $WebhookData
)

# Logg inn med Managed Identity
Connect-AzAccount -Identity

# Definer ressurser
$ResourceGroupName = "rg-bufdirno-prod"
$WebAppName = "app-bufdirno-newsletter"

Write-Output "Starter restart av $WebAppName..."
Restart-AzWebApp -ResourceGroupName $ResourceGroupName -Name $WebAppName
Write-Output "Restart fullført."
```

#### Steg 4: Publiser og test
1. Trykk **Save** og deretter **Test pane** for å verifisere at den fungerer.
2. Når den fungerer, trykk **Publish**.

---

## 3. Triggering av Runbook fra varsler (Alerts)
For å kjøre en automatisert runbook når et varsel går, må du bruke en **Action Group**.

1. Gå til **Monitor** -> **Alerts** -> **Action Groups**.
2. Opprett eller rediger en Action Group.
3. Under fanen **Actions**:
    - **Action type**: Velg `Automation Runbook`.
    - **Details**: Velg din Automation Account og runbooken du opprettet.
    - Velg om den skal kjøre i `User` eller `System` kontekst (Managed Identity er best).
4. Lagre Action Group og koble den til varslingsregelen din.

## Oppsummering: Hva skal jeg velge?
*   **Velg Manuell (Markdown)** for komplekse feilsøkingssituasjoner som krever menneskelig vurdering.
*   **Velg Automatisert (Azure Automation)** for kjente problemer som kan løses med enkle kommandoer (f.eks. "hvis køen er full, øk skalering" eller "hvis tjenesten henger, restart").
