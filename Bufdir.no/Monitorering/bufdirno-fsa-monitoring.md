# Monitoreringsoppgaver for bufdirno-fsa (Family Services Application)

## Gevinst med monitorering (Brukerhistorie)
**Som** ansvarlig for Family Services Application (FSA),
**ønsker jeg** 100% sporbarhet i søknadsprosessen og pålitelige integrasjoner mot Digipost og DSF,
**slik at** vi kan garantere at kritiske tjenester alltid fungerer og raskt identifisere hvorfor en søknad ev. stopper opp.

### Akseptansekriterier
 - Hver søknadsinnsending kan følges steg-for-steg gjennom systemet via sporing (traces).
 - Integrasjonsfeil (Digipost/DSF) fanges opp og varsles umiddelbart.
 - Det er mulig å se suksessrate for fullføring av søknadsskjemaer i et dashboard.
 - Forretningslogikkfeil logges som egne hendelser for enkel feilsøking.

Dette dokumentet beskriver oppgavene som kreves for å sette opp monitorering spesifikt for **bufdirno-fsa**, som består av en React SPA frontend og en .NET backend (**FSA.Backend.Web**), samt en Strapi CMS for innhold.

### Hybrid Monitoreringsstrategi
For dette prosjektet har vi valgt en **hybrid monitoreringsmodell** som kombinerer det beste fra to verdener:
1.  **Frontend (React): Azure Application Insights SDK**
    *   **Hvorfor:** Spesialtilpasset for Real User Monitoring (RUM). Håndterer klientside-spesifikke behov som brukersesjoner, sidevisninger og JavaScript-exceptions mer sømløst enn standard OpenTelemetry i nettleseren.
2.  **Backend (.NET & Node.js): OpenTelemetry**
    *   **Hvorfor:** Industristandard for moderne backend-instrumentering. Gir bedre ytelse, er leverandørnøytral og er Microsofts primære anbefaling for .NET 8/9 og moderne Node.js-arkitekturer.
3.  **Korrelasjon:** Begge systemer bruker **W3C Trace Context** som standard, noe som sikrer at distribuert sporing (traces) fungerer sømløst fra brukerens klikk i nettleseren, gjennom API-ene og ned til databasen.

## Innholdsfortegnelse

