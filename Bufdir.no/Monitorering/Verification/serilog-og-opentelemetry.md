# Serilog og OpenTelemetry i Bufdirno

Dette dokumentet beskriver hvordan Serilog skal integreres med den nye OpenTelemetry-baserte monitoreringsløsningen, samt hvilke prosjekter som i dag bruker legacy-løsninger som må migreres.

## Oppsummering: Behold Serilog, men bytt eksportør
Det korte svaret er: **Ja, vi skal beholde Serilog.** 

Serilog er utmerket for strukturert logging til lokale mål (Console, File) og Seq. Men når vi flytter telemetri til Azure Monitor via OpenTelemetry, må vi endre hvordan Serilog sender data til skyen.

---

## Hva skal gjøres? (Anbefalt løsning)

For alle .NET-prosjekter som går over til den nye standarden, skal følgende gjøres:

1.  **Fjern** NuGet-pakken `Serilog.Sinks.ApplicationInsights`.
2.  **Behold** Serilog for lokal logging (Console, File, Seq).
3.  **Bruk** `Azure.Monitor.OpenTelemetry.AspNetCore` for å sende både logger, spor (traces) og metrikker til Azure Monitor.

### Eksempel på konfigurasjon i `Program.cs`

```csharp
// 1. Konfigurer Serilog som vanlig for lokale sinks
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.File("logs/log.txt", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog();

// 2. Konfigurer OpenTelemetry for Azure Monitor
// OpenTelemetry vil automatisk plukke opp logger fra Serilog via ILogger-integrasjonen.
builder.Services.AddOpenTelemetry()
    .UseAzureMonitor(options =>
    {
        options.ConnectionString = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];
    });
```

---

## Spesifikke prosjekter som må oppdateres

Følgende prosjekter bruker i dag `Serilog.Sinks.ApplicationInsights` (legacy) og bør migreres til den nye standarden:

| Prosjekt | Fil for konfigurasjon | Merknad |
| :--- | :--- | :--- |
| **Bufdirno (Main Portal)** | `bufdirno/src/Site/Program.cs` | Fjerner manuell tilordning til `Serilog:WriteTo:ApplicationInsightsSink`. |
| **FSA Backend** | `bufdirno-fsa/FSA.Backend.Web/Program.cs` | Bytt ut `AddAzureMonitorTraceExporter` i `ConfigureCoreServices.cs` med `UseAzureMonitor()`. |
| **Newsletter API** | `bufdirno-newsletter-api/src/Bufdir.Newsletter.API/Program.cs` | Fjerner Serilog-sinkingen og bruk OTel i stedet. |
| **Fosterhjem API** | `bufdirno-fosterhjem-api/Api/Program.cs` | Fjerner Serilog-sinkingen. |
| **Familievern API** | `bufdirno-familievern-api/Bufdir.FamilievernApi/Familievern.Api/Program.cs` | Fjerner Serilog-sinkingen. |
| **Statistikk Backend** | `stat-backend/BufdirStatisticsDataAPI/Program.cs` | Bruker både `WriteTo.ApplicationInsights` og legacy SDK i `Startup.cs`. Begge må fjernes. |

### Hvor finner man koden?

I de fleste prosjektene (Bufdirno, Newsletter, Fosterhjem, Familievern) ser den nåværende legacy-koden i `Program.cs` omtrent slik ut:

```csharp
// GAMMEL KODE - MÅ FJERNES
context.Configuration["Serilog:WriteTo:ApplicationInsightsSink:Args:connectionString"] = 
    context.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];
```

I **FSA Backend** (`ConfigureCoreServices.cs`) ser nåværende setup slik ut:

```csharp
// GAMMEL OTel-KODE - Bør forenkles til UseAzureMonitor()
services.AddOpenTelemetry()
    .WithTracing(tracing => {
        tracing.AddAzureMonitorTraceExporter(opt => { ... });
    });
```

