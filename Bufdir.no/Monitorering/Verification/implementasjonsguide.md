# Implementasjonsguide: Fix av Monitorering og Infrastruktur

Her er de konkrete endringene som må gjøres i koden (eller Azure Portal) for å løse de kritiske problemene i FSA og Bufdirno (Site).

---

### 1. FSA Backend (bufdirno-fsa)

#### Fil: `bufdirno-fsa/FSA.Backend.Web/Configuration/ConfigureCoreServices.cs`

**Hva skal gjøres:** 
1.  Fiks **CORS-blokkering** ved å tillate `traceparent`.
2.  Oppgrader til **`UseAzureMonitor()`** for å få full overvåking (Traces, Metrics, Logs).
3.  Konfigurer **Forwarded Headers** for Application Gateway.

**Kodeendring:**
Erstatt den manuelle `AddOpenTelemetry()`-blokken (linje 163–188) med følgende:

```csharp
// 1. Konfigurer Forwarded Headers for App Gateway (Viktig for IP og HTTPS)
services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownNetworks.Clear();
    options.KnownProxies.Clear();
});

// 2. Fiks CORS (Viktig for traceparent/produksjonsstopp)
services.AddCors(options =>
{
    options.AddDefaultPolicy(builder =>
    {
        builder.AllowAnyOrigin() // Spesifiser domener i produksjon
               .AllowAnyMethod()
               .AllowAnyHeader()
               .WithExposedHeaders("traceparent", "tracestate");
    });
});

// 3. Oppgrader OpenTelemetry til anbefalt metode
services.AddOpenTelemetry().UseAzureMonitor(); 
```

---

#### Fil: `bufdirno-fsa/FSA.Backend.Web/Configuration/ConfigureWebApp.cs`

**Hva skal gjøres:** 
Aktiver **Forwarded Headers**-middleware øverst i pipelinen for å sikre korrekt klient-IP og HTTPS-støtte bak Application Gateway.

**Kodeendring:**
Legg til følgende linje som det første kallet inne i `ConfigureFsaWeb`-metoden:

```csharp
public static void ConfigureFsaWeb(this WebApplication app, WebApplicationBuilder builder)
{
    app.UseForwardedHeaders(); // Legg til denne helt øverst
    // ... rest av koden ...
}
```

---

### 2. Bufdirno Site (bufdirno)

#### Fil: `bufdirno/src/Site/Program.cs`

**Hva skal gjøres:** 
1.  Fjern **dobbel logging** ved å fjerne Serilog Application Insights Sink.
2.  Oppgrader til **`UseAzureMonitor()`**.

**Kodeendring:**
1.  Fjern linje 53–58 (der `UseSerilog` manuelt setter opp `ApplicationInsightsSink`).
2.  Erstatt den manuelle `AddOpenTelemetry()`-blokken (linje 67–105) med:

```csharp
services.AddOpenTelemetry().UseAzureMonitor(options => 
{
    options.ConnectionString = azureMonitorConnectionString;
});
```

*Merk: Du må legge til NuGet-pakken `Azure.Monitor.OpenTelemetry.AspNetCore` i Site-prosjektet først.*

---

#### Fil: `bufdirno/src/Site/appsettings.json`

**Hva skal gjøres:** 
Fjern Serilog sin kobling til Application Insights for å unngå dobbel fakturering.

**Kodeendring:**
Slett seksjonen `ApplicationInsightsSink` under `Serilog:WriteTo`:

```json
"ApplicationInsightsSink": {
    "Name": "ApplicationInsights",
    "Args": {
        "telemetryConverter": "BufdirWeb.Site.Infrastructure.ApplicationInsights.AppInsightsTraceTelemetryConverter, BufdirWeb.Site"
    }
}
```

---

#### Fil: `bufdirno/src/Site/Startup.cs`

**Hva skal gjøres:** 
Konfigurer **Forwarded Headers** i `ConfigureServices` slik at backenden stoler på headere fra Application Gateway.

**Kodeendring:**
Legg til følgende i `ConfigureServices`-metoden:

```csharp
services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownNetworks.Clear();
    options.KnownProxies.Clear();
});
```

---

### 3. Frontend og Strapi (Node.js)

#### Sikkerhet (FSA Frontend)
*   **Fil:** `bufdirno-fsa/FSA.Frontend.React/src/monitoring/appInsights.ts` (eller lignende)
*   **Tiltak:** Sørg for at `connectionString` ikke logges til konsollen i produksjon.
*   **Se også:** [Verifisering av JS/TS Monitorering](js-ts-monitoring-verification.md)

#### Strapi Loggstøy
*   **Fil:** `instrumentation.ts` i Strapi-prosjekter.
*   **Tiltak:** Deaktiver `CustomConsoleSpanExporter` eller `DiagConsoleLogger` i produksjon.

---

### 4. Azure Portal (Infrastruktur)

#### Application Gateway (WAF)
*   Sjekk at WAF ikke blokkerer `traceparent`-headeren (W3C Standard).
*   Sjekk at `X-Forwarded-For` og `X-Forwarded-Proto` sendes videre til backend.

#### Application Insights
*   Vurder **Sampling** (f.eks. 10-20%) i stedet for aggressiv filtrering i koden (`ErrorOnlySpanExporter`), for å få bedre innsikt i systemets helse uten ekstreme kostnader.
