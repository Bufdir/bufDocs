# Monitoreringsoppgaver for Statistikksystemet (stat-system)

## Gevinst med monitorering (Brukerhistorie)
**Som** dataanalytiker for statistikksystemet,
**ønsker jeg** full kontroll på datakvalitet og ytelse i tunge aggregeringsoperasjoner,
**slik at** vi kan levere korrekte statistiske data raskt og pålitelig til våre brukere.

### Akseptansekriterier
 - Tunge aggregeringsoperasjoner spores for å identifisere ytelsesflaskehalser.
 - Data-synkronisering mellom Strapi og .NET API overvåkes og varsles ved feil.
 - Kvalitetsavvik i data (forretningslogikk) logges som custom events.
 - Dashboards viser ytelse for både innholdsleveranse (Strapi) og datauttrekk (Backend).

Dette dokumentet beskriver oppgavene som kreves for å sette opp monitorering for **Statistikksystemet**, som består av **stat-content-strapi5** (Strapi 5 CMS) og **stat-backend** (BufdirStatisticsDataAPI).

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
 - Koble både `stat-content-strapi5` og `stat-backend` til den felles Application Insights-ressursen for Bufdirno for å sikre full korrelasjon.
 - Verifiser at `APPLICATIONINSIGHTS_CONNECTION_STRING` er tilgjengelig som miljøvariabel i både Azure Container App (Strapi) og App Service (Backend).
 - Konfigurer ressurs-tagger: `project: statistics`, `service: stat-system`.

---

## Fase 2: Applikasjonsinstrumentering

### Oppgave 2.1: Instrumenter Strapi 5 (Node.js) med OpenTelemetry
 - Installer nødvendige OpenTelemetry-pakker i `stat-content-strapi5`:
  ```bash
  npm install @opentelemetry/api @opentelemetry/sdk-node \
    @opentelemetry/auto-instrumentations-node \
    @azure/monitor-opentelemetry-exporter
  ```
 - Opprett en initialiseringsfil for OpenTelemetry (f.eks. `src/otel.ts`).
 - Sørg for at instrumenteringen starter før Strapi-applikasjonen.

#### Implementasjonsveiledning for OpenTelemetry i Strapi
**Eksempel på `src/otel.ts`:**
```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { AzureMonitorTraceExporter } from '@azure/monitor-opentelemetry-exporter';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'Bufdir.Stat.Content.Strapi',
  }),
  traceExporter: new AzureMonitorTraceExporter({
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING,
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-fs': { enabled: false },
    }),
  ],
});

sdk.start();
```

### Oppgave 2.2: Moderniser stat-backend med OpenTelemetry
Prosjektet bruker i dag `AddApplicationInsightsTelemetry()`. Dette bør moderniseres til OpenTelemetry.

 - Installer OpenTelemetry NuGet-pakker i `BufdirStatisticsDataAPI`:
    - `OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore`, `OpenTelemetry.Instrumentation.Http`, `OpenTelemetry.Instrumentation.SqlClient`, `Azure.Monitor.OpenTelemetry.AspNetCore`.
 - Konfigurer OpenTelemetry i `Startup.cs` eller `Program.cs`.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
```csharp
var serviceName = "Bufdir.Statistics.API";

services.AddOpenTelemetry()
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
            .AddAzureMonitorTraceExporter(o => o.ConnectionString = Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"]);
    })
    .WithMetrics(metrics =>
    {
        metrics
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddRuntimeInstrumentation();
    });
```

---

## Fase 3: Infrastrukturmonitorering

### Oppgave 3.1: Monitorer Azure Container App (Strapi)
 - Konfigurer logginnsamling (stdout/stderr) til felles Log Analytics Workspace.
 - Overvåk ressursbruk (CPU og Minne) og antall container-restarter.

### Oppgave 3.2: Monitorer Azure App Service (Backend)
 - Aktiver diagnostikkinnstillinger for App Service.
 - Overvåk CPU og minnebruk, spesielt ved tunge statistiske spørringer.

### Oppgave 3.3: Databaseovervåking
 - **MySQL (Strapi):** Aktiver overvåking for MySQL-instansen. Overvåk tilkoblinger og diskbruk.
 - **MongoDB / SQL Server (Backend):** Sett opp spesifikk overvåking av responstider og gjennomstrømning avhengig av databasetype.

---

## Fase 4: Varslingskonfigurasjon

### Oppgave 4.1: Tilgjengelighet
 - Sett opp syntetiske tester mot Strapi Admin-panelet og Backend Swagger/helsesjekk.
 - Varsle ved responstid > 5 sekunder for innholdsleveranse eller statistikk-uttrekk.

### Oppgave 4.2: Feilrater
 - Varsle ved økning i HTTP 5xx-feil fra både Strapi og Backend.
 - Overvåk logger for kritiske feil knyttet til databaseforbindelser.

### Oppgave 4.3: Monitorering av datakvalitet og synkronisering
 - Logg hendelse når data-synkronisering mellom Strapi og .NET API starter og slutter.
 - Varsle dersom synkronisering feiler eller tar unormalt lang tid (logikkfeil i transformasjon).
 - Logg "InconsistentDataFound" som en Custom Event hvis API-et mottar data som ikke validerer mot forretningsreglene.

---

## Fase 5: Dashboards og visualisering

### Oppgave 5.1: Systemdashboard for Statistikk
 - Vis ytelse for de mest brukte innholdsendepunktene i Strapi.
 - Vis antall API-kall og feilrate for statistikktjenesten.
 - Vis ressursbruk for både Container App og App Service i samme bilde.