I **Statistikk Backend** brukes en eldre metode i `Program.cs`:

```csharp
// GAMMEL KODE - MÅ FJERNES
.WriteTo.ApplicationInsights(TelemetryConverter.Traces, ...)
```

---

## Hvorfor skal vi gjøre det slik?

### 1. Unngå dobbelt-logging (Kritisk!)
Hvis du beholder `Serilog.Sinks.ApplicationInsights` samtidig som du aktiverer OpenTelemetry, vil hver eneste logglinje bli sendt **to ganger** til Azure Monitor:
- Én gang via Serilog-sinkingen.
- Én gang via OpenTelemetry sin automatiske `ILogger`-instrumentering.

Dette fører til unødvendig støy i loggene og doble kostnader for datalagring.

### 2. Full støtte for strukturert logging
En vanlig misforståelse er at man mister Serilog-egenskaper (properties) hvis man ikke bruker AI-sinken. Dette stemmer ikke. OpenTelemetry i .NET er bygget for å støtte `ILogger` fullt ut. Siden Serilog fungerer som backend for `ILogger`, vil alle dine "destructured" objekter og properties bli fanget opp av OpenTelemetry og lagt i `customDimensions`-feltet i Application Insights.

### 3. Perfekt korrelasjon (Distributed Tracing)
Ved å la OpenTelemetry håndtere loggeksporten, sikrer vi at `Trace ID` and `Span ID` alltid er synkronisert mellom logglinjer og HTTP-forespørsler. Dette gjør det mulig å se nøyaktig hvilke logger som tilhører en spesifikk forespørsel i Application Insights "End-to-end transaction details"-visning.

### 4. Fremtidssikkert og ytelsesorientert
`Azure.Monitor.OpenTelemetry.AspNetCore` er Microsofts anbefalte SDK for .NET 8 og nyere. Den er mer effektiv enn den eldre Application Insights SDK-en og følger åpne industristandarder.

---

## Konkrete funn i dagens kodebase

For å svare på "hvilket prosjekt og hvor i koden", her er en oversikt over faktiske funn som bør utbedres i henhold til denne guiden.

### 1. Manglende `UseForwardedHeaders()` (AppGW-støtte)
Dette er kritisk for korrekt logging av klient-IP og protokoll (https) bak Application Gateway.
*   **Status:** Finnes i `bufdirno/src/Site/Startup.cs` (linje 389), men **mangler** i:
    - `bufdirno-fsa/FSA.Backend.Web/Configuration/ConfigureWebApp.cs`
    - `bufdirno-newsletter-api/src/Bufdir.Newsletter.API/Program.cs`
    - `bufdirno-fosterhjem-api/Api/Program.cs`
    - `bufdirno-familievern-api/Bufdir.FamilievernApi/Familievern.Api/Program.cs`
*   **Tiltak:** Legg til `app.UseForwardedHeaders()` før `app.UseHttpsRedirection()` i disse filene.

### 2. Redundant `ActivityEnricher`
*   **Prosjekt:** **FSA Backend**
*   **Fil:** `bufdirno-fsa/FSA.Backend.Web/Program.cs` (linje 25) og `bufdirno-fsa/FSA.Backend.Web/Configuration/ActivityEnricher.cs`.
*   **Problem:** Denne enricheren legger manuelt til `TraceId` og `SpanId` på Serilog-logger. OpenTelemetry gjør dette automatisk nå.
*   **Tiltak:** Fjern `.Enrich.With(new ActivityEnricher())` og slett selve klassen.

### 3. Varierende filtrering av Health Probes
Noen prosjekter har filtrering, andre ikke. Vi bør standardisere dette for å redusere støy og kostnad.
*   **Newsletter API:** Har filter i `Program.cs` (linje 59), men bruker `path.Contains("health")`.
*   **Fosterhjem API:** Har filter i `Program.cs` (linje 161).
*   **Familievern API:** **Mangler filter** helt i `Program.cs` (linje 112).
*   **Tiltak:** Standardiser til et filter som fanger opp alle helsesjekker (f.eks. ved å sjekke om stien starter med `/health`).

