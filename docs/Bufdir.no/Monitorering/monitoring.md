# Overordnet Plan for Monitorering i Bufdirno

Dette dokumentet gir en oversikt over monitoreringsstrategien for hele prosjektet. Detaljerte oppgaver for hvert delprosjekt finnes i egne filer:

- [bufdirno (Hovedportal)](./bufdirno-monitoring.md)
- [bufdirno-fsa (Family Services Application)](./bufdirno-fsa-monitoring.md)
- [Familievern-api](./familievern-api-monitoring.md)
- [Fosterhjem-api](./fosterhjem-api-monitoring.md)
- [Newsletter-api](./newsletter-api-monitoring.md)
- [stat-system (Statistikk)](./stat-system-monitoring.md)
- [Utrapporteringsbank](./utrapporteringsbank-monitoring.md)
- [Sertifikater og Secrets](#overvåking-av-sertifikater-og-secrets)
- [Spesifikke metrikker og spor](#spesifikke-metrikker-og-spor-metrics--traces)

---

## Felles Oppgaver

### Fase 1: Grunnleggende infrastruktur
 - Opprett felles Log Analytics Workspace.
 - Opprett én felles Application Insights-ressurs (Workspace-based) for alle Bufdirno-komponenter for å sikre full korrelasjon (Distributed Tracing).
 - Konfigurer globale handlingsgrupper (Action Groups) for varsling.
 - Implementer Azure Security Center på tvers av alle abonnementer.

### Fase 2: Standardisering
 - Etabler felles navngivingskonvensjon for alle monitoreringsressurser.
 - Definer standard tagger for kostnadsstyring og filtrering.
 - Etabler struktur for Runbooks (se [veiledning](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md)).

---

## Korrelasjon og Distributed Tracing
For å kunne følge en forespørsel fra Next.js frontend, gjennom Optimizely CMS, og videre til mikrotjenester og databaser, er det avgjørende at:
1. **Felles ressurs:** Alle komponenter sender telemetri til samme Application Insights-ressurs.
2. **W3C Trace Context:** Alle tjenester må støtte og videreformidle standardiserte trace-headere (gjør automatisk av OpenTelemetry).
3. **Cloud Role Name:** Hver tjeneste må sette et unikt `service.name` (Cloud Role Name) i OpenTelemetry-konfigurasjonen for å skille dem i Application Map. Det anbefales å skille mellom `.Server` og `.Browser` for frontend-applikasjoner.

---

## Browser-monitorering og RUM (Real User Monitoring)
For applikasjoner med en frontend-del (Next.js, React) er det mulig og sterkt anbefalt å sette opp sporing og metrikker som kjører direkte i brukerens nettleser. Dette gir innsikt i:
*   **Faktisk brukeropplevelse:** Lastetider, rendering-ytelse (Core Web Vitals) og nettverksforsinkelse fra klientens ståsted.
*   **Klient-side feil:** JavaScript-unntak og feilede API-kall som ellers ikke ville vært synlige i server-logger.
*   **End-to-end sporing:** Ved bruk av W3C Trace Context kan en sporings-ID følge en forespørsel fra brukerens klikk i browseren, gjennom API-gateway, til backend-tjenester og helt ned til databasen.

### Sikkerhetshensyn ved Browser-monitorering
Når man instrumenterer koden som kjører i browseren, vil `ConnectionString` til Application Insights være synlig for sluttbrukeren.
1.  **Risikovurdering:** Denne strengen gir kun tillatelse til å *sende* data til Azure (Ingestion). Den gir ingen tilgang til å lese logger eller se andres data.
2.  **Anbefaling:** For Bufdirno anses dette som en akseptabel risiko for offentlige flater. For strengere krav kan man sette opp en **OpenTelemetry Collector** som fungerer som en proxy mellom browseren og Azure.

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
| Kategori | Lavt estimat (Lite trafikk) | Høyt estimat (Høy trafikk/debug) |
| :--- | :--- | :--- |
| Datainnsamling (7 moduler) | 250 kr | 1 200 kr |
| Lagring (90 dager) | 20 kr | 100 kr |
| Varsling & Tester | 80 kr | 250 kr |
| **Sum per måned** | **350 kr** | **1 550 kr** |

*Merk: Kostnadene er basert på at alle 7 moduler (portal, FSA, API-er, statistikk og utrapporteringsbank) er instrumentert. Kostnadene vil variere sterkt basert på "Logging Level". Hvis man logger all SQL-tekst og har mye trafikk, vil datamengden øke. Det anbefales å sette opp "Daily Cap" (f.eks. 5GB/dag) for å unngå uforutsette kostnader.*

---

## Varslingskonfigurasjon i Azure Monitor

Varsling er den proaktive delen av monitoreringen som sikrer at teamet får beskjed før brukerne merker feil. I Bufdirno-prosjektet brukes Azure Monitor Alerts.

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

For å unngå uforutsett nedetid forårsaket av utløpte sertifikater eller secrets, implementerer Bufdirno automatisert overvåking av Azure Key Vault og eksterne tjenester.

### 1. Azure Key Vault Overvåking
Key Vault har innebygd støtte for å sende hendelser til **Azure Event Grid** når en secret eller et sertifikat er nær utløpsdato.
*   **Log Analytics:** Alle aksesser og endringer i Key Vault logges til felles Log Analytics Workspace (Diagnostic Settings).
*   **Varsling:** Det settes opp Log Search Alerts som sjekker for hendelser relatert til utløp (Events med ID `SecretNearExpiry` eller `CertificateNearExpiry`).

### 2. Sertifikater (SSL/TLS)
*   **App Service:** Azure App Service har innebygd overvåking av Managed Certificates. For eksterne sertifikater må utløpsdato overvåkes manuelt eller via skript.
*   **Syntetiske tester:** Application Insights "Availability Tests" vil automatisk gi feil hvis et SSL-sertifikat utløper eller er ugyldig for en overvåket URL.

### 3. Azure AD App Registrations (Client Secrets)
*   **Problem:** Client Secrets for Azure AD utløper ofte etter 1-2 år og varsles ikke automatisk via standard Key Vault-logger hvis de kun er lagret som tekst.
*   **Løsning:** Det anbefales å bruke en Azure Automation Runbook eller en Logic App som periodisk (f.eks. ukentlig) sjekker utløpsdato på alle relevante App Registrations i Azure AD og sender varsel til Action Group hvis utløp er < 30 dager.

---

## Spesifikke metrikker og spor (Metrics & Traces)

For å gå fra grunnleggende overvåking ("kjører systemet?") til dyp innsikt ("fungerer forretningen optimalt?"), implementerer Bufdirno en strategi for finspisset modellering av metrikker og spor.

### 1. Kategorisering av data
*   **Tekniske metrikker:** Fokus på kjøretidsmiljøet (f.eks. Node.js event loop delay, SQL-responstider, minnebruk).
*   **Brukeropplevelse (RUM):** Fokus på klient-side ytelse (f.eks. Core Web Vitals, hydration-tid i Next.js).
*   **Forretningsmetrikker:** Fokus på verdi og flyt (f.eks. fullføringsgrad for søknader, suksessrate for nyhetsbrev).

### 2. Strategisk verdi
Ved å bruke OpenTelemetry-standarden på tvers av alle språk (.NET, Node.js, TypeScript) oppnår vi:
*   **Sammenhengende feilsøking:** Vi kan følge en "trace" fra en treghet i browseren, gjennom API-er, til den nøyaktige SQL-spørringen som forårsaket den.
*   **Proaktiv optimalisering:** Metrikker som `cache.hit_rate` og `query_complexity` gjør at vi kan optimalisere infrastrukturen før det oppstår flaskehalser.
*   **Forretningsinnsikt:** Ved å logge `customEvents` for kritiske steg i en søknadsprosess, kan vi identifisere hvor brukere faller fra uten å trenge komplekse analyseverktøy.

### 3. Veien videre
Hvert delprosjekt har sitt eget kapittel for spesifikke metrikker og spor. Disse bør gjennomgås og finspisses i takt med at applikasjonene utvikles:
*   Se Fase 7 i [bufdirno](./bufdirno-monitoring.md), [bufdirno-fsa](./bufdirno-fsa-monitoring.md), [stat-system](./stat-system-monitoring.md) og [Utrapporteringsbank](./utrapporteringsbank-monitoring.md).
*   Se Fase 5 i [familievern-api](./familievern-api-monitoring.md), [fosterhjem-api](./fosterhjem-api-monitoring.md) og [newsletter-api](./newsletter-api-monitoring.md).

---

## Implementeringsstatus
Gå til de spesifikke prosjektfilene for detaljerte oppgaver.
