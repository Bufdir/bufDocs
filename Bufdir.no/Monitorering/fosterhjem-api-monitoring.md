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
 - Koble `fosterhjem-api` til den felles Application Insights-ressursen for Bufdirno for å sikre distribuert sporing (Distributed Tracing).
 - Verifiser at `APPLICATIONINSIGHTS_CONNECTION_STRING` i Azure peker til den felles ressursen.

### Oppgave 1.2: .NET API-instrumentering (OpenTelemetry)
 - Installer **OpenTelemetry** SDK i `fosterhjem-api`.
 - Konfigurer OpenTelemetry for å fange opp SQL Server-kall og HTTP-trafikk ved bruk av Azure Monitor exporter.
 - Sett Cloud Role Name (Service Name) til `Bufdir.Fosterhjem.API`.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
Legg til følgende pakke: `Azure.Monitor.OpenTelemetry.AspNetCore`.

**Eksempel på konfigurasjon i `Program.cs`:**
```csharp
using Azure.Monitor.OpenTelemetry.AspNetCore;
using OpenTelemetry.Resources;

// I ConfigureServices / builder:
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource.AddService("Bufdir.Fosterhjem.API"))
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

Fosterhjem-api kjører som en Container App og har kritiske integrasjoner mot eksterne systemer (ROS og Oslo Kommune).

### Oppgave 5.1: Overvåk SSL for API-endepunktet
- Sett opp Availability Test i Application Insights for å overvåke SSL-sertifikatet til API-et.
- Opprett Availability Tests for eksterne integrasjonsendepunkter for å fange opp SSL-problemer hos parter.

### Oppgave 5.2: Overvåk API-nøkler og Client Secrets
- Konfigurer varsling i Key Vault for utløp av secrets.
- Spesielt viktig for:
    - **Azure AD Client Secret**: Brukes for autentisering og kommunikasjon med andre Azure-tjenester.
    - **ROS API Key** (`RosApiKey`): Brukes for integrasjon mot Bufetat ROS-system.
    - **Oslo Kommune API Key** (`Oslo:ApiKey`): Brukes for integrasjon mot Oslo kommunes system.
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

#### Implementasjonsveiledning for tilpasset sporing (Custom Events)

For å spore en forretningsprosess som "søknadshåndtering", bruker vi `TelemetryClient` i .NET. Dette gjør at vi kan se hele forløpet som en sammenhengende operasjon i Application Insights.

**Eksempel på implementering av `ApplicationProcess`:**

```csharp
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.DataContracts;

public class ApplicationService
{
    private readonly TelemetryClient _telemetryClient;

    public ApplicationService(TelemetryClient telemetryClient)
    {
        _telemetryClient = telemetryClient;
    }

    public async Task ProcessApplication(string applicationId)
    {
        // Start en ny operasjon
        using (var operation = _telemetryClient.StartOperation<RequestTelemetry>("ApplicationProcess"))
        {
            // Legg til egenskaper for å kunne filtrere/søke i Application Insights
            operation.Telemetry.Properties["application.id"] = applicationId;
            operation.Telemetry.Properties["application.type"] = "Fosterhjem";
            
            try 
            {
                // Steg 1: Validering
                _telemetryClient.TrackEvent("ValidationStarted");
                await Validate(applicationId);
                
                // Steg 2: Lagring
                _telemetryClient.TrackEvent("StorageStarted");
                await SaveToDatabase(applicationId);
                
                operation.Telemetry.Success = true;
            }
            catch (Exception ex)
            {
                operation.Telemetry.Success = false;
                _telemetryClient.TrackException(ex);
                throw;
            }
        }
    }
}
```