### 4. Legacy Serilog Sink (Application Insights)
Nesten alle prosjekter har denne koden som nå bør fjernes etter overgang til OpenTelemetry:
*   **Sted:** `Program.cs` i de fleste API-er.
*   **Kode:** 
    ```csharp
    context.Configuration["Serilog:WriteTo:ApplicationInsightsSink:Args:connectionString"] = ...
    ```
*   **Tiltak:** Fjern denne linjen og fjern `Serilog.Sinks.ApplicationInsights` fra `.csproj`.

---

## Sjekkliste for migrering

- [ ] Er `Serilog.Sinks.ApplicationInsights` fjernet fra `.csproj`?
- [ ] Er `.WriteTo.ApplicationInsights(...)` fjernet fra Serilog-oppsettet?
- [ ] Er `builder.Services.AddOpenTelemetry().UseAzureMonitor()` lagt til?
- [ ] Er `APPLICATIONINSIGHTS_CONNECTION_STRING` konfigurert korrekt i miljøet?

---

## Andre potensielle problemer ved integrasjon

Utover dobbelt-logging er det flere tekniske detaljer som kan skape utfordringer eller redundans når Serilog og OpenTelemetry (OTel) brukes sammen.

### 1. Redundante Request-logger
Mange prosjekter bruker `app.UseSerilogRequestLogging()`. Dette genererer en logglinje per HTTP-forespørsel.
*   **Problem:** OpenTelemetry sin standard-instrumentering sender allerede en "Request Trace" til Azure Monitor med nøyaktig samme informasjon (URL, statuskode, varighet).
*   **Anbefaling:** Vurder om Serilog-request-loggingen er nødvendig i Azure Monitor. Hvis man beholder den, vil man se både en "Request" og en "Log" for hver forespørsel. Dette øker datamengden.

### 2. Overflødige "ActivityEnrichers"
Noen prosjekter (f.eks. **FSA Backend**) har en egendefinert `ActivityEnricher` som legger til `TraceId` og `SpanId` manuelt på Serilog-logger.
*   **Problem:** OpenTelemetry sin `ILogger`-integrasjon gjør dette helt automatisk og på en standardisert måte.
*   **Anbefaling:** Fjern egendefinerte enrichers som henter data fra `Activity.Current` for å unngå duplikate felt i `customDimensions`.

### 3. Startup/Bootstrap-logging
Prosjektene bruker `CreateBootstrapLogger()` for å fange opp feil under oppstart.
*   **Problem:** OpenTelemetry initialiseres ofte litt ut i `Program.cs`. Hvis applikasjonen krasjer *før* `AddOpenTelemetry()` eller før eksportøren har startet, vil ikke feilen nå Azure Monitor. Den vil bare finnes i lokale logger (Console/File).
*   **Tiltak:** Vær klar over at Azure Monitor ikke fanger opp alt i de første millisekundene av oppstarten. Behold alltid Console-logging for debugging i Azure Portal (Log Stream).

### 4. Correlation ID vs Trace ID
Bufdir bruker i dag headeren `x-bufdirno-correlation-id`.
*   **Problem:** OpenTelemetry bruker standarden `traceparent` for å korrelere på tvers av tjenester.
*   **Anbefaling:** Fortsett gjerne å logge `CorrelationId` for bakoverkompatibilitet, men bruk OTel sin `Trace ID` som primærnøkkel for søk i Application Insights ("End-to-end transaction details").

### 5. Ytelse og Synkone Sinks
Standard Serilog-sinking til fil (`WriteTo.File`) kan være synkron og i verste fall blokkere tråder under høy belastning.
*   **Anbefaling:** Bruk `Serilog.Sinks.Async` hvis man logger store mengder data til fil eller konsoll samtidig som man kjører OpenTelemetry.