---

## Fase 6: Dokumentasjon og runbooks

### Oppgave 6.1: Runbooks for statistikksystemet
 - Opprett runbook for "Database Connection Pool Exhaustion" (Strapi).
 - Opprett runbook for feilsøking ved treghet i datauthenting (Backend).
 - Se [veiledning](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md) for runbooks.

---

## Fase 7: Overvåking av sertifikater og secrets

Statistikksystemet er avhengig av sikker kommunikasjon mellom Strapi og .NET API-et, samt tilgang til databaser og Azure Storage.

### Oppgave 7.1: Overvåk SSL for API og CMS
- Sett opp Availability Tests i Application Insights for både `stat-backend` og `stat-content-strapi5` for å overvåke SSL-sertifikater.

### Oppgave 7.2: Overvåk API-nøkler og Secrets
- Konfigurer varsling for utløp av secrets i Azure Key Vault.
- Spesielt viktig for:
    - **Azure AD Client Secret** (`AzureAd:ClientSecret`): Brukes for autentisering i backend.
    - **Statistics API Token** (`STATISTICS_API_TOKEN`): Brukes for integrasjonen mellom Strapi og backend.
    - **Strapi Secrets** (`JWT_SECRET`, `API_TOKEN_SALT` etc.): Overvåk aksesslogger i Key Vault.
    - **Cosmos DB / MongoDB Connection String**: Sikre at autentisering er gyldig.

---

## Fase 8: Spesifikke metrikker og spor (Metrics & Traces)

Dette kapittelet beskriver spesifikke metrikker og spor som er relevante for finspissing av overvåkingsmodellen for statistikksystemet.

### Oppgave 8.1: Implementering
 - Implementer måling av følgende tekniske og funksjonelle metrikker:
    - **Metrikker (Metrics):**
        - `stat.data_import.duration`: Tid det tar å importere statistikkdata til API-et.
        - `stat.api.query_complexity`: Mål på hvor komplekse statistikkspørringer brukerne kjører.
        - `stat.cms.publish_latency`: Tid fra innhold endres i Strapi til det er synlig i API-et.
        - `strapi.request.concurrency`: Antall samtidige forespørsler mot Strapi-API-et.
        - `nodejs.gc.pause_time`: Tid applikasjonen er satt på pause under garbage collection.
    - **Sporing (Traces):**
        - `DataAggregation`: Sporing av tunge aggregeringsoperasjoner i statistikk-API-et.
        - `CmsSyncFlow`: Sporing av dataflyten mellom Strapi og .NET API-et.
        - `ExcelGeneration`: Sporing av ressurskrevende Excel-eksport i statistikksystemet.
        - `DnsLookupDuration`: Sporing av tid brukt på DNS-oppslag mot eksterne kilder.

#### Implementasjonsveiledning for spesifikke spor (Traces)

For å spore komplekse operasjoner som går på tvers av tjenester eller tar lang tid, bruker vi OpenTelemetry-sporing.

**1. DataAggregation (C# / .NET API)**
Dette sporet brukes for å overvåke tunge beregninger i `stat-backend`.

```csharp
using System.Diagnostics;

public class StatisticsService
{
    private static readonly ActivitySource _activitySource = new ActivitySource("Bufdir.Statistics.API");

    public async Task<AggregateResult> AggregateData(AggregateRequest request)
    {
        using var activity = _activitySource.StartActivity("DataAggregation");
        activity?.SetTag("stat.query_type", request.Type);
        activity?.SetTag("stat.dataset_id", request.DatasetId);

        try
        {
            activity?.AddEvent(new ActivityEvent("CalculationStarted"));
            // Utfør aggregering...
            var result = await PerformHeavyCalculation(request);
            
            activity?.SetTag("stat.result_count", result.Count);
            activity?.SetStatus(ActivityStatusCode.Ok);
            return result;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            throw;
        }
    }
}
```

**2. CmsSyncFlow (Node.js & C#)**
For å spore dataflyten fra Strapi til .NET API-et, må vi sende med Trace Context.

**I Strapi (Node.js - når synkronisering trigges):**
```typescript
import { trace, SpanStatusCode, propagation, Context } from '@opentelemetry/api';

const tracer = trace.getTracer('stat-content-strapi');

async function syncToBackend(data: any) {
  await tracer.startActiveSpan('CmsSyncFlow', async (span) => {
    try {
      span.setAttribute('cms.content_id', data.id);
      
      // Pakk ut trace context for å sende den videre i HTTP-headeren
      const headers = {};
      propagation.inject(trace.getActiveSpan()?.spanContext() ? trace.setSpan(trace.getActiveSpan()!) : undefined, headers);

      await axios.post(process.env.BACKEND_URL + '/sync', data, { headers });
      
      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

**I .NET API (Mottak av synkronisering):**
OpenTelemetry vil automatisk plukke opp `traceparent`-headeren fra Strapi og koble seg på det eksisterende sporet dersom `AddAspNetCoreInstrumentation()` er konfigurert.

```csharp
[HttpPost("sync")]
public async Task<IActionResult> ReceiveSync([FromBody] SyncData data)
{
    // Activity.Current vil her automatisk være en del av "CmsSyncFlow" fra Strapi
    Activity.Current?.AddEvent(new ActivityEvent("DataReceivedInBackend"));
    Activity.Current?.SetTag("backend.process_id", Guid.NewGuid());
    
    await _syncService.Process(data);
    return Ok();
}
```
