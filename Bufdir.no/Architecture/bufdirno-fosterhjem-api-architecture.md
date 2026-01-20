# Fosterhjem API - bufdirno-fosterhjem-api

**Stack**: .NET API
**Repository**: `bufdirno-fosterhjem-api/`
**Solution File**: `BufDirNoApi.sln`

API for fosterhjemstjenester.

**Funksjonalitet**: Administrerer informasjon og arrangementer knyttet til fosterhjemstjenester (fosterhjem) i Norge, og støtter både offentlig informasjonsspredning og skjemainnsending. API-et tilbyr endepunkter for søk etter fosterhjemskontorer etter postnummer, henting av informasjon om fosterhjemsprogrammer og krav, administrering av arrangementsoversikter for opplæring av fosterforeldre og informasjonsmøter, og behandling av innkommende skjemaer fra potensielle fosterforeldre. Tjenesten følger Clean Architecture-prinsipper med separate lag for API-kontrollere, kjerneforretningslogikk og datatilgang via Entity Framework Core. Integrasjon med Azure AD OAuth2 sikrer sikker tilgang når den kalles fra bufdirno-portalen, mens Azure KeyVault administrerer sensitiv konfigurasjonsdata. API-et støtter hele informasjonsflyten for fosterhjem fra første henvendelse til formell søknadsinnsending.

**Konfigurasjon / Miljøvariabler**:
- `AzureKeyVaultEnabled` - Aktiverer Azure KeyVault (true/false)
- `AzureKeyVaultName` - KeyVault navn (kv-bufdirno-test, kv-bufdirno-prod, etc.)
- `ConnectionStrings:dbCon` - SQL Server tilkoblingsstreng for fosterhjem-data
- `UseInMemoryDatabase` - Bruker in-memory database for testing (true/false)
- `Require_Authentication` - Krever Azure AD autentisering (true/false)
- `SwaggerEnabled` - Aktiverer Swagger API-dokumentasjon (true/false)
- `AzureAd:Instance` - Azure AD instance URL
- `AzureAd:ClientId` - Azure AD applikasjons-ID
- `AzureAd:TenantId` - Azure AD tenant ID
- `AzureAd:TokenValidationParameters:ValidAudiences` - Gyldige API audience-verdier
- `AuthorizationUrl` - Azure AD OAuth2 authorization URL
- `TokenUrl` - Azure AD OAuth2 token URL
- `ApiScope` - OAuth2 API scope for autentisering
- **Eksterne API-integrasjoner**:
  - `RosApiBaseUrl` - ROS (Bufetat) API base URL (regioner 2-6)
  - `RosApiKey` - API-nøkkel for ROS-integrasjon
  - `Oslo:BaseAddress` - Oslo Kommune API base URL (region 8)
  - `Oslo:ApiKey` - API-nøkkel for Oslo-integrasjon
- **Klient Konfigurasjon** (`ClientConfigurations` array):
  - `AppId` - Azure AD App ID for klientsystem
  - `Name` - Klientnavn (Ros, Oslo)
  - `SystemId` - Unikt system-ID (1=ROS, 2=Oslo)
  - `EnableNewFormHandling` - Aktiverer ny skjemabehandling
  - `RegionIds` - Liste over regionIDer systemet håndterer

```mermaid
graph TB
    subgraph "bufdirno-fosterhjem-api"
        API[Api<br/>Web API<br/>Controllers]
        Core[Core<br/>Business Logic<br/>Domain Models]
        Infra[Infrastructure<br/>Data Access<br/>EF Core]
    end

    subgraph "Endpoints"
        ZipCode[GET /ZipCode/list<br/>Office Lookup]
        Form[POST /InboundForm<br/>Form Submission]
        Events[GET /Event/list<br/>Event Listings]
    end

    subgraph "Data & Security"
        DB[(SQL Server/PostgreSQL<br/>Relational DB<br/>Fosterhjemdata)]
        KV[Azure KeyVault<br/>Secrets]
        AD[Azure AD<br/>OAuth2<br/>Managed Identity]
    end

    subgraph "External Services"
        ROS[ROS<br/>Bufetat<br/>Fosterhjemsystem<br/>Regioner 2-6]
        OsloAPI[Oslo Kommune API<br/>Fosterhjemsystem<br/>Region 7]
    end

    subgraph "Consumers"
        Bufdirno[bufdirno<br/>Optimizely CMS]
    end

    API --> ZipCode
    API --> Form
    API --> Events
    API --> Core
    Core --> Infra
    Infra --> DB
    Core --> ROS
    Core --> OsloAPI
    Bufdirno --> API
    KV -.-> API
    AD -.-> API

    classDef api fill:#F59E0B,stroke:#D97706,stroke-width:2px,color:#000
    classDef layer fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff
    classDef endpoint fill:#5DADE2,stroke:#3498DB,stroke-width:2px,color:#000
    classDef database fill:#06B6D4,stroke:#0891B2,stroke-width:2px,color:#000
    classDef security fill:#EAB308,stroke:#CA8A04,stroke-width:2px,color:#000
    classDef backend fill:#3B82F6,stroke:#2563EB,stroke-width:2px,color:#fff
    classDef external fill:#EF4444,stroke:#DC2626,stroke-width:2px,color:#fff

    class API api
    class Core,Infra layer
    class ZipCode,Form,Events endpoint
    class ROS,OsloAPI external
    class DB database
    class KV,AD security
    class Bufdirno backend
```

**Projects**:
- `Api` - Web API project
- `Core` - Core business logic
- `Infrastructure` - Data access and infrastructure
- `Tests` - Test projects

**Database**: SQL Server or PostgreSQL (relational database)
- Stores foster home data, events, office information, and form submissions
- Managed via Entity Framework Core
- Clean Architecture pattern with Infrastructure layer for data access

**External Services Integration**:
- **ROS (Rekruttering og Oppfølging av Statlige fosterhjem)**: Bufetat's foster home system at https://ros.bufetat.no
  - Handles regions 2-6 (state-managed foster homes)
  - Provides area/region lookups via `/api/Area/list`
  - Form submission endpoint (currently disabled - returns HTTP 410)
- **Oslo Kommune API**: Oslo municipality's foster home system at https://fosterhjem.api.oslo.kommune.no
  - Handles region 7 (Oslo municipality)
  - Provides course and event management
  - Handles form submissions for Oslo municipality

**Authentication**: Azure AD OAuth2
- Required for all API endpoints (`Require_Authentication=true`)
- JWT token validation with `TokenValidationParameters`
- Managed Identity for Azure resource access

**Runtime Environment**: Azure Container App (.NET)
- **Deployment**: Azure Pipelines (azure-pipelines-prod.yml, azure-pipelines-dev.yml)
- **Environments**: Dev, QA, Production
- **Hosting**: Azure Container Apps
- **Container Registry**: Azure Container Registry (crbufdirnodevtest.azurecr.io)
- **Docker**: Containerized application using multi-stage build

**Development**:
```bash
dotnet run --project Api/Api.csproj
```
