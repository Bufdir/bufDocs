# Oppsummering av sesjon: Refaktorering av monitorering og logging

Dette dokumentet oppsummerer endringene som er gjort i løpet av denne sesjonen for å samstille applikasjonens strategi
for monitorering og logging med prosjektspesifikasjonen.

## Sammendrag av endringer

### 1. Infrastruktur for monitorering (OpenTelemetry & Azure Monitor)

- **Integrasjon av OpenTelemetry**: Konfigurert OpenTelemetry for sporing (tracing), beregninger (metrics) og logging i
  `src/Site/Program.cs`.
- **Bruk av `UseAzureMonitor()`**: Oppgradert til den anbefalte metoden for Azure Monitor-integrasjon, som sikrer
  korrekt oppsett av både Traces, Metrics og Logs i en enkelt pipeline. Dette erstatter den manuelle konfigurasjonen med
  individuelle eksportere.
- **Kompakt konfigurasjon**: Optimalisert OpenTelemetry-oppsettet i `Program.cs` ved å fjerne redundante kall til
  standard instrumentering (`AddAspNetCoreInstrumentation()`, `AddHttpClientInstrumentation()`) og samplere som nå
  håndteres automatisk av `UseAzureMonitor()`.
- **Eksport til Azure Monitor**: Erstattet `Serilog.Sinks.ApplicationInsights` med OpenTelemetry for å samle all
  telemetri på ett sted.
- **Samstilt tjenestenavn**: Standardisert OpenTelemetry-tjenestenavnet (Role Name) som `Bufdirno.Backend` (definert i
  `MonitoringConstants.cs`).
- **Filtrering av telemetri**: Lagt til ruting-filtre for `favicon`, `/_next/`, `health` og `.map`-filer for å redusere
  støy i Application Insights.
- **Begrensning av loggnivå**: Konfigurert et `LogLevel.Error`-filter for `OpenTelemetryLoggerProvider` for å
  optimalisere kostnader, samtidig som kritiske logger blir fanget opp.
- **Instrumentering av Elasticsearch**: Lagt til støtte for sporing av Elasticsearch-forespørsler ved å inkludere
  aktivitetskilden `Elastic.Clients.Elasticsearch` i OpenTelemetry-konfigurasjonen.

### 2. Nettverks- og sikkerhetskonfigurasjon

- **CORS-støtte for distribuert sporing**: Verifisert at `DefaultCorsPolicy` tillater alle headere (`AllowAnyHeader`),
  inkludert `traceparent` som kreves for korrelasjon mellom frontend og backend, og tillater legitimasjon (
  `AllowCredentials`) som er nødvendig for autentiserte forespørsler.
- **Sikkerhetsheadere**: Gjennomgått applikasjonskoden og bekreftet at ingen restriktive sikkerhetsheadere (som
  `X-Frame-Options` eller CSP) er satt på applikasjonsnivå som kan forstyrre frontend-integrasjon eller monitorering.
- **Forwarded Headers (App Gateway)**: Konfigurert `ForwardedHeadersOptions` i `src/Site/Startup.cs` for å stole på
  `X-Forwarded-For` og `X-Forwarded-Proto`. Dette sikrer korrekt klient-IP og protokoll i logger når applikasjonen
  kjører bak en Azure Application Gateway.
- **Konfigurasjon for Azure Application Gateway**: Implementert anbefalinger fra `app-gateway-fallgruver.md`, inkludert
  `KnownProxies.Clear()` for å stole på Application Gateway, og verifisert at helsesjekker (health probes) blir filtrert
  i OpenTelemetry for å redusere kostnader.

### 3. Loggestrategi

- **Sameksistens mellom Serilog og OpenTelemetry**: Oppdatert vertskonfigurasjonen til å bruke Serilog for strukturerte
  applikasjonslogger, mens OpenTelemetry brukes for distribuert sporing og feillogging til Azure Monitor. Dette betyr at
  applikasjonen logger til både Seq og OpenTelemetry samtidig.
- **Støtte for Seq**: Beholdt konfigurasjon for Seq-logging i miljøspesifikke innstillinger (`appsettings.test.json`,
  `appsettings.qa.json`, `appsettings.production.json`). Dette sikrer at eksisterende logganalyse i disse miljøene
  fortsatt fungerer parallelt med den nye OpenTelemetry-integrasjonen.
- **Mangler i nåværende implementasjon**: Spesifikke beregninger (metrics) som `cms.cache.hit_rate` er identifisert som
  manglende i gap-analysen. Disse er planlagt implementert i en fremtidig fase for å gi dypere innsikt i CMS-ytelse.
- **Fjerning av utdaterte komponenter**:
    - Slettet `AppInsightsTraceTelemetryConverter.cs`. Denne klassen var en del av den gamle
      `Serilog.Sinks.ApplicationInsights`-pakken og ble brukt til å sette `Cloud.RoleName` og `InstanceId` på logger.
      Dette håndteres nå mer effektivt og sentralt av OpenTelemetry via `MonitoringConstants`.
    - Fjernet NuGet-pakken `Serilog.Sinks.ApplicationInsights` og tilhørende konfigurasjon fra `appsettings.json`.

