# Bufdir.no Webportal - bufdirno

**Stack**: Optimizely CMS + Next.js
**Repository**: `bufdirno/`
**Solution File**: `BufdirWeb.sln`

Hovednettsiden for Bufdir.no, bygget på Optimizely CMS for innholdsadministrasjon med en Next.js frontend for moderne webopplevelser.

**Funksjonalitet**: Fungerer som primærportalen for Bufdir (Barne-, ungdoms- og familiedirektoratet), og tilbyr omfattende informasjon om barnevern, familietjenester, adopsjon, fosterhjem og sosialtjenester i Norge. Nettstedet gjør det mulig for innholdsredaktører å administrere rikt medieinnhold gjennom Optimizely CMS, samtidig som det leverer raske, SEO-optimaliserte sider til innbyggere via Next.js. Viktige funksjoner inkluderer dynamiske innholdsblokker, integrasjon med ulike mikrotjenester for tilbakemeldingsinnsamling, nyhetsbrevabonnement, statistikkvisualisering og kontor-/tjenestesøk. Plattformen støtter flerspråklig innholdsleveranse og integreres med Azure AD for sikker administrativ tilgang.

```mermaid
graph LR
    subgraph "bufdirno Architecture"
        Frontend[Next.js Frontend<br/>React + TypeScript]
        Backend[Optimizely CMS<br/>.NET Backend]
        FeedbackUI[Feedback Dashboard<br/>Admin UI]
    end

    subgraph "Dependencies"
        DB[(Azure SQL Server<br/>Relational DB<br/>Content + Data)]
        Storage[Azure Blob Storage<br/>Unstructured Files<br/>Media Files]
    end

    subgraph "External APIs"
        FeedbackAPI[Tilbakemeldinger API<br/>Azure Functions]
        FamilievernAPI[Familievern API<br/>Kontorsøk]
        FosterAPI[Fosterhjem API<br/>Fosterhjem]
        NewsletterAPI[Nyhetsbrev API<br/>Abonnementer]
        StatAPI[Statistikk API<br/>Data]
    end

    subgraph "Security"
        AD[Azure AD<br/>Authentication]
        KV[KeyVault<br/>Secrets]
    end

    Frontend --> Backend
    Backend --> DB
    Backend --> Storage
    Backend --> FeedbackAPI
    Backend --> FamilievernAPI
    Backend --> FosterAPI
    Backend --> NewsletterAPI
    Backend --> StatAPI
    FeedbackUI --> FeedbackAPI

    AD -.-> Backend
    KV -.-> Backend

    classDef frontend fill:#10B981,stroke:#059669,stroke-width:2px,color:#fff
    classDef backend fill:#3B82F6,stroke:#2563EB,stroke-width:2px,color:#fff
    classDef database fill:#06B6D4,stroke:#0891B2,stroke-width:2px,color:#000
    classDef api fill:#F59E0B,stroke:#D97706,stroke-width:2px,color:#000
    classDef security fill:#EAB308,stroke:#CA8A04,stroke-width:2px,color:#000

    class Frontend,FeedbackUI frontend
    class Backend backend
    class DB,Storage database
    class FeedbackAPI,FamilievernAPI,FosterAPI,NewsletterAPI,StatAPI api
    class AD,KV security
```

**Nøkkelkomponenter**:
- **Backend**: .NET-applikasjon med Optimizely CMS
- **Frontend**: Next.js React-applikasjon (`src/NextJs/`)
- **Database**: Azure SQL Server (relasjonsdatabase for CMS-innhold, sidedata og applikasjonsdata)
- **Blob Storage**: Azure Blob Storage (mediafiler, bilder, dokumenter)
- **Infrastructure**: Azure (KeyVault, Container Apps)
- **Authentication**: Azure AD (OAuth2 for CMS-administratortilgang og API-autentisering)

**Runtime Environment**: Azure Container App (.NET + Node.js)
- **Deployment**: Azure Pipelines (backend.yml, frontend.yml)
- **Environments**:
  - **Development/Test**: Container App `bufdirnext` (rg-ny.bufdir.no)
  - **Sandbox**: Container App `bufdirnext-sandbox` (rg-ny.bufdir.no)
  - **QA**: Container App `bufdirnext-qa` (rg-ny.bufdir.no)
  - **Production**: Container App `bufdirnext-prod` (rg-bufdirweb-prod)
- **CI/CD**: Automatisert utrulling ved branch-sammenslåing
- **Container Registry**: `crbufdirnodevtest.azurecr.io`
- **Resource Group**: rg-ny.bufdir.no (test/qa), rg-bufdirweb-prod (production)

**Development**:
- Backend: Visual Studio eller `dotnet run`
- Frontend: `npm run dev` (kjører på https://localhost:3000)
- CMS Admin: https://localhost:44320/EPiServer/Cms

**Konfigurasjon / Miljøvariabler**:

| Variabel | Beskrivelse | Kilde |
|----------|-------------|-------|
| `ConnectionStrings:EPiServerDB` | Azure SQL Server tilkoblingsstreng for CMS | KeyVault |
| `ConnectionStrings:EpiserverBlobs` | Azure Blob Storage tilkoblingsstreng | KeyVault |
| `AzureAd:TenantId` | Azure AD tenant ID | Config |
| `AzureAd:ClientId` | Azure AD applikasjons-ID | Config |
| `InternalResources:ClientSecret` | Hemmelighet for API-integrasjoner | KeyVault |
| `InternalResources:CaptchaSecretKey` | Google reCAPTCHA nøkkel | KeyVault |
| `ApplicationInsights:ConnectionString` | Application Insights for logging | KeyVault |
| `ElasticSearch:CloudId` | Elasticsearch cloud ID for søk | KeyVault |
| `ElasticSearch:ApiKey` | Elasticsearch API-nøkkel | KeyVault |
| `Statistics:ApiUrl` | URL til statistikk-API | Config |
| `FeedbackApi:Mail:SendGridKey` | SendGrid API-nøkkel for e-post | KeyVault |
| `AzureStorageQueue:ConnectionString` | Queue storage for Optimizely-hendelser | KeyVault |
| `Serilog:WriteTo:SeqSink:Args:apiKey` | Seq logging API-nøkkel | KeyVault |

**API Integrasjoner** (InternalResources:Resources):

| API | Beskrivelse | Autentisering |
|-----|-------------|---------------|
| `FamilievernKontor` | Familierådgivningskontorer API | OAuth2 scope |
| `Feedback` | Tilbakemeldinger API | Function key |
| `FostercareZip/Form/Events` | Fosterhjem API | OAuth2 scope |
| `Newsletter` | Nyhetsbrev API | Internal network |
