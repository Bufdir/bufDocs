# Oppsummering: Monitorering og Infrastruktur (FSA og Bufdirno)

Dette dokumentet gir en overordnet oversikt over de viktigste funnene og anbefalte tiltakene for å sikre stabil drift og god overvåking av Bufdir.no og FSA etter overgangen til ny monitoreringsstrategi.

---

### Hovedutfordringer

1.  **Vurdert Sannsynlig Årsak til Produksjonsstopp (FSA):**
    Manglende CORS-konfigurasjon i backenden blokkerte frontend-kall som inkluderte den nye `traceparent`-headeren (W3C standard for distribuert sporing).
2.  **Mangelfull overvåking i FSA Backend:**
    Dagens oppsett i FSA sender kun sporingsdata (Traces), men mangler feillogger (Logs) og ytelsesdata (Metrics) i OpenTelemetry.
3.  **Infrastruktur-utfordringer (Application Gateway):**
    Backend er ikke konfigurert til å stole på `Forwarded Headers` fra Application Gateway, noe som fører til feilrapportering av IP-adresser og potensielle HTTPS-problemer.

---

### Strategiske Anbefalinger

*   **Standardiser på `UseAzureMonitor()`:**
    Bytt fra manuelt OpenTelemetry-oppsett til Microsofts anbefalte pakke. Dette sikrer stabil korrelasjon mellom logger, traces og metrics, og er enklere å vedlikeholde.
*   **Behold Serilog, men moderniser eksporten:**
    Fortsett å bruke Serilog for strukturert logging i koden, men fjern den utdaterte `ApplicationInsightsSink`. La OpenTelemetry håndtere all eksport til Azure.
*   **Reduser sikkerhetsstøy:**
    Filtrer ut helsesjekker (Health Probes) fra Application Gateway i loggene for å redusere kostnader og gjøre det enklere å finne reelle feil.

---

### Aksjonsplan

| Prioritet | Område | Beskrivelse |
| :--- | :--- | :--- |
| **Kritisk** | FSA Backend | Aktiver CORS for `traceparent` og `UseForwardedHeaders`. |
| **Kritisk** | Begge | Oppgrader til `UseAzureMonitor()` for fullstendig innsikt. |
| **Høy** | Bufdirno Site | Fjern Serilog AI Sink for å unngå doble logger/kostnader. |
| **Middels** | Frontend/Strapi | Fjern ConnectionString fra konsollogger og reduser støy i prod. |

---

### Dokumentoversikt

*   [Kritiske Funn og Tiltak](kritiske-funn-og-tiltak.md) - Detaljert gjennomgang av risikoer.
*   [Implementasjonsguide](implementasjonsguide.md) - Steg-for-steg kodedringer.
*   [Fallgruver ved Application Gateway](app-gateway-fallgruver.md) - Dypdykk i infrastruktur.
*   [Serilog og OpenTelemetry](serilog-og-opentelemetry.md) - Hvordan kombinere disse korrekt.
*   [JS/TS Verifisering](js-ts-monitoring-verification.md) - Spesifikke funn i frontend-kode.
*   [Gap-analyse](gap-analysis-implementation.md) - Strategi vs. faktisk implementering.