- [Fase 1: Grunnleggende oppsett](#fase-1-grunnleggende-oppsett)
- [Fase 2: Applikasjonsinstrumentering](#fase-2-applikasjonsinstrumentering)
- [Fase 3: Infrastrukturmonitorering](#fase-3-infrastrukturmonitorering)
- [Fase 4: Varslingskonfigurasjon](#fase-4-varslingskonfigurasjon)
- [Fase 5: Dashboards og visualisering](#fase-5-dashboards-og-visualisering)
- [Fase 6: Dokumentasjon og runbooks](#fase-6-dokumentasjon-og-runbooks)
- [Fase 7: Overvåking av sertifikater og secrets](#fase-7-overvåking-av-sertifikater-og-secrets)
- [Fase 8: Spesifikke metrikker og spor (Metrics & Traces)](#fase-8-spesifikke-metrikker-og-spor-metrics--traces)

---

## Fase 1: Grunnleggende oppsett

### Oppgave 1.1: Bruk felles Application Insights-ressurs
 - Koble `bufdirno-fsa` til den felles Application Insights-ressursen for å muliggjøre korrelasjon med hovedportalen og mikrotjenester.
 - Gjenbruk felles Log Analytics workspace.
 - Konfigurer miljøspesifikke tagger: `project: fsa`, `service: fsa-backend` / `fsa-frontend`.

---

## Fase 2: Applikasjonsinstrumentering

### Oppgave 2.1: Instrumenter .NET Backend (FSA.Backend.Web)
 - Installer **OpenTelemetry** SDK i `FSA.Backend.Web`-modulen.
 - Konfigurer OpenTelemetry i `ConfigureCoreServices.cs` for å fange opp SQL Server-kall og HTTP-trafikk ved bruk av Azure Monitor exporter.
 - Legg til connection string fra Key Vault.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
Legg til følgende pakker i `FSA.Backend.Web`:
`Azure.Monitor.OpenTelemetry.AspNetCore`.

**Eksempel på konfigurasjon i `ConfigureCoreServices.cs`:**
```csharp
using Azure.Monitor.OpenTelemetry.AspNetCore;
using OpenTelemetry.Resources;

// I AddCoreServices:
services.AddOpenTelemetry()
    .ConfigureResource(resource => resource.AddService("Bufdir.FSA.Backend"))
    .UseAzureMonitor(options =>
    {
        options.ConnectionString = configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];
    });
```

### Oppgave 2.2: Instrumenter React Frontend (Application Insights SDK)
 - Installer Application Insights SDK:
  ```bash
  npm install @microsoft/applicationinsights-web
  ```
 - Opprett en initialiseringsfil for Application Insights i React-appen.

#### Implementasjonsveiledning for React med Application Insights

```typescript
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

const appInsights = new ApplicationInsights({
  config: {
    connectionString: "DIN_CONNECTION_STRING_HER",
    enableAutoRouteTracking: true,
    distributedTracingMode: 2, // W3C standard
  }
});
appInsights.loadAppInsights();
appInsights.trackPageView();
```

**Viktige fordeler:**
1. **Enkelt oppsett:** Ingen behov for OTLP Collector proxy.
2. **Real User Monitoring (RUM):** Man ser nøyaktig hva brukeren opplever direkte i Azure.
3. **Distributed Tracing:** Korrelerer forespørsler fra frontend til backend via W3C standard.

### Oppgave 2.3: Instrumenter Strapi CMS (OpenTelemetry)
 - Konfigurer **OpenTelemetry** Node.js SDK for Strapi med Azure Monitor exporter.
 - Sett `service.name` til `Bufdir.FSA.Strapi`.

#### Implementasjonsveiledning for Strapi med OpenTelemetry

**1. Installer pakker:**
```bash
npm install @azure/monitor-opentelemetry @opentelemetry/api
```

**2. Opprett `otel.js`:**
```javascript
const { useAzureMonitor } = require("@azure/monitor-opentelemetry");

useAzureMonitor({
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
  },
  resourceAttributes: {
    "service.name": "Bufdir.FSA.Strapi",
    "project": "fsa"
  }
});
```

---

## Fase 3: Infrastrukturmonitorering

### Oppgave 3.1: Monitorer Azure App Service (FSA.Backend.Web)
 - Aktiver diagnostikk for FSA Web App.
 - Overvåk minnebruk og tråder, spesielt ved tunge integrasjoner.

### Oppgave 3.2: Monitorer Azure Container App (Strapi)
 - Konfigurer logginnsamling for Strapi-containeren.
 - Overvåk CPU og minne for Strapi-instansen.

### Oppgave 3.3: Databaseovervåking (Azure SQL & PostgreSQL)
 - **Azure SQL (FSA Data):** Overvåk deadlocks og DTU-bruk.
 - **PostgreSQL (Strapi):** Overvåk aktive tilkoblinger og diskplass.

---

## Fase 4: Varslingskonfigurasjon

### Oppgave 4.1: Integrasjonsvarsler
 - **Digipost:** Varsle ved feilede forsendelser > 5% siste time.
 - **DSF (Bambus):** Varsle ved timeout eller 4xx/5xx feil mot Bambus-API.

### Oppgave 4.2: Klientside-feil
 - Varsle ved unormal økning i JavaScript-feil i React-frontend.

### Oppgave 4.3: Valideringsfeil og logikkavvik
 - Logg kritiske valideringsfeil i FSA-skjemaer som ikke skyldes brukerfeil (f.eks. data-inkonsistens).
 - Logg når integrasjoner (Digipost/DSF) returnerer suksess, men innholdet er ugyldig for forretningslogikken.
  - Opprett varsel for "Business Logic Errors" ved bruk av `span.recordException()` eller tilsvarende med tilpassede egenskaper.

#### Eksempel på Logging av Forretningsfeil i React
```typescript
import { appInsights } from './monitoring/appInsights';

const handleSubmit = (data) => {
    if (!isValidBusinessData(data)) {
        appInsights.trackException({ 
            exception: new Error('Invalid Business Data'),
            properties: { 
                errorCode: 'FSA-102',
                severity: 'Critical'
            }
        });
        // Håndter feil i UI
    }
}
```

---

## Fase 5: Dashboards og visualisering

### Oppgave 5.1: FSA-spesifikt dashboard
 - Lag trakt-visualisering for skjemainnsending (Startet -> Validert -> Sendt).
 - Vis helsetilstand for eksterne avhengigheter (Digipost, DSF).

---

## Fase 6: Dokumentasjon og runbooks

### Oppgave 6.1: Runbooks for FSA
 - Opprett runbook for feilsøking av integrasjonsfeil (f.eks. Digipost).
 - Opprett runbook for PostgreSQL-problemer i Strapi.
 - Se [veiledning](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md) for runbooks.

---

## Fase 7: Overvåking av sertifikater og secrets

FSA har kritiske integrasjoner mot Digipost og DSF (Bambus), samt bruk av Strapi, som er avhengige av gyldige sertifikater og secrets.

### Oppgave 7.1: Overvåk integrasjonssertifikater
- Sørg for at sertifikater som brukes mot Digipost og DSF er lagret i Azure Key Vault som "Certificates".
- Aktiver "CertificateNearExpiry" varsling i Key Vault for disse spesifikke sertifikatene.
- Opprett Availability Tests for integrasjonsendepunkter for å fange opp SSL-feil.

### Oppgave 7.2: Overvåk ID-porten og Maskinporten Secrets
- Opprett Log Search Alerts for utløp av secrets som brukes til autentisering mot ID-porten og Maskinporten.
- Verifiser varsling for:
    - **Azure AD Client Secret** (`InternalResources:ClientSecret`): Brukes for backend-autentisering.
    - **Strapi Secrets** (`JWT_SECRET`, `API_TOKEN_SALT` etc.): Selv om disse ikke utløper automatisk, bør de overvåkes for uautorisert tilgang via Key Vault-logger.

---

## Fase 8: Spesifikke metrikker og spor (Metrics & Traces)

Dette kapittelet beskriver spesifikke metrikker og spor som er relevante for finspissing av overvåkingsmodellen for bufdirno-fsa.

### Oppgave 8.1: Implementering
 - Implementer måling av følgende tekniske og funksjonelle metrikker:
    - **Metrikker (Metrics):**
        - `fsa.form.completion_rate`: Forholdet mellom påbegynte og fullførte skjemaer.
        - `fsa.integration.latency`: Responstid for kall mot Digipost og DSF (Bambus).
        - `fsa.user.session_duration`: Gjennomsnittlig tid en bruker bruker i applikasjonen.
        - `fsa.validation.failure_count`: Antall ganger validering feiler (identifiserer vanskelige skjemafelter).
        - `strapi.eventloop.delay`: Event loop forsinkelse i Strapi (viktig for API-respons).
        - `strapi.memory.usage`: Minneforbruk for CMS-containeren.
    - **Sporing (Traces):**
        - `SubmissionFlow`: Detaljert sporing av hele innsendingsprosessen, fra validering til arkivering.
        - `ExternalAuthTrace`: Sporing av autentiseringsflyten mot eksterne ID-portaler.
        - `StrapiHookExecution`: Sporing av Strapi Lifecycle Hooks (f.eks. ved lagring av innhold).
        - `DatabaseConnectionLatency`: Sporing av tid brukt på å etablere tilkobling til PostgreSQL.
