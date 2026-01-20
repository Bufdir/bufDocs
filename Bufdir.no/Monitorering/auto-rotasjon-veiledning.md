# Veiledning for Automatisert Fornyelse (Auto-rotation)

Dette dokumentet beskriver hvordan man implementerer automatisert fornyelse av secrets og sertifikater i Bufdirno-løsningen for å eliminere manuell håndtering og forhindre nedetid.

## 1. Managed Identities (Anbefalt løsning)

Den beste måten å håndtere secrets på er å fjerne behovet for dem helt ved å bruke **Managed Identities**. Dette er i praksis en automatisk administrert identitet i Azure Entra ID (tidligere Azure AD) som tildeles en spesifikk ressurs (f.eks. en App Service eller en Container App).

### Hvorfor er dette uklart?
Tradisjonelt bruker applikasjoner brukernavn/passord eller API-nøkler for å autentisere seg mot databaser eller andre tjenester. Managed Identities fjerner dette mellomleddet. I stedet for at applikasjonen "beviser" hvem den er ved å vise en secret, gjenkjenner Azure ressursen direkte fordi den kjører i et autorisert miljø.

**Fordeler:**
- **Ingen secrets å rotere**: Azure håndterer fornyelse av tokens i bakgrunnen.
- **Ingen secrets i koden**: Du trenger ikke lagre sensitive verdier i `appsettings.json` eller Key Vault.
- **Bedre sikkerhet**: Identiteten er bundet til den spesifikke ressursen i Azure.

### System-assigned vs. User-assigned
Det finnes to typer identiteter du kan bruke:

1.  **System-assigned**: Identiteten er koblet direkte til ressursens livssyklus. Hvis du sletter App Servicen, slettes identiteten. Passer best for enkle scenarioer der én app trenger tilgang til én ressurs.
2.  **User-assigned**: En uavhengig identitet som kan tildeles flere ressurser. Dette er nyttig hvis du har en gruppe mikrotjenester som alle trenger tilgang til den samme Key Vault-en eller Storage-kontoen.

### Slik implementeres det:

#### Steg 1: Aktivering i Azure
- Gå til din **App Service** eller **Container App** i Azure Portal.
- Naviger til **Identity** i menyen.
- Sett **Status** til "On" under fanen "System assigned".

#### Steg 2: Gi rettigheter (RBAC)
Når identiteten er opprettet, må du gi den tilgang til måltjenesten:
- Gå til f.eks. din **Key Vault** -> **Access Control (IAM)** -> **Add role assignment**.
- Velg rollen **Key Vault Secrets User**.
- Velg "Managed Identity" som medlem, og finn din App Service.

#### Steg 3: Bruk i kode
Bruk `Azure.Identity`-biblioteket. `DefaultAzureCredential` vil automatisk prøve å bruke Managed Identity når koden kjører i Azure.

```csharp
// Eksempel: Koble til Key Vault uten secrets
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

var kvUri = "https://ditt-hvelv.vault.azure.net/";
var client = new SecretClient(new Uri(kvUri), new DefaultAzureCredential());

// Du kan nå hente secrets uten å ha en nøkkel selv
KeyVaultSecret secret = await client.GetSecretAsync("MinSecret");
```

#### Eksempel: SQL Server uten passord
I stedet for en connection string med `Password=...`, kan du bruke Managed Identity:

```csharp
// Connection string i appsettings.json:
// "Server=tcp:dinn-server.database.windows.net,1433;Database=fsa-db;Authentication=Active Directory Managed Identity;"

// Entity Framework Core vil nå bruke identiteten til App Servicen for å logge inn.
```

---

## 2. Auto-rotasjon av Key Vault Secrets

For secrets som ikke kan erstattes av Managed Identities (f.eks. databasepassord for eksterne databaser eller API-nøkler), kan Azure Key Vault automatisere rotasjonen ved å sende hendelser til Event Grid, som igjen trigger en Azure Function.

### 2.1 Konseptuell arbeidsflyt
Arbeidsflyten for rotasjon følger normalt dette mønsteret:
1.  **Trigger**: En "Rotation Policy" i Key Vault når sitt intervall (f.eks. 30 dager før utløp).
2.  **Event**: Key Vault sender en `SecretNearExpiry`-hendelse til Azure Event Grid.
3.  **Handler**: En Azure Function (forhåndskonfigurert) mottar hendelsen.
4.  **Rotasjon**:
    - Funksjonen genererer et nytt passord/nøkkel.
    - Funksjonen oppdaterer måltjenesten (f.eks. SQL Server eller SendGrid) med den nye verdien.
    - Funksjonen oppretter en ny versjon av secreten i Key Vault.
5.  **Verifisering**: Funksjonen tester at den nye versjonen fungerer før den markerer rotasjonen som fullført.

### 2.2 Rotasjon av Databasepassord (SQL Server)
Azure har ferdige maler for rotasjon av SQL-passord. Dette krever en "Credential Manager" (Azure Function) som har tilgang til både Key Vault og SQL Server.

**Viktige punkter for Bufdirno:**
- **To-nøkkel system**: For å unngå nedetid under rotasjon, kan man bruke to parallelle brukerkontoer. Funksjonen roterer den ene mens den andre er i bruk.
- **SQL-rettigheter**: Funksjonen må ha `ALTER ANY LOGIN`-rettigheter på SQL-serveren for å kunne endre passord.

