# Monitoreringsoppgaver for newsletter-api

## Gevinst med monitorering (Brukerhistorie)
**Som** kommunikasjonsansvarlig,
**ønsker jeg** bekreftelse på at nyhetsbrev blir levert og at utsendelseskøen fungerer som den skal,
**slik at** vi kan sikre at viktig informasjon når ut til alle mottakere uten forsinkelser.

### Akseptansekriterier
 - Suksessrate for levering av nyhetsbrev er synlig i et dashboard.
 - Kø-lengde og prosesseringskapasitet overvåkes for å unngå flaskehalser.
 - Det sendes varsel hvis utsendelsesbatcher feiler eller tar unormalt lang tid.
 - Individuelle utsendelser kan spores fra kø til leveranse via traces.

Dette dokumentet beskriver oppgavene som kreves for å sette opp monitorering for **newsletter-api** (Container App).

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
 - Koble `newsletter-api` til den felles Application Insights-ressursen for Bufdirno for å sikre distribuert sporing (Distributed Tracing).
 - Verifiser at `APPLICATIONINSIGHTS_CONNECTION_STRING` i Azure peker til den felles ressursen.

### Oppgave 1.2: .NET API-instrumentering (OpenTelemetry)
 - Implementer OpenTelemetry i modulen.
 - Sikre at `Distributed Tracing` fungerer mellom portalen og dette API-et ved å bruke W3C Trace Context.
 - Sett `OTEL_SERVICE_NAME=Bufdir.Newsletter.API`.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
Legg til følgende pakker:
`OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore`, `OpenTelemetry.Instrumentation.SqlClient`, og `Azure.Monitor.OpenTelemetry.AspNetCore`.

**Eksempel på konfigurasjon i `Program.cs`:**
```csharp
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var serviceName = "Bufdir.Newsletter.API";

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
 - Opprett runbook for feilede bakgrunnsjobber i `newsletter-api`.
 - Se [veiledning for runbooks](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md).

---

## Fase 5: Overvåking av sertifikater og secrets

Newsletter-api integrerer med eksterne e-postleverandører (f.eks. SendGrid) og nyhetsbrevsystemer (Make), og krever gyldige API-nøkler.

### Oppgave 5.1: Overvåk API-nøkler og Client Secrets
- Sørg for at alle API-nøkler er lagret i Azure Key Vault.
- Aktiver varsling for utløp av secrets i Key Vault.
- Spesielt viktig for:
    - **Make (Dialog) API Key** (`Services:Make:ApiKey`): Brukes for integrasjon mot nyhetsbrevsystemet.
    - **SendGrid API Key**: Brukes for e-postleveranse.
    - **Azure AD Client Secret**: Brukes for autentisering mot andre moduler.

### Oppgave 5.2: Overvåk SSL for API-endepunktet
- Sett opp Availability Test i Application Insights for å overvåke SSL-sertifikatet til API-endepunktet.

---

## Fase 6: Spesifikke metrikker og spor (Metrics & Traces)

Dette kapittelet beskriver spesifikke metrikker og spor som er relevante for finspissing av overvåkingsmodellen for newsletter-api.

### Oppgave 6.1: Implementering
 - Implementer måling av følgende:
    - **Metrikker (Metrics):**
        - `newsletter.delivery.success_rate`: Prosentandel vellykkede utsendelser.
        - `newsletter.queue.length`: Antall e-poster som venter på utsendelse.
        - `newsletter.process.duration`: Tid det tar å prosessere en hel utsendelsesbatch.
    - **Sporing (Traces):**
        - `EmailDeliveryTrace`: Full sporbarhet for en enkelt e-post fra kø til SMTP-server.
