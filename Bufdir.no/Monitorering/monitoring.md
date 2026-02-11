# Overordnet Plan for Monitorering i Bufdirno

Dette dokumentet gir en oversikt over monitoreringsstrategien for hele løsningen. Detaljerte oppgaver for hver modul finnes i egne filer:

- [bufdirno (Hovedportal)](./bufdirno-monitoring.md)
- [bufdirno-fsa (Family Services Application)](./bufdirno-fsa-monitoring.md)
- [Familievern-api](./familievern-api-monitoring.md)
- [Fosterhjem-api](./fosterhjem-api-monitoring.md)
- [Newsletter-api](./newsletter-api-monitoring.md)
- [stat-system (Statistikk)](./stat-system-monitoring.md)
- [Utrapporteringsbank](./utrapporteringsbank-monitoring.md)
- [Løsning av CORS-feil](#cors-feil-ved-distributed-tracing)
- [Sertifikater og Secrets](#overvåking-av-sertifikater-og-secrets)
- [Automatisering av Monitorering](./automatisering-av-monitorering.md)
- [Automatisert Fornyelse (Auto-rotation)](./auto-rotasjon-veiledning.md)
- [Spesifikke metrikker og spor](#spesifikke-metrikker-og-spor-metrics--traces)

---

## Hybrid Monitoreringsstrategi
Bufdirno benytter en **hybrid monitoreringsmodell** for å sikre optimal observabilitet på tvers av hele økosystemet. Denne strategien er valgt for å utnytte styrkene til de ulike verktøyene:

1.  **Frontend (Nettleser): Azure Application Insights SDK**
    *   **Hvorfor:** Spesialtilpasset for **Real User Monitoring (RUM)**. Håndterer klientside-spesifikke behov som brukersesjoner, sidevisninger, klikk-strømmer og JavaScript-exceptions mer sømløst enn standard OpenTelemetry i nettleseren. Det krever ingen kompleks proxy-infrastruktur (som OTLP Collector) for å sende data sikkert til Azure.
2.  **Backend (.NET & Node.js): OpenTelemetry**
    *   **Hvorfor:** Industristandard for moderne backend-instrumentering. Det er Microsofts primære anbefaling for .NET 8/9 og moderne Node.js-arkitekturer. OpenTelemetry gir bedre ytelse på serveren, er leverandørnøytral og har et rikt økosystem av instrumentering for databaser, køer og eksterne API-er.
3.  **Korrelasjon (Distributed Tracing): W3C Trace Context**
    *   **Hvorfor:** Ved å bruke den åpne standarden **W3C Trace Context** på tvers av både Application Insights SDK (frontend) og OpenTelemetry (backend), oppnår vi sømløs korrelasjon. En forespørsel kan følges fra brukerens første klikk i nettleseren, gjennom alle mikrotjenester, og helt ned til den enkelte SQL-spørring eller eksterne tjenestekall.

---

## Felles Oppgaver

### Fase 1: Grunnleggende infrastruktur
 - Opprett felles Log Analytics Workspace.
 - Opprett én felles Application Insights-ressurs (Workspace-based) for alle moduler for å sikre full korrelasjon (Distributed Tracing).
 - Konfigurer globale handlingsgrupper (Action Groups) for varsling.
 - Implementer Azure Security Center på tvers av alle abonnementer.

### Fase 2: Standardisering
 - Etabler felles navngivingskonvensjon for alle monitoreringsressurser.
 - Definer standard tagger for kostnadsstyring og filtrering.
 - Etabler struktur for Runbooks (se [veiledning](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md)).

---

## Korrelasjon og Distributed Tracing
For å kunne følge en forespørsel fra nettleseren, gjennom ulike frontender og backender, og videre til mikrotjenester og databaser, er det avgjørende at:
1. **Felles ressurs:** Alle komponenter sender telemetri til samme Application Insights-ressurs.
2. **W3C Trace Context:** Alle tjenester må støtte og videreformidle standardiserte trace-headere (gjør automatisk av både AI SDK og OpenTelemetry).
3. **Cloud Role Name:** Hver tjeneste må sette et unikt `service.name` (eller `ai.cloud.role`) for å skille dem i Application Map. Det anbefales å skille mellom `.Server` og `.Browser` for frontend-applikasjoner.

---

## Browser-monitorering og RUM (Real User Monitoring)
For applikasjoner med en frontend-del (Next.js, React) er det mulig og sterkt anbefalt å sette opp sporing og metrikker som kjører direkte i brukerens nettleser. Dette gir innsikt i:
*   **Faktisk brukeropplevelse:** Lastetider, rendering-ytelse (Core Web Vitals) og nettverksforsinkelse fra klientens ståsted.
*   **Klient-side feil:** JavaScript-unntak og feilede API-kall som ellers ikke ville vært synlige i server-logger.
*   **End-to-end sporing:** Ved bruk av W3C Trace Context kan en sporings-ID følge en forespørsel fra brukerens klikk i browseren, gjennom API-gateway, til backend-tjenester og helt ned til databasen.

### Sikkerhetshensyn ved Browser-monitorering
Når man instrumenterer koden som kjører i browseren, vil `ConnectionString` til Application Insights være synlig for sluttbrukeren.
1.  **Risikovurdering:** Denne strengen gir kun tillatelse til å *sende* data til Azure (Ingestion). Den gir ingen tilgang til å lese logger eller se andres data.
2.  **Anbefaling:** For Bufdirno anses dette som en akseptabel risiko for offentlige flater. Ved å bruke Application Insights SDK direkte i browseren unngår man behovet for en OpenTelemetry Collector proxy, noe som forenkler arkitekturen betraktelig.

---

## Monitorering av Forretningslogikk og Hendelser
For å fange opp feil som ikke er tekniske (som HTTP 500), men som er kritiske for forretningen (f.eks. "bruker har ikke tilgang til skjema", "ugyldig dataformat fra ekstern part"), brukes **Custom Events** og **Custom Exceptions**.

1. **Custom Events:** Brukes for å logge viktige hendelser (f.eks. `ApplicationSubmitted`, `ReportGenerated`).
2. **Custom Exceptions:** Brukes for å fange opp forventede forretningsfeil som krever oppfølging.
3. **Varsling:** Azure Monitor kan settes opp til å varsle når spesifikke hendelser inntreffer eller overstiger en terskel ved hjelp av KQL-spørringer mot `customEvents`- eller `exceptions`-tabellen.

---

## Estimert Kostnad for Azure Monitor
Dette er et estimat basert på standard prising i Azure (North Europe) og forventet datamengde for Bufdirno-økosystemet.

### 1. Log Analytics & Application Insights (Data Ingestion)
Azure Monitor tar betalt per GB data som lagres.
*   **Pris:** Ca. 25-30 kr per GB (Pay-as-you-go).
*   **Estimat:** For en medium løsning som Bufdirno (portal + 5-6 API-er) forventes det mellom 2 og 10 GB per måned per miljø (test/prod).
*   **Månedlig kostnad:** 50 kr - 300 kr per miljø.

### 2. Datalagring (Retention)
De første 31 dagene er inkludert gratis.
*   **Pris:** Ca. 1.20 kr per GB per måned for lagring utover 31 dager.
*   **Anbefaling:** Ved å beholde 90 dager (som foreslått i planen) vil kostnaden øke marginalt (ca. 5-20 kr i måneden).

### 3. Varsling og Regler (Alerts)
*   **Metric Alert Rules:** Ca. 1 kr per regel per måned.
*   **Log Search Alerts:** Ca. 5 kr per regel per måned.
*   **Action Groups (SMS/Voice):** SMS koster ca. 0.30 kr per stykk (E-post og Push er gratis).
*   **Månedlig kostnad:** 20 kr - 100 kr avhengig av antall regler.

### 4. Syntetiske Tester (Availability)
*   **Ping-tester:** Inkludert i Application Insights uten ekstra kostnad.
*   **Multi-step web tests:** Kan koste ekstra, men anbefales ikke som startpunkt.

### Totalt Estimert Månedsbudsjett
| Kategori | Lavt estimat (Lite trafikk) | Høyt estimat (Høy trafikk/debug) | Ved Daily Cap (5GB/dag) |
| :--- | :--- | :--- | :--- |
| Datainnsamling (7 moduler) | 250 kr | 1 200 kr | 4 500 kr |
| Lagring (90 dager) | 20 kr | 100 kr | 360 kr |
| Varsling & Tester | 80 kr | 250 kr | 250 kr |
| **Sum per måned** | **350 kr** | **1 550 kr** | **5 110 kr** |

*Merk: Kostnadene er basert på at alle 7 moduler (portal, FSA, API-er, statistikk og utrapporteringsbank) er instrumentert. Kostnadene vil variere sterkt basert på [Logging Level](#styring-av-loggmengde-og-lognivå-logging-level). Hvis man logger all SQL-tekst og har mye trafikk, vil datamengden øke. Ved å sette en "Daily Cap" på 5GB/dag (ca. 150GB/mnd), vil den maksimale kostnaden ligge rundt 5 000 kr i måneden.*

---

## Styring av Loggmengde og Lognivå (Logging Level)

For å kontrollere kostnadene i Azure Monitor og unngå støy i loggene, er det viktig å styre hvor detaljert informasjonen som sendes skal være. I produksjon er det anbefalt å begrense logging til nivå **Error** eller **Warning**, med unntak av spesifikke forretningsmetrikker.

### 1. .NET Backend (OpenTelemetry)
For .NET-applikasjoner som bruker `Azure.Monitor.OpenTelemetry.AspNetCore`, styres lognivået primært via `appsettings.json`.

For å begrense til kun Error:
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Error",
      "Microsoft": "Warning",
      "Microsoft.Hosting.Lifetime": "Information"
    }
  }
}
```

Du kan også styre dette direkte i koden. Dette er nyttig hvis du vil sikre at OpenTelemetry-eksportøren alltid har et bestemt nivå uavhengig av hva som står i konfigurasjonsfilen.

#### I `Program.cs` (Moderne .NET):
```csharp
builder.Logging.AddFilter<OpenTelemetryLoggerProvider>("", LogLevel.Error);
```

#### I `ConfigureCoreServices.cs` (Ved bruk av Dependency Injection):
Hvis prosjektet (som `bufdirno-fsa`) bruker en utvidelsesmetode for tjenester, legges filteret til i `AddLogging`:

```csharp
services.AddLogging(logging =>
{
    logging.AddFilter<OpenTelemetryLoggerProvider>(null, LogLevel.Error);
});
```

Ved å spesifisere `OpenTelemetryLoggerProvider` sikrer du at filteret kun gjelder for dataene som sendes til Azure Monitor, mens andre logg-destinasjoner (som konsoll) kan beholde sine egne nivåer.

### 2. Node.js og Next.js (Server-side)
For tjenester som kjører på Node.js med OpenTelemetry, kan lognivået styres via miljøvariabler i Azure App Service eller Container Apps:
```bash
OTEL_LOG_LEVEL=error
```

### 3. Frontend (Application Insights SDK)
I nettleseren kan du begrense hva som sendes til Azure ved å konfigurere SDK-en i `AIClient.tsx` eller tilsvarende:
```javascript
const appInsights = new ApplicationInsights({
  config: {
    connectionString: "...",
    loggingLevelConsole: 0, // 0: Off, 1: Only Critical, 2: Error
    disableExceptionTracking: false, // Sikre at feil fortsatt spores
    // Bruk Telemetry Processors for finmasket filtrering
  }
});
```

### 4. Strategi for filtrering
*   **Debug/Verbose:** Skal aldri være aktivert i produksjon.
*   **Information:** Brukes kun for kritiske livssyklus-hendelser.
*   **Warning/Error:** Standard nivå for produksjon for å fange opp avvik og faktiske feil.

### 5. Hvordan unngå støy fra 404-forespørsler (Not Found)
404-feil skyldes ofte roboter, feilstavede URL-er eller manglende ikoner (f.eks. `favicon.ico`). Dette kan fylle opp loggene og øke kostnadene i Azure Monitor.

#### I .NET (OpenTelemetry)
For å filtrere bort 404-forespørsler fra sporing (Traces), kan du konfigurere `AspNetCoreInstrumentation`:

```csharp
services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation(options =>
        {
            options.Filter = (httpContext) =>
            {
                // Eksempel: Ikke logg favicon eller helsesjekker
                var path = httpContext.Request.Path.Value;
                if (path != null && (path.Contains("favicon") || path.Contains("health")))
                {
                    return false;
                }
                return true;
            };
        })
        .UseAzureMonitor(...)
    );