### 2.3 Rotasjon av tredjeparts API-nøkler
For tjenester som SendGrid, Make (Dialog) eller andre SaaS-løsninger, må man implementere en skreddersydd Azure Function.

**Eksempel på logikk i Azure Function (Pseudo-kode):**
```csharp
public async Task RotateSendGridKey()
{
    // 1. Generer ny API-nøkkel via SendGrid API
    var newKey = await _sendGridClient.CreateApiKeyAsync("AutoRotatedKey");
    
    // 2. Lagre den nye nøkkelen som en NY VERSJON i Key Vault
    await _keyVaultClient.SetSecretAsync("SendGrid-API-Key", newKey.Value);
    
    // 3. (Valgfritt) Deaktiver den gamle nøkkelen etter 24 timer
}
```

---

## 3. Automatisert fornyelse av SSL/TLS-sertifikater

Manuelle utløp av SSL-sertifikater er en vanlig årsak til nedetid. Bufdirno bør bruke automatiserte løsninger basert på sertifikattype.

### 3.1 Azure Managed Certificates (App Service / Container Apps)
Dette er den foretrukne løsningen for offentlige endepunkter som `bufdir.no` eller subdomener.

**Slik fungerer det:**
- Azure fungerer som din Certificate Authority (CA).
- **Auto-fornyelse**: Azure fornyer automatisk sertifikatet ca. 45 dager før det utløper.
- **Ingen kostnad**: Inkludert i App Service-planen (Basic og oppover).
- **Krav**: Domene-eierskap må bekreftes via CNAME-record i DNS.

### 3.2 Key Vault og App Service-integrasjon
Hvis man bruker sertifikater fra eksterne leverandører (som GlobalSign eller DigiCert) eller wildcard-sertifikater:

1.  **Lagring**: Last opp sertifikatet (PFX) til Key Vault.
2.  **Kobling**: I App Service, velg "Import Key Vault Certificate".
3.  **Sync**: App Service sjekker Key Vault hver 24. time. Hvis en ny versjon av sertifikatet lastes opp til hvelvet, oppdaterer App Service seg automatisk uten restart.
4.  **Auto-fornyelse via CA**: Azure Key Vault har direkte integrasjon med visse leverandører (DigiCert/GlobalSign). Da kan Key Vault selv be om fornyelse fra leverandøren når det nærmer seg utløp.

### 3.3 Overvåking via Availability Tests
Som et ekstra sikkerhetsnett bør alle moduler ha en **Custom SSL Test** i Application Insights. Denne sjekker selve endepunktet og varsler hvis sertifikatet som presenteres i browseren er i ferd med å utløpe, uavhengig av hvordan det fornyes.

---

## 4. Oppsett av rotasjons-policy (Bicep-eksempel)

For å sikre at rotasjon faktisk skjer, må man definere en `rotationPolicy` ressurs i Azure. Dette bør gjøres som en del av IaC (Infrastructure as Code) i prosjektets deploy-skript.

### 4.1 Komplett Bicep-eksempel for en Secret

Dette eksempelet viser hvordan man definerer en secret med en tilhørende policy som trigger både rotasjon og varsling.

```bicep
param vaultName string = 'kv-bufdirno-prod'
param secretName string = 'SqlDatabasePassword'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: vaultName
}

resource secret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: secretName
  properties: {
    value: 'InitialPassword123!' // Bør egentlig genereres dynamisk
  }
}

resource secretRotationPolicy 'Microsoft.KeyVault/vaults/secrets/rotationPolicies@2021-11-01-preview' = {
  name: '${vaultName}/${secretName}/default'
  properties: {
    lifetimeActions: [
      {
        action: {
          type: 'Rotate'
        }
        trigger: {
          timeAfterCreate: 'P60D' // Roter hver 60. dag etter opprettelse
        }
      }
      {
        action: {
          type: 'Notify'
        }
        trigger: {
          timeBeforeExpiry: 'P15D' // Varsle 15 dager før utløp hvis noe feiler
        }
      }
    ]
    attributes: {
      expiryTime: 'P90D' // Sett nytt utløp til 90 dager etter rotasjon
    }
  }
  dependsOn: [
    secret
  ]
}
```

### 4.2 Forklaring av tidsformatene (ISO 8601)
- `P60D`: 60 dager (Period 60 Days).
- `P30D`: 30 dager.
- `P15D`: 15 dager.

### 4.3 Krav for at Bicep-policy skal fungere
For at `type: 'Rotate'` i Bicep skal fungere for secrets, må Key Vault være koblet til en Azure Function via Event Grid som faktisk utfører selve rotasjonen i målsystemet. For sertifikater fra støttede utstedere håndteres dette internt av Azure.

---

## Oppsummering og Prioritering

1. **Prio 1**: Bruk **Managed Identities** for alt internt i Azure (SQL, Storage, Key Vault, Service-to-Service).
2. **Prio 2**: Bruk **Azure Managed Certificates** for alle offentlige endepunkter.
3. **Prio 3**: Implementer **Rotation Policies** i Key Vault for kritiske tredjeparts-integrasjoner.