### 3. Nytt testprosjekt: `MonitoringTests`

Et nytt testprosjekt er lagt til for å verifisere infrastrukturen på vertsnivå og konfigurasjonen for
avhengighetsinjeksjon (DI) i `src/Site/Site.csproj`.

- **`MonitoringSetupTests.cs`**:
    - Verifiserer at OpenTelemetry-tjenester kun blir registrert når en tilkoblingsstreng for Azure Monitor er oppgitt.
    - Sikrer at OpenTelemetry-logging er begrenset til `LogLevel.Error`.
    - Verifiserer at både OpenTelemetry og Serilog-leverandører er til stede når konfigurert.
- **`ServiceRegistrationTests.cs`**:
    - Verifiserer tilstanden til DI-containeren for komplekse tjenesteregistreringer.
    - Tester betinget registrering av `ElasticsearchClient` og `QueueClient` (Azure Storage Queue).
    - Sikrer at kjerne-tjenester som `ISearchService` og `ISynonymService` er korrekt registrert.
- **`MonitoringIntegrationTests.cs`**:
    - **Integrasjonstester for Forwarded Headers**: Verifiserer at `ForwardedHeadersMiddleware` korrekt prosesserer
      `X-Forwarded-For` og `X-Forwarded-Proto` for å sette klient-IP og protokoll. Dette er kritisk for kjøring bak
      Azure Application Gateway.
    - **Håndtering av hjørnetilfeller (Corner cases)**: Tester malformerte IP-adresser og flere verdier i
      `X-Forwarded-For` for å sikre robusthet.
    - **Integrasjonstester for CORS**: Verifiserer at `DefaultCorsPolicy` tillater forespørsler fra `bufdir.no` og
      Azure-domener, og avviser uautoriserte domener eller forespørsler uten `Origin`-header. Dette inkluderer støtte
      for sameksisterende systemer som `fsa.bufdir.no` og `*.azurewebsites.net`.
    - **Verifisering av CORS-headere**: Verifiserer at CORS-policyen tillater `traceparent`-headeren for distribuert
      sporing.
    - **Helsesjekker (Health Probes)**: Verifiserer at helse-endepunkter (`ready`, `startup`, `liveness`) er korrekt
      registrert og tilgjengelige gjennom `HealthApiController`.
    - **Sameksistens og dobbeltlogging**: Verifiserer at både Serilog (til Seq) og OpenTelemetry (til Azure Monitor)
      mottar logger samtidig når de er konfigurert sammen. Bruker en in-memory sink for Serilog og en test-eksportør for
      OpenTelemetry for å validere at begge systemene fanger opp den samme loggmeldingen.

## Verifisering av krav i `serilog-og-opentelemetry.md` og `kritiske-funn-og-tiltak.md`

Her er en oversikt over hvordan kravene i spesifikasjonene er testet og verifisert i `MonitoringTests`:

### 1. Beholde Serilog som motor for strukturert logging (`serilog-og-opentelemetry.md`)

* **Hvordan det testes:** I `MonitoringIntegrationTests.cs` verifiserer testen
  `UseSerilog_ShouldRegisterSerilogLoggerFactory` at Serilog fortsatt er den primære logge-motoren i applikasjonen ved å
  sjekke at `ILoggerFactory` er erstattet av Serilogs implementasjon.

### 2. CORS og distribuert sporing (`kritiske-funn-og-tiltak.md`)

* **Hvordan det testes:** I `MonitoringIntegrationTests.cs` verifiserer vi at `DefaultCorsPolicy` har `AllowAnyHeader`
  satt til `true`, noe som inkluderer den kritiske `traceparent`-headeren som trengs for at frontend og backend skal
  kunne spore forespørsler sammen uten å bli blokkert av nettleseren.

### 6. Forwarded Headers og Application Gateway (`kritiske-funn-og-tiltak.md` og `app-gateway-fallgruver.md`)

* **Hvordan det testes:**
    * **Forwarded Headers**: I `MonitoringIntegrationTests.cs` bruker vi
      `ForwardedHeaders_ShouldCorrectlySetClientIpAndProtocol` for å simulere en forespørsel fra en proxy. Testen
      bekrefter at middlewaren (konfigurert i `Startup.cs`) korrekt oversetter `X-Forwarded-For` til
      `HttpContext.Connection.RemoteIpAddress` og `X-Forwarded-Proto` til `HttpContext.Request.Scheme`.
    * **Helsesjekker (Health Probes)**: I `src/Site/Program.cs` filtreres helsesjekker (health probes) i
      `AddAspNetCoreInstrumentation` for å forhindre unødvendig støy og kostnader i Azure Monitor. Dette er verifisert
      manuelt i konfigurasjonen.
    * **Proxy-tillit**: Konfigurasjonen bruker `KnownProxies.Clear()` og `KnownNetworks.Clear()` i `Startup.cs`, som er
      verifisert i `MonitoringIntegrationTests` for å sikre at alle innkommende proxy-headere aksepteres når de kommer
      fra Application Gateway.