### 6. Dobbel Exception-rapportering
Hvis man har konfigurert OTel med `.AddAspNetCoreInstrumentation(o => o.RecordException = true)`, vil unntak bli lagt ved tracen. Samtidig vil Serilog logge unntaket som en Error-log.
*   **Resultat:** I Application Insights vil du se unntaket under både "Failures" (som del av requesten) og "Logs" (som en separat oppføring). Dette er normalt sett ønskelig for synlighet, men kan oppleves som "støy".

### 7. Navngivning av attributter (Enrichers vs. Resources)
Standard Serilog-enrichers (f.eks. `WithMachineName`, `WithEnvironmentName`) legger til felt som `MachineName` og `EnvironmentName` i `customDimensions`.
*   **Problem:** OpenTelemetry har sine egne standardiserte felt for dette (`host.name`, `deployment.environment`).
*   **Anbefaling:** For å unngå duplikate data i Azure Monitor, kan man gradvis fase ut generiske Serilog-enrichers og heller stole på OpenTelemetry sine Resource-attributter.

---

## Azure Application Gateway (AppGW) Spesifikke Problemer

Når applikasjonen kjører bak en Azure Application Gateway, er det noen spesifikke utfordringer som kan oppstå ved overgang til OpenTelemetry og ny monitorering.

### 1. Manglende `UseForwardedHeaders()`
Dette er den vanligste feilkilden i Azure-miljøer med AppGW. 
*   **Problem:** AppGW fungerer som en reverse proxy og terminerer SSL. Uten riktig konfigurasjon vil applikasjonen tro at alle forespørsler kommer fra AppGW sin interne IP-adresse, og at de skjer over HTTP (ikke HTTPS).
*   **Konsekvens for monitorering:** 
    - Serilog-logger vil vise feil `ClientIP`.
    - OpenTelemetry vil logge `http.url` som `http://...` i stedet for `https://...`.
    - Man kan oppleve "Redirect Loops" hvis applikasjonen prøver å tvinge HTTPS-omdirigering uten å vite at den allerede er bak en SSL-terminator.
*   **Løsning:** Sørg for at `app.UseForwardedHeaders()` er konfigurert i `Program.cs`/`Startup.cs` og at den stoler på AppGW sine subnett.

### 2. Støy fra Health Probes
AppGW sender jevnlige "Health Probes" for å sjekke om applikasjonen lever. 
*   **Problem:** Disse forespørslene (f.eks. til `/` eller `/health`) genererer en enorm mengde logger og traces i Azure Monitor.
*   **Løsning:** Bruk et filter i OpenTelemetry-konfigurasjonen for å ignorere disse:
    ```csharp
    .AddAspNetCoreInstrumentation(options =>
    {
        options.Filter = (httpContext) => 
        {
            // Ignorer forespørsler fra AppGW Health Probes
            return !httpContext.Request.Path.StartsWithSegments("/health");
        };
    })
    ```

### 3. W3C Trace Context (traceparent)
OpenTelemetry bruker W3C-standarden for korrelering. 
*   **Problem:** Hvis AppGW ikke er konfigurert til å støtte W3C (eller hvis den overskriver headere), kan man miste korreleringen mellom Gateway-logger og applikasjonslogger.
*   **Anbefaling:** Sørg for at "Diagnostic Settings" på Application Gateway er satt opp til å sende data til samme Log Analytics-workspace som applikasjonen, og at W3C-støtte er aktivert (hvis tilgjengelig i din versjon/region).

### 4. SSL-offloading og Telemetri-URL-er
Hvis SSL termineres i AppGW, vil OpenTelemetry ofte logge `http.scheme` som `http`.
*   **Problem:** Dette kan føre til forvirring i Application Insights når man analyserer trafikkmønstre.
*   **Løsning:** Igjen, `UseForwardedHeaders()` løser dette ved å fortelle .NET at den opprinnelige protokollen var `https`.