```

For å filtrere basert på statuskode (etter at forespørselen er ferdig), er det mest effektivt å bruke en **Custom Processor** eller filtrere i **Application Insights** via en `ITelemetryProcessor`.

#### I Frontend (Application Insights SDK)
Bruk en `TelemetryInitializer` for å droppe telemetri med 404-statuskode:

```javascript
appInsights.addTelemetryInitializer((telemetry) => {
    if (telemetry.data && telemetry.data.responseCode === 404) {
        return false; // Hindrer at data sendes til Azure
    }
});
```

#### I Node.js (OpenTelemetry)
Bruk filter-funksjonaliteten i `HttpInstrumentation`:

```javascript
new HttpInstrumentation({
  filterRequest: (req) => {
    // Returner false for å ignorere spesifikke stier
    return !req.url.includes('health');
  }
})
```

---

## Harmonering av OpenTelemetry og Serilog

Mange prosjekter i Bufdirno bruker **Serilog** for strukturert logging til fil og konsoll. Når vi introduserer OpenTelemetry for å sende data til Azure Monitor, er det viktig å unngå konflikter og "dobbelt-logging".

### 1. Unngå dobbelt-logging (Viktig!)
Hvis du bruker både `Serilog.Sinks.ApplicationInsights` og `Azure.Monitor.OpenTelemetry.AspNetCore`, vil hver loggmelding bli sendt to ganger til Azure Monitor.

**Anbefalt løsning:**
1.  **Fjern** `Serilog.Sinks.ApplicationInsights` fra prosjektet.
2.  Behold Serilog for lokal logging (Console, File).
3.  La OpenTelemetry håndtere all eksport til Azure Monitor via den innebygde `ILogger`-integrasjonen.

### 2. Slik fungerer de sammen
Når du bruker `.UseSerilog()`, erstatter Serilog standard `LoggerFactory`. Alle kall til `ILogger.LogInformation()` etc. går da gjennom Serilog.

OpenTelemetry sin `OpenTelemetryLoggerProvider` kobler seg på standard .NET logging-pipeline. Det betyr at når Serilog er konfigurert korrekt, vil OpenTelemetry plukke opp de samme loggmeldingene og sende dem til Azure Monitor, komplett med Serilog sine "properties" (strukturert logging).

### 3. Eksempel på konfigurasjon i `Program.cs`

```csharp
// 1. Serilog konfigureres som vanlig for lokal logging
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .WriteTo.Console()
    .WriteTo.File("logs/log.txt")
    .CreateLogger();

