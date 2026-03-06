# Serilog og OpenTelemetry i Bufdir.no

Dette dokumentet beskriver hvordan vi kombinerer den eksisterende Serilog-konfigurasjonen med det nye OpenTelemetry-oppsettet for best mulig effekt.

---

### Målsetning
*   Beholde Serilog som motor for strukturert logging i koden.
*   Beholde lokale sinks (Console/File) for lokal utvikling.
*   Bytte ut `Serilog.Sinks.ApplicationInsights` med OpenTelemetry for sending til Azure Monitor.

---

### Hvorfor bytte ut Serilog AI Sink?
1.  **Dobbel Logging:** Når både Serilog AI Sink og OpenTelemetry er aktive, sendes loggene to ganger til Azure, som dobler kostnadene.
2.  **Korrelasjon:** OpenTelemetry er designet for å koble logger direkte sammen med Traces (sporing). Dette fungerer best når OpenTelemetry selv håndterer eksporten.
3.  **Fremtidsrettet:** Microsoft anbefaler OpenTelemetry som den primære måten å sende telemetri til Azure på i moderne .NET-applikasjoner.

---

### Implementasjonsstrategi

*   Fjern `Serilog.Sinks.ApplicationInsights` NuGet-pakken.
*   Fjern AI-sink konfigurasjonen i `appsettings.json` under `Serilog:WriteTo`.
*   Bruk `.UseAzureMonitor()` fra `Azure.Monitor.OpenTelemetry.AspNetCore` i `Program.cs`.

OpenTelemetry vil automatisk fange opp alle logger som sendes via `ILogger` (inkludert de som går via Serilog-pipelinen) og sende dem til Azure Monitor med full korrelasjonsdata.
