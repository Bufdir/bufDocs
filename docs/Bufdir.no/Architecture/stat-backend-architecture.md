# Statistikk & Data API - stat-backend

**Stack**: .NET 6.0
**Repository**: `stat-backend/`
**Solution File**: `BufdirStatistics.sln`

Modulær statistikk-API som leverer data til diverse Bufdir-tjenester.

**Funksjonalitet**: Leverer statistiske data og analyser gjennom en modulær API-arkitektur som støtter flere spesialiserte tjenester. Systemet består av to hovedmoduler: MunStat (Kommunemonitor) som gir statistikk på kommunenivå og dashboards for lokalmyndigheters overvåking av barnevernsstatistikk, og Statistics-modulen som leverer generell statistisk data for innholdsblokker på Bufdir.no. API-et aggregerer data fra Cosmos DB (MongoDB API) som inneholder tidsseriestatistikk, saksnumre, demografiske opplysninger og trendanalyser. Integrasjon med stat-content-strapi5 gir konfigurerbare datavisualiseringer, diagramdefinisjoner og visningsparametere. Den modulære arkitekturen tillater uavhengig utrulling og skalering av statistikktjenester, med hver modul hostet på separate Azure App Services. Systemet støtter komplekse spørringer, dataaggregering og caching for høy-ytende levering av statistisk innsikt til dashboards og offentlige informasjonssider.

**Konfigurasjon / Miljøvariabler**:

**Azure AD Konfigurasjon**:

| Variabel | Beskrivelse | Kilde |
|----------|-------------|-------|
| `AzureAd:Instance` | Azure AD instance URL | Config |
| `AzureAd:ClientId` | Azure AD applikasjons-ID | Config |
| `AzureAd:TenantId` | Azure AD tenant ID | Config |
| `AzureAd:Domain` | Azure AD domene | Config |

**Generell Konfigurasjon**:

| Variabel | Beskrivelse | Eksempel |
|----------|-------------|----------|
| `ASPNETCORE_ENVIRONMENT` | Miljøtype | LocalDevelopment, Development, Production |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights tilkoblingsstreng | KeyVault |

**MongoDB / Cosmos DB Konfigurasjon** (`MongoDb` section):

| Variabel | Beskrivelse | Kilde |
|----------|-------------|-------|
| `MongoDb:ConnectionString` | Direkte tilkoblingsstreng (prioriteres hvis satt) | KeyVault |
| `MongoDb:Secret` | Navn på KeyVault-hemmelighet for connection string | Config |
| `MongoDb:Host` | MongoDB/Cosmos DB host | Config |
| `MongoDb:Port` | MongoDB/Cosmos DB port | Config |
| `MongoDb:Username` | Database brukernavn | Config |
| `MongoDb:Password` | Database passord | KeyVault |

**Azure Konfigurasjon** (`Azure` section):

| Variabel | Beskrivelse | Kilde |
|----------|-------------|-------|
| `Azure:KeyVaultName` | Azure KeyVault navn for secrets | Config |
| `Azure:TenantId` | Azure tenant ID for KeyVault tilgang | Config |

```mermaid
graph TB
    subgraph "stat-backend Architecture"
        MainAPI[BufdirStatisticsDataAPI<br/>Main Module Loader]
        MunStat[MunStat Module<br/>Kommunemonitor API]
        Statistics[Statistics Module<br/>General Stats API]
        Core[Core<br/>Shared Functionality]
        Tools[Tools<br/>Utilities]
    end

    subgraph "Data & Content"
        CosmosDB[(Cosmos DB<br/>NoSQL Document DB<br/>MongoDB API<br/>Statistikkdata)]
        StrapiContent[stat-content-strapi5<br/>Strapi CMS<br/>Content API<br/>Konfigurasjon]
    end

    subgraph "Consumers"
        Bufdirno[bufdirno<br/>Statistikkblokker]
        Kommunemonitor[Kommunemonitor<br/>Dashboard]
    end

    subgraph "Security"
        KV[Azure KeyVault<br/>Connection Strings]
    end

    MainAPI --> MunStat
    MainAPI --> Statistics
    MainAPI --> Core
    MunStat --> Core
    Statistics --> Core
    Statistics --> CosmosDB
    MunStat --> CosmosDB
    Statistics --> StrapiContent
    Bufdirno --> Statistics
    Kommunemonitor --> MunStat
    KV -.-> MainAPI

    classDef api fill:#F59E0B,stroke:#D97706,stroke-width:2px,color:#000
    classDef module fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff
    classDef database fill:#06B6D4,stroke:#0891B2,stroke-width:2px,color:#000
    classDef cms fill:#8B5CF6,stroke:#7C3AED,stroke-width:2px,color:#fff
    classDef backend fill:#3B82F6,stroke:#2563EB,stroke-width:2px,color:#fff
    classDef security fill:#EAB308,stroke:#CA8A04,stroke-width:2px,color:#000

    class MainAPI api
    class MunStat,Statistics,Core,Tools module
    class CosmosDB database
    class StrapiContent cms
    class Bufdirno,Kommunemonitor backend
    class KV security
```

**Modules**:
- `MunStat` - Municipal monitor API (Kommunemonitor)
- `Statistics` - General statistics API for Strapi blocks
- `Core` - Shared functionality
- `BufdirStatisticsDataAPI` - Main runnable module
- `Tools` - Utility tools

**Database**: Azure Cosmos DB with MongoDB API (NoSQL document database)
- Stores statistical data, time-series data, and aggregated metrics
- MongoDB-compatible API for flexible schema and high-performance queries
- Optimized for read-heavy workloads (statistics dashboards and reports)
- Scalable for large datasets

**Authentication**: Azure KeyVault + IP Whitelisting
- Cosmos DB connection string stored in Azure KeyVault
- Managed Identity for App Service KeyVault access
- Client certificates for inter-service communication

**Runtime Environment**: Azure App Service (.NET)
- **Deployment**: WebDeploy from CI/CD pipeline
- **Environments**: Dev, QA, Production
- **Hosting**: Azure App Service
- **CI/CD**: Azure Pipelines (build and release)

**Development**:
- Local SQL Server or MongoDB for dev
- Visual Studio for .NET 6.0 development
- API access via Swagger for local testing
