# Monitoreringsoppgaver for fosterhjem-api

## Gevinst med monitorering (Brukerhistorie)
**Som** fagansvarlig for fosterhjemsløsningen,
**ønsker jeg** proaktiv overvåking av søknadshåndteringen og container-helsen,
**slik at** vi kan garantere en sømløs søknadsflyt og rette feil før de påvirker saksbehandlingen.

### Akseptansekriterier
 - Container-helse (restarts, ressursbruk) overvåkes og varsles.
 - Forretningsprosessen for søknadshåndtering spores som en sammenhengende operasjon.
 - Spesifikke metrikker for innsendingsflyt er visualisert i et dashboard.
 - Feil i søknadsprosessen logges med tilstrekkelig kontekst (f.eks. søknads-ID) for rask feilsøking.

Dette dokumentet beskriver oppgavene som kreves for å sette opp monitorering for **fosterhjem-api** (Container App).

## Innholdsfortegnelse
- [Fase 1: Applikasjonsinstrumentering](#fase-1-applikasjonsinstrumentering)
- [Fase 2: Infrastrukturmonitorering](#fase-2-infrastrukturmonitorering)
- [Fase 3: Varslingskonfigurasjon](#fase-3-varslingskonfigurasjon)
- [Fase 4: Dokumentasjon og runbooks](#fase-4-dokumentasjon-og-runbooks)
- [Fase 5: Overvåking av sertifikater og secrets](#fase-5-overvåking-av-sertifikater-og-secrets)
- [Fase 6: Spesifikke metrikker og spor (Metrics & Traces)](#fase-6-spesifikke-metrikker-og-spor-metrics--traces)

---

## Fase 1: Applikasjonsinstrumentering

### Oppgave 1.1: Bruk felles Application Insights
 - Koble `fosterhjem-api` til den felles Application Insights-ressursen for Bufdirno for å sikre distribuert sporing (Distributed Tracing).
 - Verifiser at `APPLICATIONINSIGHTS_CONNECTION_STRING` i Azure peker til den felles ressursen.

### Oppgave 1.2: .NET API-instrumentering (OpenTelemetry)
 - Implementer OpenTelemetry i prosjektet.
 - Sikre at `Distributed Tracing` fungerer mellom portalen og dette API-et ved å bruke W3C Trace Context.
 - Sett `OTEL_SERVICE_NAME=Bufdir.Fosterhjem.API`.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
Legg til følgende pakker:
`OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore`, `OpenTelemetry.Instrumentation.SqlClient`, og `Azure.Monitor.OpenTelemetry.AspNetCore`.

**Eksempel på konfigurasjon i `Program.cs`:**
```csharp
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var serviceName = "Bufdir.Fosterhjem.API";

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

## Fase 2: Infrastrukturmonitorering

### Oppgave 2.1: Azure Container App
 - Konfigurer loggstrømming til felles Log Analytics Workspace.
 - Overvåk container-restarts og status for replicas.
 - Overvåk CPU og Minne for containeren.

---

## Fase 3: Varslingskonfigurasjon

### Oppgave 3.1: Tilgjengelighet
 - Sett opp syntetiske tester (URL ping-test) for helsesjekk-endepunktet (f.eks. `/health`).
 - Varsle dersom responstid overstiger 2 sekunder.

### Oppgave 3.2: Funksjonsfeil
 - Varsle ved unormal økning i container-restarter.

---

## Fase 4: Dokumentasjon og runbooks

### Oppgave 4.1: Runbooks
 - Opprett runbook for feilsøking av container-feil og oppstartsproblemer.
 - Se [veiledning for runbooks](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md).

---

## Fase 5: Overvåking av sertifikater og secrets

Fosterhjem-api kjører som en Container App og er avhengig av sikker tilgang til Azure ressurser.

### Oppgave 5.1: Overvåk SSL for API-endepunktet
- Sett opp Availability Test i Application Insights for å overvåke SSL-sertifikatet til API-et.

### Oppgave 5.2: Overvåk Managed Identity og Secrets
- Overvåk utløpsdato på eventuelle secrets i Key Vault som brukes til integrasjoner.
- Verifiser at tilgang via Managed Identity fungerer (logges som teknisk metrikk).

---

## Fase 6: Spesifikke metrikker og spor (Metrics & Traces)

Dette kapittelet beskriver spesifikke metrikker og spor som er relevante for finspissing av overvåkingsmodellen for fosterhjem-api.

### Oppgave 6.1: Implementering
 - Implementer måling av følgende:
    - **Metrikker (Metrics):**
        - `api.container.startup_time`: Tid fra container-start til API-et er klart.
        - `api.request.concurrency`: Antall samtidige forespørsler som håndteres.
    - **Sporing (Traces):**
        - `ApplicationProcess`: Sporing av søknadshåndtering for fosterhjem.

#### Implementasjonsveiledning for spesifikke spor (Traces)

For å spore en forretningsprosess som "søknadshåndtering", bruker vi `ActivitySource` i .NET. Dette gjør at vi kan se hele forløpet som en sammenhengende operasjon i Application Insights.

**Eksempel på implementering av `ApplicationProcess`:**

```csharp
using System.Diagnostics;

public class ApplicationService
{
    // Definer ActivitySource (bør være statisk og gjenbrukes)
    private static readonly ActivitySource _activitySource = new ActivitySource("Bufdir.Fosterhjem.API");

    public async Task ProcessApplication(string applicationId)
    {
        // Start et nytt spor (span)
        using var activity = _activitySource.StartActivity("ApplicationProcess");
        
        // Legg til attributter for å kunne filtrere/søke i Application Insights
        activity?.SetTag("application.id", applicationId);
        activity?.SetTag("application.type", "Fosterhjem");
        
        try 
        {
            // Steg 1: Validering
            activity?.AddEvent(new ActivityEvent("ValidationStarted"));
            await Validate(applicationId);
            
            // Steg 2: Lagring
            activity?.AddEvent(new ActivityEvent("StorageStarted"));
            await SaveToDatabase(applicationId);
            
            activity?.SetStatus(ActivityStatusCode.Ok);
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
