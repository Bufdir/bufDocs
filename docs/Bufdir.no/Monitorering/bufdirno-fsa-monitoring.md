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
 - Installer OpenTelemetry NuGet-pakker i `FSA.Backend.Web`-modulen.
 - Konfigurer OpenTelemetry i `Program.cs` for å fange opp SQL Server-kall og HTTP-trafikk.
 - Legg til connection string fra Key Vault.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
Legg til følgende pakker i `FSA.Backend.Web`:
`OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore`, `OpenTelemetry.Instrumentation.SqlClient`, og `Azure.Monitor.OpenTelemetry.AspNetCore`.

**Eksempel på konfigurasjon i `Program.cs`:**
```csharp
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var serviceName = "Bufdir.FSA.Backend";

builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .AddSource(serviceName)
            .SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(serviceName))
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddSqlClientInstrumentation(options =>
            {
                options.SetDbStatementForStoredProcedures = true;
                options.SetDbStatementForText = true;
                options.RecordException = true;
            })
            .AddAzureMonitorTraceExporter(o => o.ConnectionString = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"]);
    })
    .WithMetrics(metrics =>
    {
        metrics
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddRuntimeInstrumentation();
    });
```

### Oppgave 2.2: Instrumenter React Frontend (OpenTelemetry)
 - Installer OpenTelemetry npm-pakker for web:
  ```bash
  npm install @opentelemetry/api @opentelemetry/sdk-trace-web \
    @opentelemetry/instrumentation-xml-http-request \
    @opentelemetry/instrumentation-fetch \
    @opentelemetry/resources \
    @opentelemetry/semantic-conventions \
    @opentelemetry/exporter-trace-otlp-http
  ```
 - Opprett en initialiseringsfil for OpenTelemetry i React-appen.
 - Sørg for at `Distributed Tracing` headere (W3C) sendes med API-kall til backenden.

#### Implementasjonsveiledning for React med OpenTelemetry (Browser)

For å sikre full sporbarhet fra React-frontend helt til databasen, bruker vi OpenTelemetry Web SDK direkte i browseren.

**Eksempel på `src/otel-frontend.ts`:**

```typescript
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { getWebAutoInstrumentations } from '@opentelemetry/auto-instrumentations-web';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { AzureMonitorTraceExporter } from '@azure/monitor-opentelemetry-exporter';

const provider = new WebTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'Bufdir.FSA.Frontend.Browser',
  }),
});

// Exporter sender telemetri direkte fra browser til Azure Application Insights
const exporter = new AzureMonitorTraceExporter({
  connectionString: "DIN_CONNECTION_STRING_HER",
});

provider.addSpanProcessor(new BatchSpanProcessor(exporter));

registerInstrumentations({
  instrumentations: [
    getWebAutoInstrumentations({
      '@opentelemetry/instrumentation-fetch': {
        // Viktig: Dette sprer Trace Context til backenden (W3C standard)
        propagateTraceHeaderCorsUrls: [ /fsa-api\.bufdir\.no/g ], 
      },
      '@opentelemetry/instrumentation-xml-http-request': {
        propagateTraceHeaderCorsUrls: [ /fsa-api\.bufdir\.no/g ],
      },
    }),
  ],
  tracerProvider: provider,
});

provider.register();
```

**Viktige fordeler med browser-monitorering:**
1. **Real User Monitoring (RUM):** Man ser nøyaktig hva brukeren opplever, inkludert treghet i nettverk og rendering i browseren.
2. **Distributed Tracing:** Når en bruker klikker på "Send søknad", kan vi følge den eksakte forespørselen gjennom React -> .NET API -> Database.
3. **Feilhåndtering:** JavaScript-feil fanges opp automatisk og korreleres med brukerens sesjon.

> **Sikkerhetsmerknad:** Connection String blir eksponert i klientkoden. Dette er normal praksis for RUM-verktøy, da strengen kun tillater innsending av data (ingestion), ikke lesing av data. For maksimal sikkerhet kan man sette opp en proxy som mottar OTLP-trafikk og sender den videre til Azure.

### Oppgave 2.3: Instrumenter Strapi CMS (Container App)
 - Konfigurer OpenTelemetry Node.js SDK for Strapi.
 - Sett `OTEL_SERVICE_NAME=Bufdir.FSA.Strapi`.

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
// Bruk en custom tracer for å logge hendelser eller unntak
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('fsa-frontend-logic');

const handleSubmit = (data) => {
    if (!isValidBusinessData(data)) {
        tracer.startActiveSpan('Business Logic Error', (span) => {
            span.setAttribute('errorCode', 'FSA-102');
            span.setAttribute('severity', 'Critical');
            span.recordException(new Error('Invalid Business Data'));
            span.end();
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

FSA har kritiske integrasjoner mot Digipost og DSF (Bambus) som er avhengige av gyldige sertifikater og secrets.

### Oppgave 7.1: Overvåk integrasjonssertifikater
- Sørg for at sertifikater som brukes mot Digipost og DSF er lagret i Azure Key Vault som "Certificates" (ikke bare secrets).
- Aktiver "CertificateNearExpiry" varsling i Key Vault for disse spesifikke sertifikatene.

### Oppgave 7.2: Overvåk ID-porten og Maskinporten Secrets
- Opprett Log Search Alerts for utløp av secrets som brukes til autentisering mot ID-porten og Maskinporten.

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
