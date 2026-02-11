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

### Hybrid Monitoreringsstrategi
For dette prosjektet har vi valgt en **hybrid monitoreringsmodell**:
1.  **Backend (.NET): OpenTelemetry**
    *   **Hvorfor:** Industristandard for moderne backend-instrumentering. Gir bedre ytelse og er Microsofts primære anbefaling for .NET.
2.  **Korrelasjon:** Bruker **W3C Trace Context** som standard, noe som sikrer at distribuert sporing fungerer sømløst på tvers av tjenester.

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
 - Installer **OpenTelemetry** SDK i `familievern-api`.
 - Konfigurer OpenTelemetry for å fange opp SQL Server-kall og HTTP-trafikk ved bruk av Azure Monitor exporter.
 - Sett Cloud Role Name (Service Name) til `Bufdir.Familievern.API`.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
Legg til følgende pakke: `Azure.Monitor.OpenTelemetry.AspNetCore`.

**Eksempel på konfigurasjon i `Program.cs`:**
```csharp
using Azure.Monitor.OpenTelemetry.AspNetCore;
using OpenTelemetry.Resources;

// I ConfigureServices / builder:
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource.AddService("Bufdir.Familievern.API"))
    .UseAzureMonitor(options =>
    {
        options.ConnectionString = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];
    });

// Filtrer bort støyende ruter (typiske 404)
builder.Services.ConfigureOpenTelemetryTracerProvider((sp, builder) =>
    builder.AddAspNetCoreInstrumentation(options =>
    {
        options.Filter = (httpContext) =>
        {
            var path = httpContext.Request.Path.Value;
            return path == null ||
                   (!path.Contains("favicon") &&
                    !path.Contains("/health") &&
                    !path.EndsWith(".map"));
        };
    }));
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

Familievern-api benytter Azure App Service og kommuniserer med eksterne ressurser og Azure Storage.

### Oppgave 5.1: Overvåk SSL for API-endepunktet
- Sett opp en syntetisk test (Availability Test) i Application Insights som overvåker API-endepunktet for å fange opp utløpte SSL-sertifikater.

### Oppgave 5.2: Overvåk Secrets i Key Vault
- Konfigurer varsling for utløp av secrets i Key Vault.
- Spesielt viktig for:
    - **Azure AD Client Secret**: Brukes for autentisering.
    - **SendGrid API Key** (`Mail:SendgridKey`): Brukes for utsendelse av e-post.
    - **Azure Storage Access Keys**: Overvåk aksesslogger for å sikre at rotasjon utføres ved behov.

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