builder.Host.UseSerilog();

// 2. OpenTelemetry settes opp for Azure Monitor
builder.Services.AddOpenTelemetry()
    .UseAzureMonitor(options =>
    {
        options.ConnectionString = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];
    });

// 3. Viktig: Sikre at OTEL-filteret er satt hvis du vil begrense AI-logger
// uavhengig av Serilog sin lokale konfigurasjon
builder.Logging.AddFilter<OpenTelemetryLoggerProvider>("", LogLevel.Error);
```

### 4. Fordeler med denne tilnærmingen
- **Enkelhet:** Du trenger ikke en egen Serilog-sink for Azure Monitor.
- **Ytelse:** OpenTelemetry-eksportøren er høytytende og leverandørnøytral.
- **Konsistens:** Samme sporings-ID (Trace ID) brukes både i Serilog-logger og OpenTelemetry-sporing, noe som gjør feilsøking på tvers av tjenester mye enklere.

---

## CORS-feil ved Distributed Tracing

Når man aktiverer Distributed Tracing med Application Insights SDK (frontend) og OpenTelemetry (backend), vil klientsiden automatisk legge til ekstra headere i HTTP-forespørslene for å korrelere spor på tvers av tjenester. Dette kan utløse CORS-feil (Cross-Origin Resource Sharing) hvis backend eller gateway ikke er konfigurert til å tillate disse headerne.

### 1. Hvorfor oppstår feilen?
Nettlesere sender en "preflight"-forespørsel (OPTIONS) når en request inneholder headere som ikke er på standardlisten. Hvis responsen fra serveren ikke eksplisitt tillater disse headerne, vil nettleseren blokkere den faktiske forespørselen.

De vanligste headerne som legges til er:
*   `traceparent` (W3C Trace Context standard)
*   `tracestate` (W3C Trace Context standard)
*   `request-id` (Application Insights legacy standard)
*   `x-ms-request-id`
*   `x-ms-request-root-id`

### 2. Løsning i .NET Backend
I backenden må CORS-policyen oppdateres til å tillate disse headerne. Den enkleste måten er å tillate alle headere:

```csharp
services.AddCors(options =>
{
    options.AddDefaultPolicy(builder =>
    {
        builder.WithOrigins("https://din-frontend-url.no")
               .AllowAnyHeader() // Tillater alle headere, inkludert sporing
               .AllowAnyMethod()
               .AllowCredentials();
    });
});
```

Hvis du vil være mer restriktiv, må du spesifisere headerne:
```csharp
builder.WithHeaders("traceparent", "tracestate", "request-id", "x-ms-request-id", "x-ms-request-root-id", "Content-Type");
```

### 3. Løsning i Next.js (Node.js) Backend

Hvis du bruker Next.js API Routes eller en annen Node.js-backend, må du også tillate sporings-headerne.

#### Alternativ A: Via `next.config.js` (Enklest)
Dette er den enkleste metoden for å sette statiske CORS-headere for alle API-ruter:

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Credentials", value: "true" },
          { key: "Access-Control-Allow-Origin", value: "https://din-frontend-url.no" },
          { key: "Access-Control-Allow-Methods", value: "GET,DELETE,PATCH,POST,PUT,OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, traceparent, tracestate, request-id, x-ms-request-id, x-ms-request-root-id" },
        ]
      }
    ]
  }
}
```

