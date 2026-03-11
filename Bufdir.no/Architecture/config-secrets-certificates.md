# Konfigurasjon, Secrets og Sertifikater for Bufdir.no

Dette dokumentet gir en samlet oversikt over hvordan konfigurasjon, hemmeligheter (secrets) og sertifikater håndteres på tvers av alle løsninger under Bufdir.no.

## Innholdsfortegnelse
1. [Overordnet Strategi](#1-overordnet-strategi)
2. [Fellesmønstre og Verktøy](#2-fellesmønstre-og-verktøy)
3. [Detaljert Oversikt over Secrets per Modul](#3-detaljert-oversikt-over-secrets-per-modul)
4. [Sertifikater](#4-sertifikater)
5. [Pipeline og Konfigurasjonsflyt](#5-pipeline-og-konfigurasjonsflyt)
6. [Service Principals for Pipelines](#6-service-principals-for-pipelines)
7. [Oversikt over Utløpsdatoer og Rotering](#7-oversikt-over-utløpsdatoer-og-rotering)
8. [Modulspesifikk Konfigurasjonsflyt](#8-modulspesifikk-konfigurasjonsflyt)
9. [Oversikt over Kritiske Secrets og Sertifikater](#9-oversikt-over-kritiske-secrets-og-sertifikater)

## 1. Overordnet Strategi

Bufdir.no følger en moderne tilnærming til konfigurasjonshåndtering med fokus på sikkerhet, sporbarhet og miljøseparasjon.

- **Konfigurasjon**: Generell applikasjonskonfigurasjon lagres i `appsettings.json`, `.env`-filer eller miljøvariabler.
- **Secrets**: Sensitive data som passord, API-nøkler og tilkoblingsstrenger lagres i **Azure KeyVault** eller **Azure DevOps Variable Groups**.
- **Sertifikater**: SSL/TLS-sertifikater for egendefinerte domener og klientsertifikater for integrasjoner (f.eks. ID-porten) administreres sentralt i Azure.

---

## 2. Fellesmønstre og Verktøy

### 2.1 Azure KeyVault
De fleste .NET-applikasjonene i porteføljen bruker Azure KeyVault for å hente secrets under oppstart. 
- **Tilgang**: Applikasjonene bruker **Managed Identity** for sikker tilgang til KeyVault uten behov for egne hemmeligheter.
- **Navnekonvensjon**: Typisk `kv-bufdirno-[miljø]`.

### 2.2 Azure DevOps Variable Groups
Brukes i Azure Pipelines for å injisere miljøspesifikke verdier under bygging og deploy.
- Eksempler: `stat-content5-test`, `stat-content5-qa`, `stat-content5-prod`.

### 2.3 Miljøseparasjon
Konfigurasjon er strengt separert mellom miljøer:
- **Utvikling (Dev)**: Lokale `.env`-filer eller `appsettings.Development.json`.
- **Test/QA**: Azure-miljøer med egne KeyVaults og ressursgrupper.
- **Produksjon (Prod)**: Strengest tilgangskontroll og isolerte ressurser.

---

## 3. Detaljert Oversikt over Secrets per Modul

### 3.1 Azure AD, ID-porten og Maskinporten (Felles)
| Secret | Beskrivelse | Lokasjon | Utløp |
|--------|-------------|----------|-------|
| `AZURE_CLIENT_SECRET` | Azure AD App Registration hemmelighet | KeyVault | 12-24 mnd |
| `IDPORTEN_CLIENT_SECRET` | ID-porten klient-hemmelighet | KeyVault | Varierer |
| `MASKINPORTEN_JWK_ENCODED` | Base64-kodet JWK for Maskinporten-autentisering | KeyVault / Env | Varierer |
| `EncodedX509NameInKeyVault` | Navn på virksomhetssertifikat i KeyVault | KeyVault | 12-24 mnd |

### 3.2 Integrasjoner og Eksterne API-er
Flere moduler integrerer mot nasjonale fellesløsninger og eksterne tjenester.

#### 3.2.1 Maskinporten & Folkeregisteret (FREG)
Brukt i **bufdirno-fsa** og **utrapporteringsbank**.
- **Secrets**: 
  - `MASKINPORTEN_JWK_ENCODED`: Brukes av Node.js/Next.js for å signere JWT-grants.
  - Virksomhetssertifikat: Brukes av .NET-applikasjoner via `Altinn.ApiClients.Maskinporten`.
- **Konfigurasjon**:
  - `MASKINPORTEN_CLIENT_ID`: Klient-ID registrert hos DigDir.
  - `MASKINPORTEN_SCOPES`: Liste over scopes (f.eks. `folkeregister:deling/offentligmedhjemmel`).
  - `MASKINPORTEN_AUDIENCE`: Endepunkt for Maskinporten (test/prod).

### 3.3 Bufdir.no (Optimizely CMS)
- **Database**: `ConnectionStrings:EPiServerDB`
- **Azure Storage**: `AzureStorageConnectionString`
- **Application Insights**: `APPINSIGHTS_INSTRUMENTATIONKEY`

### 3.4 API-moduler (.NET)
| Modul | Viktige Secrets | KeyVault |
|-------|-----------------|----------|
| **familievern-api** | `dbCon`, `AzureAd:ClientSecret` | `kv-familievernapi` |
| **fosterhjem-api** | `RosApiKey`, `Oslo:ApiKey`, `dbCon` | `kv-bufdirno-[miljø]` |
| **feedback-api** | `SqlConnectionString`, `AzureWebJobsStorage` | App Settings (Secret) |
| **newsletter-api** | `Services:Make:UserId`, `dbCon` | KeyVault |
| **stat-backend** | `CosmosDb:ConnectionString`, `Azure:KeyVaultName` | KeyVault |

### 3.5 CMS-moduler (Strapi / Node.js)
Lagres ofte som miljøvariabler i Azure Container Apps, hentet fra KeyVault under deploy.
- `APP_KEYS`
- `ADMIN_JWT_SECRET`
- `JWT_SECRET`
- `API_TOKEN_SALT`
- `DATABASE_URL` (eller spesifikke host/user/pass variabler)

---

## 4. Sertifikater

### 4.1 SSL/TLS Sertifikater
Alle offentlige endepunkter bruker SSL/TLS-sertifikater utstedt for `bufdir.no` eller underdomener.
- **Håndtering**: Administreres i Azure App Service / Container Apps.
- **Utløp**: Typisk årlig fornyelse.
- **Auto-fornyelse**: Aktivert der det er støttet av Azure.

### 4.2 ID-porten & Maskinporten Sertifikater
For integrasjon med ID-porten og Maskinporten kreves det ofte virksomhetssertifikater eller spesifikke klient-sertifikater.
- **Format**: `.pfx`, `.cer` filer eller JWK.
- **Lagring**: Azure KeyVault som "Certificates" (for pfx) eller "Secrets" (for JWK/Base64).
- **Virksomhetssertifikat**: Maskinporten krever et gyldig virksomhetssertifikat for å autentisere organisasjonen.
- **JWK (JSON Web Key)**: Alternativ til sertifikat-filer, spesielt i Node.js-løsninger.

---

## 5. Pipeline og Konfigurasjonsflyt

### 5.1 CI/CD Flyt
1. **Build**: Applikasjonen bygges. Miljønøytral i de fleste tilfeller.
2. **Deploy**:
   - Azure Pipeline henter variabler fra **Variable Groups**.
   - Variabler mappes til **Application Settings** i Azure (App Service / Container App).
   - Ved oppstart kobler applikasjonen seg til **Azure KeyVault** (via Managed Identity) for å hente faktiske secrets.

### 5.2 Eksempel: Azure Pipelines Mapping
```yaml
- task: AzureRMWebAppDeployment@4
  inputs:
    appType: webApp
    WebAppName: $(appName)
    AppSettings: '-AzureAd:ClientSecret $(clientSecret) -ConnectionStrings:DefaultConnection $(dbConn)'
```

---

## 6. Service Principals for Pipelines

For at Azure Pipelines skal kunne administrere og rulle ut ressurser til Azure, benyttes **Service Principals** (App Registrations) i Azure Entra ID. Disse tilgjengeliggjøres i Azure DevOps gjennom **Service Connections**.

### 6.1 Autentisering og Sikkerhet
Vi benytter i hovedsak to metoder for autentisering av pipelines:

1.  **Workload Identity Federation (OIDC)**: 
    - Dette er den anbefalte metoden som brukes for nyere tilkoblinger (f.eks. `sp-bufdir-app-qa`, `sp-bufdir-app-prod`).
    - Det kreves ingen lagrede hemmeligheter (secrets) i Azure DevOps, da Azure stoler på tokens utstedt av Azure DevOps. Dette fjerner behovet for rotering av passord.
2.  **Service Principal med Secret**:
    - Eldre tilkoblinger (f.eks. `bufdirno-fantomet`) kan bruke en tradisjonell `Client Secret`.
    - Disse krever manuell rotering før utløpsdato (typisk 1-2 år).

### 6.2 Oversikt over Service Connections
| Navn i Pipeline | Type Autentisering | Formål |
| :--- | :--- | :--- |
| `bufdirno-fantomet` | Secret / Federated | Tilgang til dev/test subskripsjon for Fantomet-miljøer. |
| `sp-bufdir-app-qa` | Workload Identity (OIDC) | Deployment til QA-miljøet. |
| `sp-bufdir-app-prod` | Workload Identity (OIDC) | Deployment til produksjonsmiljøet. |
| `acrServiceConnection` | Service Principal | Tilgang til Azure Container Registry for push/pull av Docker-images. |

---

## 7. Oversikt over Utløpsdatoer og Rotering
| Secret / Sertifikat | Forventet Gyldighet | Type Rotering |
| :--- | :--- | :--- |
| **Azure AD App Secrets** | 12-24 mnd | Manuell fornyelse i Azure Entra ID |
| **ID-porten Secrets** | Varierer (typisk 1-2 år) | Manuell fornyelse i DigDir Samarbeidsportalen |
| **Virksomhetssertifikat** | 2-3 år | Bestilling fra utsteder (Buypass/Commfides) |
| **SSL/TLS Sertifikater** | 1 år | Ofte auto-fornyelse via Azure (Managed Certificates) |
| **Service Principal Secrets** | 1-2 år | Manuell fornyelse i Azure Entra ID og oppdatering i Azure DevOps |
| **Maskinporten JWK** | Varierer | Genereres på nytt ved behov |
| **API-nøkler (Make, Ros)** | Varierer | Manuelt generert i respektive portaler |

---

## 8. Modulspesifikk Konfigurasjonsflyt

Dette kapittelet beskriver nøyaktig hvordan konfigurasjon, secrets og sertifikater henger sammen med pipelines for hver enkelt modul.

### 8.1 bufdirno (Webportal)
Hovedportalen består av en Next.js frontend og en Optimizely CMS backend (.NET), begge deployet til Azure Container Apps.

| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `EPiServerDB` | Tilkoblingsstreng for Optimizely database | KeyVault (`kv-bufdirno-prod`) |
| `AzureStorageConnectionString` | Azure Blob Storage tilkobling for media | KeyVault (`kv-bufdirno-prod`) |
| `VSS_NUGET_ACCESSTOKEN` | Tilgang til interne NuGet-pakker i build | Variable Group |
| `AZURE_CLIENT_SECRET` | Secret for Azure AD autentisering | KeyVault (`kv-bufdirno-prod`) |
| `IDPORTEN_CLIENT_SECRET` | Secret for ID-porten (OIDC) | KeyVault (`kv-bufdirno-prod`) |

- **Konfigurasjon**:
  - Backend: `appsettings.json` i `src/Site`.
  - Frontend: `next.config.js` og miljøvariabler.
- **Secrets**:
  - Begge moduler henter secrets fra Azure KeyVault ved runtime via Managed Identity.
- **Pipeline**: `bufdirno/frontend.yml` og `bufdirno/backend.yml`.
  - Bruker Docker-baserte bygginger og deployer til Container Apps via `az containerapp update`.

### 8.2 bufdirno-fsa (Family Services Application)
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `VITE_APPINSIGHTS_CONNECTION_STRING` | AppInsights tilkobling for frontend | Variable Group |
| `SQL_PASSWORD` | Passord for SQL-migrering (DACPAC) | KeyVault (`kv-dsm-prod`) |
| `MASKINPORTEN_CLIENT_ID` | Klient-ID for Maskinporten | `appsettings.Production.json` |
| `MASKINPORTEN_JWK_ENCODED` | Base64 JWK for Maskinporten-token | KeyVault (`kv-dsm-prod`) |
| `EncodedX509NameInKeyVault` | Navn på virksomhetssertifikat i KeyVault | KeyVault (`kv-dsm-prod`) |

- **Konfigurasjon**:
  - Backend: `appsettings.json` og `appsettings.Production.json` i `FSA.Backend.Web`.
  - Frontend: Miljøvariabler injisert via Vite under bygging.
- **Secrets**:
  - Hentes fra Azure KeyVault (`dsm-fsa-keyvault-dev`, `kv-dsm-qa`, `kv-dsm-prod`) ved runtime via Managed Identity.
  - SQL-passord for migrasjon hentes fra KeyVault i pipelinen via `AzureKeyVault@2` tasken.
- **Pipeline**: `bufdirno-fsa/azure-pipeline.yml`
  - Bruker `VITE_APPINSIGHTS_CONNECTION_STRING` som settes i pipeline-variabler.
  - Deploy-template `templates/deploy.yml` mapper SQL-credentials for DACPAC-deploy.

### 8.3 bufdirno-fsa-content (FSA Strapi)
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `APP_KEYS` | Strapi app-nøkler for session | KeyVault (`kv-dsm-prod`) |
| `API_TOKEN_SALT` | Salt for API-tokens | KeyVault (`kv-dsm-prod`) |
| `DATABASE_URL` | Postgres database-URL | KeyVault (`kv-dsm-prod`) |
| `ADMIN_JWT_SECRET` | Secret for Admin-panelets JWT | KeyVault (`kv-dsm-prod`) |

- **Konfigurasjon**: `.env`-filer spesifikke for miljøet (f.eks. `.env-prod`).
- **Secrets**: 
  - Ved oppstart kjøres en mekanisme som henter hemmeligheter fra Azure KeyVault via Managed Identity.
- **Pipeline**: `bufdirno-fsa-content/azure-pipeline.yml`
  - Docker-basert bygging og deployment til Azure Container App.

### 8.4 bufdirno-familievern-api
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `dbCon` | SQL Server tilkoblingsstreng | KeyVault (`kv-familievernapi-prod`) |
| `AzureAd:ClientSecret` | Azure AD App Secret | KeyVault (`kv-familievernapi-prod`) |

- **Konfigurasjon**: `appsettings.json` i `Familievern.Api`.
- **Secrets**: Hentes fra `kv-familievernapi` ved runtime.
- **Pipeline**: `bufdirno-familievern-api/azure-pipelines.yml`
  - Bruker `templates/deploy-appservice.yml` for deployment til Azure App Service.
  - Ingen direkte injisering av app-secrets i pipelinen; applikasjonen stoler på KeyVault-tilgang via Managed Identity.

### 8.5 bufdirno-fosterhjem-api
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `dbCon` | SQL Server tilkoblingsstreng | KeyVault (`kv-bufdirno-prod`) |
| `RosApiKey` | API-nøkkel for Ros-integrasjon | KeyVault (`kv-bufdirno-prod`) |
| `Oslo:ApiKey` | API-nøkkel for Oslo-integrasjon | KeyVault (`kv-bufdirno-prod`) |

- **Konfigurasjon**: `appsettings.json` med `AzureKeyVaultEnabled: true`.
- **Secrets**:
  - `RosApiKey` og `Oslo:ApiKey` lagres i KeyVault.
  - Connection strings hentes fra KeyVault.
- **Pipeline**: Standard .NET deployment til Azure Container Apps.

### 8.6 bufdirno-feedback-api (Azure Functions)
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `SqlConnectionString` | SQL Server tilkoblingsstreng | App Settings / KeyVault |
| `DEVSQLPASS` / `PRODSQLPASS` | Passord for SQL-migrering | Variable Group |

- **Konfigurasjon**: App Settings i Azure Portal.
- **Secrets**: `SqlConnectionString` lagres som Secret i App Settings eller i KeyVault.
- **Pipeline**: `bufdirno-feedback-api/azure-pipelines.yml`
  - SQL-passord for migrasjon (`DEVSQLPASS`, `QASQLPASS`, `PRODSQLPASS`) hentes fra Variable Groups i Azure DevOps.

### 8.7 stat-content-strapi5 (Strapi CMS)
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `DATABASE_URL` | Postgres database-URL | KeyVault (`kv-dsm-prod`) |
| `JWT_SECRET` | Secret for JWT-signering | KeyVault (`kv-dsm-prod`) |
| `ADMIN_JWT_SECRET` | Secret for Admin-panelets JWT | KeyVault (`kv-dsm-prod`) |
| `IMAGE_STORAGE_ACCOUNT_NAME` | Navn på Azure Storage for bilder | Variable Group |

- **Konfigurasjon**: `.env`-filer spesifikke for miljøet (`Dockerfile-prod` peker på `.env-prod`).
- **Secrets**: 
  - Ved oppstart kjøres `applySecretsToContentTypes.js` som henter hemmeligheter fra Azure KeyVault.
- **Pipeline**: `stat-content-strapi5/azure-pipeline.yml`
  - Bruker Variable Groups (`stat-content5-test`, `stat-content5-qa`, `stat-content5-prod`) for å styre ressursnavn og miljø.
  - Oppdaterer Container App via Azure CLI (`az containerapp update`).

### 8.8 utrapporteringsbank (Next.js)
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `DB_PASSWORD` | Passord for databasen | KeyVault (`kv-dsm-prod`) |
| `MASKINPORTEN_JWK_ENCODED` | JWK for Maskinporten | KeyVault (`kv-dsm-prod`) |
| `AZURE_CLIENT_SECRET` | Secret for Azure AD autentisering | KeyVault (`kv-bufdirno-prod`) |
| `IDPORTEN_CLIENT_SECRET` | Secret for ID-porten (OIDC) | KeyVault (`kv-bufdirno-prod`) |
| `NEXT_PUBLIC_APP_INSIGHTS_KEY` | Instrumentation key for frontend | Variable Group |

- **Konfigurasjon**: `next.config.ts` og miljøvariabler.
- **Secrets**: 
  - `DB_PASSWORD`, `IDPORTEN_CLIENT_SECRET`, `AZURE_CLIENT_SECRET` hentes fra KeyVault.
- **Pipeline**: `utrapporteringsbank/azure-pipelines.yml`
  - Docker-basert bygging.
  - Deployer til Azure Container App via `az containerapp revision copy`.

### 8.9 bufdirno-newsletter-api
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `dbCon` | SQL Server tilkoblingsstreng | KeyVault (`kv-bufdirno-prod`) |
| `Services:Make:UserId` | Bruker-ID for Make.Newsletters | KeyVault (`kv-bufdirno-prod`) |
| `VSS_NUGET_ACCESSTOKEN` | Tilgang til interne NuGet-pakker | Variable Group |

- **Konfigurasjon**: App Settings i Azure Container App.
- **Pipeline**: `bufdirno-newsletter-api/azure-pipelines.yml`
  - Bruker `NuGetAuthenticate@1` med `VSS_NUGET_ACCESSTOKEN` for å hente interne pakker under Docker-bygging.
  - Oppdaterer Container App med ny build-id tag.

### 8.10 stat-backend (.NET API)
| Setting / Secret / Sertifikat | Beskrivelse | Lokasjon |
| :--- | :--- | :--- |
| `CosmosDb:ConnectionString` | Tilkobling til CosmosDB | KeyVault (`kv-bufdirno-prod`) |
| `Azure:KeyVaultName` | Navn på KeyVault appen skal lese fra | `appsettings.json` |

- **Konfigurasjon**: `appsettings.json` med `Azure:KeyVaultName`.
- **Secrets**: Hentes fra KeyVault ved runtime.
- **Pipeline**: `stat-backend/azure-pipelines.yml`
  - Deployer til Azure App Service via `templates/deploy-appservice.yml`.

## 9. Oversikt over Kritiske Secrets og Sertifikater

### 9.1 Sentrale KeyVaults og innhold
Alle secrets er lagret i dedikerte Azure KeyVaults. Tilgang styres via Managed Identity for applikasjonene.

| Miljø | KeyVault Navn | Hovedinnhold |
| :--- | :--- | :--- |
| **Produksjon (Felles)** | `kv-bufdirno-prod` | `EPiServerDB`, `AzureStorageConnectionString`, `RosApiKey`, `Oslo:ApiKey`, `dbCon` (Newsletter), `dbCon` (Stat), `CosmosDb:ConnectionString`, `IDPORTEN_CLIENT_SECRET`, `AZURE_CLIENT_SECRET` |
| **Produksjon (FSA)** | `kv-dsm-prod` | `SQL_PASSWORD`, `MASKINPORTEN_JWK_ENCODED`, `Virksomhetssertifikat`, `APP_KEYS`, `API_TOKEN_SALT`, `DATABASE_URL`, `ADMIN_JWT_SECRET` |
| **Produksjon (Familievern)** | `kv-familievernapi-prod` | `dbCon`, `AzureAd:ClientSecret` |
| **QA / Test** | `kv-bufdirno-qa`, `kv-dsm-qa` | Tilsvarende secrets for test- og QA-miljøer. |

### 8.2 Sertifikater (SSL og Virksomhet)
Sertifikater er lagret enten som "Certificates" eller "Secrets" (for JWK/Base64) i Azure KeyVault, eller administrert direkte i Azure App Service/Container Apps.

| Sertifikat | Lokasjon / Ressurs | Format |
| :--- | :--- | :--- |
| **SSL for bufdir.no** | Azure App Service / Container Apps / Front Door | SSL/TLS (Pfx / Managed) |
| **Virksomhetssertifikat** | Azure KeyVault (`kv-dsm-prod`, `kv-bufdirno-prod`) | `.pfx` eller Secret med Base64 |
| **Maskinporten JWK** | Azure KeyVault (`kv-dsm-prod`) | JSON Web Key (Stored as Secret) |
| **ID-porten Klient-sert** | Azure KeyVault (`kv-bufdirno-prod`) | `.pfx` eller Secret |
