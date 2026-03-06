# Gap-analyse: Implementasjon vs. Strategi

Dette dokumentet analyserer avvikene mellom den vedtatte monitoreringsstrategien og den faktiske implementasjonen i koden.

---

### Oversikt over avvik

| Område | Strategi | Faktisk Implementasjon | Status |
| :--- | :--- | :--- | :--- |
| **OpenTelemetry (FSA)** | Skal bruke standard OTEL | Bruker manuelt oppsett uten metrics/logs | ⚠️ Avvik |
| **OpenTelemetry (Site)** | Skal bruke standard OTEL | Bruker manuelt oppsett (trace exporter) | ⚠️ Avvik |
| **Logging (Serilog)** | Skal slutte å sende direkte til AI | Bruker fortsatt `ApplicationInsightsSink` | ⚠️ Avvik |
| **CORS (W3C)** | Skal støtte distribuert sporing | Backend blokkerer `traceparent`-header | ❌ Kritisk |
| **Infrastruktur** | Skal støtte App Gateway | Mangler `ForwardedHeaders`-oppsett | ⚠️ Avvik |

### Konsekvenser av gapet
1.  **Produksjonsstopp:** CORS-avviket er den direkte årsaken til at applikasjonen slutter å fungere når overvåking aktiveres.
2.  **Kostnadseksplosjon:** Dobbel logging i Site (Serilog + OTEL) fører til unødvendige Azure-kostnader.
3.  **Manglende innsikt:** Uten Metrics og Logs i FSA-backend er man "blind" for ytelsesproblemer og ressursbruk.

### Anbefalte tiltak
Se [Implementasjonsguide](implementasjonsguide.md) for konkrete steg for å lukke disse gapene.