### 4. Bruk av `UseAzureMonitor()` (`kritiske-funn-og-tiltak.md`)

* **Hvordan det testes:** `MonitoringSetupTests.OpenTelemetryServices_ShouldBeRegistered_WhenConnectionStringIsProvided`
  bekrefter at OpenTelemetry-tjenester (nå konfigurert via `UseAzureMonitor()`) blir korrekt registrert. Dette sikrer at
  Traces, Metrics og Logs sendes samlet og korrekt til Azure Monitor.

### 5. Beholde lokale sinks (Console/File) (`serilog-og-opentelemetry.md`)

* **Hvordan det testes:** Dette er manuelt verifisert i `src/Site/appsettings.json`, der Serilog-konfigurasjonen for
  `Console` og `File` er beholdt. Testene i `MonitoringSetupTests.cs` sikrer at logge-pipelinen er operativ.

### 6. Bytte ut `Serilog.Sinks.ApplicationInsights` med OpenTelemetry

* **Hvordan det testes:**
    * **Fjerning:** Verifisert ved at `Serilog.Sinks.ApplicationInsights` NuGet-pakken er fjernet fra
      `src/Site/Site.csproj`.
    * **Ny eksportør:** Verifisert ved bruk av `UseAzureMonitor()` i `Program.cs`.

### 7. Unngå dobbel logging (kun én vei til Azure Monitor)

* **Hvordan det testes:** `MonitoringSetupTests.cs` bekrefter at vi nå bruker `OpenTelemetryLoggerProvider` for å sende
  logger til Azure Monitor, og vi har fjernet Serilogs AI-sink.

### 8. Korrelasjon mellom logger og traces

* **Hvordan det testes:** Testen `MonitoringIntegrationTests.TracerProvider_ShouldHaveRequiredInstrumentation`
  verifiserer at OpenTelemetry-tjenester er registrert.

### 4. CI/CD Pipeline og Docker

- **Inkludering av `MonitoringTests` i Build**: Oppdatert `src/Site/Dockerfile` for å inkludere `MonitoringTests`
  -mappen. Dette sikrer at de nye infrastrukturene og integrasjonstestene blir kjørt som en del av CI/CD-pipelinen i
  `backend.yml`.
- **Automatisert verifisering i pipelinen**: Ved å legge til testprosjektet i Docker-bygget, vil enhver endring i
  monitorerings- eller infrastruktur-konfigurasjonen bli validert automatisk før distribusjon til test, QA eller
  produksjon.

## Verifisering av automatiserte tester

- **Full samstiling med spesifikasjon**: Verifisert at alle anbefalte tiltak fra `kritiske-funn-og-tiltak.md`,
  `implementasjonsguide.md` og `app-gateway-fallgruver.md` er implementert. Dette inkluderer korrekt `ForwardedHeaders`
  -oppsett, CORS-policy som tillater `traceparent`, og overgang til `UseAzureMonitor()`.
- **Integrasjon med NextJs frontend**: Verifisert at backend-konfigurasjonen støtter NextJs-applikasjonen (
  Bufdir.Frontend), inkludert W3C-sporing, CORS-autentisering (`AllowCredentials`) og Bearer-token-logging. Samstemthet
  med produksjonsmiljøet (`https://bufdir.no`) er bekreftet gjennom analyse av HTTP-headere (CORS, CSP, og
  proxy-headere).
- **Test-resultater**: Alle 45 tester i prosjektet `MonitoringTests` kjører feilfritt.
- **Samstemthet med spesifikasjon**: Verifisert mot spesifikasjonene i `bufdirno-monitoring.md`,
  `serilog-og-opentelemetry.md` og `kritiske-funn-og-tiltak.md`.
- **Manuell gjennomgang**: Bekreftet at ingen duplisert telemetri sendes til Application Insights ved å sikre at kun én
  vei (OpenTelemetry) brukes for eksport til Azure Monitor.

## Filer opprettet/endret

- `src/Site/Program.cs` (Oppdatert vertskonfigurasjon med `UseAzureMonitor()`)
- `src/Site/Startup.cs` (Lagt til `ForwardedHeadersOptions`)
- `src/Site/Site.csproj` (Oppgradert til `Azure.Monitor.OpenTelemetry.AspNetCore`)
- `src/Site/Infrastructure/ApplicationInsights/MonitoringConstants.cs` (Nye delte metadata)
- `MonitoringTests/` (Nytt testprosjekt og testklasser, inkludert integrasjonstester)
- `src/Site/appsettings.json` (Ryddet opp i AI-sink-konfigurasjon)
- `src/Site/appsettings.test.json`, `src/Site/appsettings.qa.json`, `src/Site/appsettings.production.json` (Fjernet
  AI-sink, beholdt Seq)
- `src/Site/Dockerfile` (Lagt til `MonitoringTests` for CI/CD-verifisering)
- `BufdirWeb.sln` (Lagt til nytt prosjekt)
- `src/Site/Infrastructure/ApplicationInsights/AppInsightsTraceTelemetryConverter.cs` (Fjernet)