#### Alternativ B: Via `middleware.ts` (Fleksibelt)
Hvis du trenger dynamisk sjekk av Origin eller mer avansert logikk, bruk Middleware:

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Håndter preflight-forespørsler (OPTIONS)
  if (request.method === 'OPTIONS') {
    return new NextResponse(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': 'https://din-frontend-url.no',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, traceparent, tracestate, request-id, x-ms-request-id, x-ms-request-root-id',
        'Access-Control-Max-Age': '86400',
      },
    })
  }

  const response = NextResponse.next()
  response.headers.set('Access-Control-Allow-Origin', 'https://din-frontend-url.no')
  return response
}
```

### 4. Løsning i Azure Application Gateway

Siden løsningen benytter Azure Application Gateway, må du sikre at den er konfigurert til å håndtere eller sende videre disse headerne. Hvis du får CORS-feil på grunn av sporings-headere, er det to hovedmåter å løse det på i Gateway-en.

#### Alternativ A: Rewrite Rules (Anbefalt)
Du kan bruke "Rewrite Rules" i Application Gateway til å automatisk legge til nødvendige CORS-headere for "preflight"-forespørsler (OPTIONS). Dette er spesielt nyttig hvis du ikke vil eller kan endre koden i backenden.

Her er et konkret eksempel på hvordan logikken settes opp. Selv om Azure internt bruker JSON (ARM-maler), er logikken her beskrevet i et strukturert format for oversikt:

**Logikk for Rewrite Rule (Beskrivende eksempel):**
```xml
<!-- Dette er en konseptuell fremstilling av en Rewrite Rule for CORS i App Gateway -->
<RewriteRuleSet name="DistributedTracingCORS">
    <RewriteRule name="AllowTracingHeaders">
        <Conditions>
            <!-- Sjekk om dette er en preflight-forespørsel -->
            <Condition variable="var_request_method" match="OPTIONS" />
        </Conditions>
        <Actions>
            <!-- Legg til de nødvendige headerne for OpenTelemetry/Application Insights -->
            <SetResponseHeader name="Access-Control-Allow-Headers" 
                               value="Content-Type, traceparent, tracestate, request-id, x-ms-request-id, x-ms-request-root-id" />
            <SetResponseHeader name="Access-Control-Allow-Origin" value="{var_http_origin}" />
            <SetResponseHeader name="Access-Control-Allow-Methods" value="GET, POST, PUT, DELETE, OPTIONS" />
            <SetResponseHeader name="Access-Control-Allow-Credentials" value="true" />
            <SetResponseHeader name="Access-Control-Max-Age" value="86400" />
        </Actions>
    </RewriteRule>
