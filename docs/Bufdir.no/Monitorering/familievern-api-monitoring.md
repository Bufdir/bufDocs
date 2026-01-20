# Monitoreringsoppgaver for familievern-api

## Gevinst med monitorering (Brukerhistorie)
**Som** systemforvalter for familievern-api,
**ønsker jeg** full oversikt over ytelse og integrasjoner i App Service,
**slik at** vi kan sikre driftsstabilitet og effektivt feilsøke sammenhengen mellom portalen og API-et.

### Akseptansekriterier
 - API-ets responstid og feilrate overvåkes kontinuerlig.
 - Distributed tracing viser sammenhengen mellom portalen og familievern-api.
 - Det sendes varsel ved høy belastning på App Service (CPU/minne).
 - Integrasjonspunkter logges slik at treghet kan isoleres til spesifikke avhengigheter.

Dette dokumentet beskriver oppgavene som kreves for å sette opp monitorering for **familievern-api** (App Service).

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
 - Koble `familievern-api` til den felles Application Insights-ressursen for Bufdirno for å sikre distribuert sporing (Distributed Tracing).
 - Verifiser at `APPLICATIONINSIGHTS_CONNECTION_STRING` i Azure peker til den felles ressursen.

### Oppgave 1.2: .NET API-instrumentering (OpenTelemetry)
 - Implementer OpenTelemetry i prosjektet.
 - Sikre at `Distributed Tracing` fungerer mellom portalen og dette API-et ved å bruke W3C Trace Context.
 - Sett `OTEL_SERVICE_NAME=Bufdir.Familievern.API`.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
Legg til følgende pakker:
`OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore`, `OpenTelemetry.Instrumentation.SqlClient`, og `Azure.Monitor.OpenTelemetry.AspNetCore`.

**Eksempel på konfigurasjon i `Program.cs`:**
```csharp
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var serviceName = "Bufdir.Familievern.API";

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

### Oppgave 2.1: Azure App Service
 - Aktiver HTTP-logging og diagnostikk til felles Log Analytics Workspace.
 - Overvåk CPU og Minne for App Service Planen.
 - Overvåk antall aktive tilkoblinger og responstider.

---

## Fase 3: Varslingskonfigurasjon

### Oppgave 3.1: Tilgjengelighet
 - Sett opp syntetiske tester (URL ping-test) for helsesjekk-endepunktet (f.eks. `/health`).
 - Varsle dersom responstid overstiger 2 sekunder.

### Oppgave 3.2: Feilrater
 - Varsle ved unormal økning i HTTP 5xx-feil.

---

## Fase 4: Dokumentasjon og runbooks

### Oppgave 4.1: Runbooks
 - Opprett runbook for gjenoppretting av API-forbindelser ved nettverksbrudd.
 - Se [veiledning for runbooks](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md).

---

## Fase 5: Overvåking av sertifikater og secrets

Familievern-api benytter Azure App Service og kommuniserer med eksterne ressurser.

### Oppgave 5.1: Overvåk SSL for API-endepunktet
- Sett opp en syntetisk test (Availability Test) i Application Insights som overvåker `https://familievern-api.bufdir.no` (eller tilsvarende) for å fange opp utløpte SSL-sertifikater.

### Oppgave 5.2: Overvåk Secrets i Key Vault
- Aktiver varsling for utløp av secrets som brukes til autentisering eller tilgang til Azure Storage.

---

## Fase 6: Spesifikke metrikker og spor (Metrics & Traces)

Dette kapittelet beskriver spesifikke metrikker og spor som er relevante for finspissing av overvåkingsmodellen for familievern-api.

### Oppgave 6.1: Implementering
 - Implementer måling av følgende:
    - **Metrikker (Metrics):**
        - `api.request.size`: Størrelse på innkommende forespørsler.
        - `api.response.size`: Størrelse på utgående svar.
        - `api.dependency.latency`: Responstid for underliggende tjenester eller databaser.
    - **Sporing (Traces):**
        - `DataRetrieval`: Sporing av komplekse datahentingsoperasjoner.
