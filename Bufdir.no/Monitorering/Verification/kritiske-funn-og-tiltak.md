# Vurdert Sannsynlig Årsak til Produksjonsstopp (FSA)

Etter en grundig gjennomgang av koden i `bufdirno-fsa` (både frontend og backend), er det identifisert én hovedårsak som mest sannsynlig har ført til produksjonsstopp, samt flere andre kritiske mangler som bør utbedres umiddelbart.

---

### 🚨 1. Hovedårsak: CORS-blokkering av applikasjonen (Sannsynlig kilde til funksjonsstopp)
Dette er den eneste endringen som alene kan stoppe all funksjonalitet for brukerne ("produksjonsstopp").

*   **Hva skjedde?**
    I `bufdirno-fsa/FSA.Frontend.React/src/monitoring/appInsights.ts` er overvåking konfigurert med:
    ```typescript
    enableCorsCorrelation: true,
    distributedTracingMode: DistributedTracingModes.W3C,
    ```
    Dette betyr at frontenden legger til en HTTP-header som heter `traceparent` på alle kall til backenden for å kunne spore en forespørsel på tvers av systemene.

*   **Hvorfor stoppet det?**
    I backenden (`bufdirno-fsa/FSA.Backend.Web/Configuration/ConfigureCoreServices.cs`) finnes det **ingen** `AddCors`-konfigurasjon som tillater denne spesifikke headeren. Selv om `app.UseCors()` kalles i `ConfigureWebApp.cs`, vil nettleseren (Chrome/Edge/Safari) blokkere alle API-kall fordi backenden ikke eksplisitt sier "ja, jeg godtar `traceparent`-headeren".

*   **Konsekvens:** Alle knapper som sender data, eller sider som henter data fra backenden, slutter å fungere. Brukeren ser bare feilmeldinger eller at ingenting skjer.

---

### ⚠️ 2. Kritisk mangel: "Blind" backend (FSA)
Selv om backenden sender *Traces* (sporingsdata), mangler den helt *Metrics* (ytelsesdata) og *Logs* (feilmeldinger/logger) i OpenTelemetry-oppsettet.

*   **Hvorfor er dette kritisk?**
    I `ConfigureCoreServices.cs` er det kun `.WithTracing()` som er satt opp manuelt. Hvis det oppstår en server feil (500-feil) eller ytelsesproblemer, vil du ikke se loggmeldingene eller ressursbruken i Azure Monitor/Application Insights under den nye strategien. Du mister dermed evnen til å feilsøke effektivt i produksjon.

---

### ⚠️ 3. Kritisk risiko: Ustabil/Manuell konfigurasjon
Både `bufdirno` (Site) og `bufdirno-fsa` bruker nå en manuell og utdatert måte å konfigurere OpenTelemetry på (ved bruk av `AddAzureMonitorTraceExporter` i stedet for `UseAzureMonitor()`).

*   **Risiko:** Dette øker sjansen for feilkonfigurering, manglende korrelasjon mellom logger og traces, og gjør det vanskeligere å vedlikeholde. Den anbefalte metoden fra Microsoft (`UseAzureMonitor()`) håndterer alt dette automatisk og sikrer at både Traces, Metrics og Logs blir sendt korrekt.

---

### ⚠️ 4. Application Gateway Fallgruver (Forwarded Headers)
Backend er ikke konfigurert til å stole på `X-Forwarded-For` eller `X-Forwarded-Proto` fra Azure Application Gateway.

*   **Konsekvens:** Feil klient-IP i logger (viser IP-en til Application Gateway i stedet for brukeren), og potensielle problemer med OIDC/HTTPS-redirects.
*   **Se også:** [Fallgruver ved bruk av Azure Application Gateway og Monitorering](app-gateway-fallgruver.md)

---

### 5. Konkrete Kodeendringer per Prosjekt

For fullstendige kodesnutter og filreferanser, se [Implementasjonsguide: Fix av Monitorering og Infrastruktur](implementasjonsguide.md).

#### FSA Backend
*   Legg til `AddCors` med støtte for `traceparent`.
*   Aktiver `UseForwardedHeaders()`.
*   Oppgrader til `UseAzureMonitor()`.

#### Bufdirno Site
*   Fjern Serilog Application Insights Sink (unngå dobbel logging).
*   Oppgrader til `UseAzureMonitor()`.
*   Konfigurer `ForwardedHeadersOptions`.

---

### 6. Kombinere Serilog og OpenTelemetry
Vi ønsker å beholde Serilog som logging-motor for strukturert logging og lokal logging (Console/File), men la OpenTelemetry håndtere eksporten til Azure Monitor.

*   **Tiltak:** Fjern `Serilog.Sinks.ApplicationInsights` fra `appsettings.json` og `Program.cs`.
*   **Resultat:** Serilog sender logger til standard ILogger-pipeline, som OpenTelemetry plukker opp og sender til Azure Monitor. Ingen dobbel logging, men full funksjonalitet.
*   **Se også:** [Serilog og OpenTelemetry i Bufdir.no](serilog-og-opentelemetry.md)