</RewriteRuleSet>
```

**Konkret JSON-konfigurasjon (ARM Template):**
Hvis du konfigurerer via "Infrastructure as Code", vil det se slik ut i ARM-malen:

```json
{
  "name": "AllowTracingHeaders",
  "actionSet": {
    "responseHeaderConfigurations": [
      {
        "headerName": "Access-Control-Allow-Headers",
        "headerValue": "Content-Type, traceparent, tracestate, request-id, x-ms-request-id, x-ms-request-root-id"
      },
      {
        "headerName": "Access-Control-Allow-Origin",
        "headerValue": "{var_http_origin}"
      }
    ]
  },
  "conditions": [
    {
      "variable": "var_request_method",
      "pattern": "OPTIONS",
      "ignoreCase": true
    }
  ]
}
```

#### Alternativ B: Konfigurasjon i applikasjonskode
Hvis du ikke ønsker å håndtere CORS i Application Gateway, må du sikre at applikasjonskoden din (f.eks. i .NET eller Next.js) er konfigurert til å tillate sporings-headere. Se de spesifikke avsnittene over for:
- [Løsning i .NET Backend](#2-løsning-i-net-backend)
- [Løsning i Next.js Backend](#3-løsning-i-nextjs-nodejs-backend)

**Viktig:** Hvis du bruker WAF (Web Application Firewall) på Gateway-en, må du sjekke at "Anomaly Scoring" ikke blokkerer forespørslene fordi de inneholder ukjente headere. Du må kanskje legge inn en "Exclusion rule" for de spesifikke sporings-headerne (`traceparent`, `tracestate`, `request-id`).

### 5. Løsning i Frontend (Application Insights SDK)

Hvis du absolutt ikke kan endre backend- eller gateway-konfigurasjonen umiddelbart, kan du midlertidig deaktivere korrelasjonsheaderne i frontend. **Vær oppmerksom på at du da mister Distributed Tracing (sammenhengen mellom frontend- og backend-logger).**

I `appInsights.ts` / `AIClient.tsx`:
```javascript
const appInsights = new ApplicationInsights({
  config: {
    connectionString: "...",
    disableCorsCorrelation: true, // Deaktiverer de ekstra headerne for CORS-kall
    enableCorsCorrelation: false
  }
});
```

### 6. CORS-feil mot 3.-partstjenester (f.eks. Mediaflow)

Når du sender forespørsler til eksterne tjenester som du ikke kontrollerer selv (som Mediaflow, Vimeo, Google Maps), kan du ikke endre deres CORS-policy. Hvis disse tjenestene blokkerer forespørsler på grunn av sporings-headere, må du ekskludere disse domene fra automatisk sporing.

**Løsning:**
Bruk `excludeRequestFromAutoTrackingPatterns` i konfigurasjonen til Application Insights SDK. Dette hindrer at SDK-en legger til `traceparent` og andre headere på forespørsler til de spesifiserte domene.

```javascript
const appInsights = new ApplicationInsights({
  config: {
    connectionString: "...",
    // Ekskluder spesifikke domener fra å få lagt til sporings-headere
    excludeRequestFromAutoTrackingPatterns: [
        /mediaflow\.com/, 
        /mediaflowpro\.com/,
        /vimeo\.com/
    ],
  }
});
```
Dette løser CORS-problemet uten å deaktivere sporing for dine egne backender.
*Merk: Dette anbefales ikke som en permanent løsning, da det reduserer observabiliteten.*

---

## Varslingskonfigurasjon i Azure Monitor

Varsling er den proaktive delen av monitoreringen som sikrer at teamet får beskjed før brukerne merker feil. I Bufdirno-løsningen brukes Azure Monitor Alerts.

### 1. Typer varsler
*   **Metric Alerts:** Brukes for infrastruktur og ytelse (f.eks. CPU > 80%, Responstid > 2s). Disse er raske og reagerer nesten i sanntid.
*   **Log Search Alerts:** Brukes for å overvåke feilrater og forretningslogikk. Disse kjører en KQL-spørring (Kusto Query Language) med et fast intervall (f.eks. hvert 5. minutt).
    - *Eksempel:* Varsle hvis antall unntak (exceptions) > 10 de siste 5 minuttene.
*   **Availability Alerts:** Syntetiske tester (ping-tester) som sjekker om nettstedet svarer fra flere steder i verden.

### 2. Action Groups (Handlingsgrupper)
En Action Group definerer *hvem* som skal varsles og *hvordan*. Det anbefales å dele opp i:
*   **Prio 1 (Kritisk):** Sendes til vakttelefon (SMS/Push) og e-post. Brukes ved nedetid eller totale systemfeil.
*   **Prio 2 (Advarsel):** Sendes kun til e-post. Brukes ved økte feilrater eller ytelsesdegradering som ikke krever umiddelbar handling om natten.
*   **Automation:** Kan trigge en Azure Function eller en Logic App for å forsøke automatisk gjenoppretting (f.eks. restart av en tjeneste).

### 3. Slik setter man opp et nytt varsel
1.  **Scope:** Velg ressursen (f.eks. Application Insights eller Log Analytics Workspace).
2.  **Condition:** Definer logikken.
    - For Log Search: Skriv en KQL-spørring.
    - Velg terskelverdi (Threshold) og tidsvindu (Aggregation granularity).
3.  **Actions:** Velg riktig Action Group basert på alvorlighetsgrad.
    - Her kan du også koble til en [automatisert runbook](./runbook/azure-automation-runbook-setup.md).
4.  **Details:** Gi varselet et beskrivende navn og velg alvorlighetsgrad (Sev 0 til Sev 4).
    - Legg ved lenke til en [manuell runbook](./runbook/runbook-guide.md) i beskrivelsen.

### Beste praksis for Bufdirno
*   **Unngå varslingstretthet:** Ikke varsle på ting som ikke krever handling.
*   **Bruk "Suppress Alerts":** Konfigurer varsler slik at de ikke sender gjentatte meldinger for samme feil i løpet av kort tid.
*   **Koble til Runbooks:** Hvert varsel bør inneholde en lenke til en relevant [runbook](./runbook/runbook-guide.md) slik at den som mottar varselet vet nøyaktig hva de skal gjøre.

---

## Overvåking av Sertifikater og Secrets

For å unngå uforutsett nedetid forårsaket av utløpte sertifikater eller secrets, implementerer Bufdirno automatisert overvåking av Azure Key Vault og eksterne tjenester på tvers av alle moduler.

### 1. Azure Key Vault Overvåking
Key Vault har innebygd støtte for å sende hendelser til **Azure Event Grid** når en secret eller et sertifikat er nær utløpsdato.
*   **Log Analytics:** Alle aksesser og endringer i Key Vault logges til felles Log Analytics Workspace (Diagnostic Settings).
*   **Varsling:** Det settes opp Log Search Alerts som sjekker for hendelser relatert til utløp (Events med ID `SecretNearExpiry` eller `CertificateNearExpiry`).

### 2. Sertifikater (SSL/TLS)
*   **App Service & Container Apps:** Overvåk SSL-sertifikater for alle moduler via Availability Tests i Application Insights.
*   **Virksomhetssertifikater:** Spesielt kritisk for Maskinporten-integrasjon i `utrapporteringsbank` og integrasjoner i `bufdirno-fsa`.

### 3. Modulspesifikk overvåking
Detaljerte oppgaver for overvåking av secrets (som Azure AD Client Secrets, API-nøkler for SendGrid, ROS, Oslo Kommune, og Make) er beskrevet i de individuelle modul-filene:
*   [bufdirno (Hovedportal)](./bufdirno-monitoring.md#fase-7-overvåking-av-sertifikater-og-secrets)
*   [bufdirno-fsa](./bufdirno-fsa-monitoring.md#fase-7-overvåking-av-sertifikater-og-secrets)
*   [familievern-api](./familievern-api-monitoring.md#fase-5-overvåking-av-sertifikater-og-secrets)
*   [fosterhjem-api](./fosterhjem-api-monitoring.md#fase-5-overvåking-av-sertifikater-og-secrets)
*   [newsletter-api](./newsletter-api-monitoring.md#fase-5-overvåking-av-sertifikater-og-secrets)
*   [stat-system](./stat-system-monitoring.md#fase-7-overvåking-av-sertifikater-og-secrets)
*   [Utrapporteringsbank](./utrapporteringsbank-monitoring.md#fase-7-overvåking-av-sertifikater-og-secrets)

### 4. Automatisering
For å skalere overvåkingen av secrets og sertifikater på tvers av alle moduler, bør oppsettet automatiseres ved bruk av Infrastruktur som Kode (IaC) eller Azure Policy. Se [Automatisering av Monitorering](./automatisering-av-monitorering.md) for tekniske detaljer og eksempler.

---

## Spesifikke metrikker og spor (Metrics & Traces)

For å gå fra grunnleggende overvåking ("kjører systemet?") til dyp innsikt ("fungerer forretningen optimalt?"), implementerer Bufdirno en strategi for finspisset modellering av metrikker og spor.

### 1. Kategorisering av data
*   **Tekniske metrikker:** Fokus på kjøretidsmiljøet (f.eks. Node.js event loop delay, SQL-responstider, minnebruk).
*   **Brukeropplevelse (RUM):** Fokus på klient-side ytelse (f.eks. Core Web Vitals, hydration-tid i Next.js).
*   **Forretningsmetrikker:** Fokus på verdi og flyt (f.eks. fullføringsgrad for søknader, suksessrate for nyhetsbrev).

### 2. Strategisk verdi
Ved å kombinere Application Insights SDK (frontend) og OpenTelemetry (backend) oppnår vi:
*   **Sammenhengende feilsøking:** Vi kan følge en "trace" fra en treghet i browseren, gjennom API-er, til den nøyaktige SQL-spørringen som forårsaket den, takket være W3C Trace Context.
*   **Proaktiv optimalisering:** Metrikker som `cache.hit_rate` og `query_complexity` gjør at vi kan optimalisere infrastrukturen før det oppstår flaskehalser.
*   **Forretningsinnsikt:** Ved å logge `customEvents` for kritiske steg i en søknadsprosess, kan vi identifisere hvor brukere faller fra uten å trenge komplekse analyseverktøy.

### 3. Veien videre
Hver modul har sitt eget kapittel for spesifikke metrikker og spor. Disse bør gjennomgås og finspisses i takt med at applikasjonene utvikles:
*   Se Fase 7 i [bufdirno](./bufdirno-monitoring.md), [bufdirno-fsa](./bufdirno-fsa-monitoring.md), [stat-system](./stat-system-monitoring.md) og [Utrapporteringsbank](./utrapporteringsbank-monitoring.md).
*   Se Fase 5 i [familievern-api](./familievern-api-monitoring.md), [fosterhjem-api](./fosterhjem-api-monitoring.md) og [newsletter-api](./newsletter-api-monitoring.md).

---

## Implementeringsstatus
Gå til de spesifikke filene for detaljerte oppgaver.
