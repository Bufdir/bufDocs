# Monitoreringsoppgaver for Utrapporteringsbank

## Gevinst med monitorering (Brukerhistorie)
**Som** forvalter av Utrapporteringsbanken,
**ønsker jeg** dyp innsikt i rapportgenerering og sikker autentisering via Maskinporten,
**slik at** vi kan garantere feilfrie rapporter og en trygg brukeropplevelse for alle saksbehandlere.

### Akseptansekriterier
 - Rapportgenerering overvåkes og det sendes varsel ved feil eller unormal tidsbruk.
 - Autentisering via Maskinporten logges for å identifisere påloggingsproblemer.
 - Databaseytelse (PostgreSQL via Drizzle) er synlig i dashboards.
 - Distributed tracing viser hele løpet fra brukerinteraksjon til ferdig generert rapport.

Dette dokumentet beskriver oppgavene som kreves for å sette opp monitorering for **Utrapporteringsbank**, en Next.js-applikasjon som bruker Drizzle ORM og PostgreSQL.

### Hybrid Monitoreringsstrategi
Utrapporteringsbanken benytter en hybrid monitoreringsmodell:
1.  **Frontend (Nettleser): Azure Application Insights SDK**
    *   **Hvorfor:** Spesialtilpasset for Real User Monitoring (RUM). Fanger opp brukersesjoner, sidevisninger og klient-exceptions mer detaljert enn standard OpenTelemetry.
2.  **Backend (Next.js Server / API): OpenTelemetry**
    *   **Hvorfor:** Industristandard for server-side instrumentering. Sikrer høy ytelse ved rapportgenerering og dyp innsikt i databasekall.
3.  **Korrelasjon:** Ved å bruke **W3C Trace Context** sikrer vi at en brukers forespørsel kan følges fra nettleseren og helt gjennom server-side logikken.

## Innholdsfortegnelse

- [Fase 1: Grunnleggende oppsett](#fase-1-grunnleggende-oppsett)
- [Fase 2: Applikasjonsinstrumentering](#fase-2-applikasjonsinstrumentering)
- [Fase 3: Infrastrukturmonitorering](#fase-3-infrastrukturmonitorering)
- [Fase 4: Varslingskonfigurasjon](#fase-4-varslingskonfigurasjon)
- [Fase 5: Dashboards og visualisering](#fase-5-dashboards-og-visualisering)
- [Fase 6: Dokumentasjon og runbooks](#fase-6-dokumentasjon-og-runbooks)
- [Fase 7: Overvåking av sertifikater og secrets](#fase-7-overvåking-av-sertifikater-og-secrets)
- [Fase 8: Spesifikke metrikker og spor (Metrics & Traces)](#fase-8-spesifikke-metrikker-og-spor-metrics--traces)

---

## Fase 1: Grunnleggende oppsett

### Oppgave 1.1: Bruk felles Application Insights-ressurs
 - Koble `utrapporteringsbank` til den felles Application Insights-ressursen for Bufdirno.
 - Verifiser at `APPLICATIONINSIGHTS_CONNECTION_STRING` er tilgjengelig i miljøvariablene (Azure Container App).
 - Konfigurer ressurs-tagger: `project: utrapporteringsbank`, `service: frontend-api`.

---

## Fase 2: Applikasjonsinstrumentering

### Oppgave 2.1: Instrumenter Next.js Frontend og API (Node.js)
 - Installer OpenTelemetry npm-pakker:
  ```bash
  npm install @opentelemetry/api @opentelemetry/sdk-node \
    @opentelemetry/auto-instrumentations-node \
    @opentelemetry/sdk-trace-web \
    @opentelemetry/instrumentation-xml-http-request \
    @opentelemetry/instrumentation-fetch \
    @opentelemetry/resources \
    @opentelemetry/semantic-conventions \
    @opentelemetry/exporter-trace-otlp-http \
    @azure/monitor-opentelemetry-exporter
  ```
 - Aktiver OpenTelemetry i `next.config.ts`:
  ```typescript
  const nextConfig: NextConfig = {
    experimental: {
      instrumentationHook: true,
    },
    // ... andre innstillinger
  };
  ```
 - Opprett `src/instrumentation.ts` for å fange opp HTTP-forespørsler og databasekall.

#### Implementasjonsveiledning for Application Insights (Node.js & Browser)

For å få full sporing i Utrapporteringsbanken (både på serveren og i nettleseren), bruker vi Application Insights SDK-er.

**1. Server-side (SSR, API-ruter, Databasekall): `src/instrumentation.ts`**

```typescript
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { NodeSDK } = await import('@microsoft/applicationinsights-node-js');
    // Konfigurer for Node.js
  }
}
```

##### Unngå støy fra 404 på serversiden (Node.js / Next.js API)
Når du bruker OpenTelemetry-instrumentering for HTTP, kan du filtrere bort typiske 404-ruter (favicon, `/_next/`-assets, helsesjekker) slik:

```typescript
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';

const httpInstr = new HttpInstrumentation({
  ignoreIncomingRequestHook: (req) => {
    const url = req.url || '';
    return url.includes('favicon') || url.startsWith('/_next/') || url.includes('/health') || url.endsWith('.map');
  }
});

// I NodeSDK-konfigurasjonen, legg til instrumentasjonen:
// new NodeSDK({ instrumentations: [httpInstr, ...andre] })
```

**2. Klient-side (Browser): `src/components/MonitorInit.tsx`**

```tsx
'use client';

import { useEffect } from 'react';
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

export function MonitorInit() {
  useEffect(() => {
    const appInsights = new ApplicationInsights({
      config: {
        connectionString: "DIN_CONNECTION_STRING_HER",
        enableAutoRouteTracking: true,
      }
    });
    appInsights.loadAppInsights();

    // Dropp 404 i nettleseren for å unngå unødvendig telemetri
    appInsights.addTelemetryInitializer((telemetry) => {
      if (telemetry.data && telemetry.data.responseCode === 404) {
        return false;
      }
    });

    appInsights.trackPageView();
  }, []);

  return null;
}
```

### Viktig ved CORS-feil:
Ved bruk av Distributed Tracing legger frontenden til ekstra headere (`traceparent` osv.). Hvis du får CORS-feil i Utrapporteringsbanken (som er en Next.js-app), se den [detaljerte veiledningen for Next.js CORS](./monitoring.md#3-løsning-i-nextjs-nodejs-backend) i hovedplanen.

**Viktige punkter:**
1. **Todelt overvåking**: Ved å skille mellom server og browser kan vi se hvor treghet oppstår.
2. **Korrelasjon**: Browser-sporet kobles sammen med server-sporet via W3C Trace Context.
3. **Azure Application Gateway**: Pass på at gatewayen tillater sporings-headerne (`traceparent` osv.).

### Oppgave 2.2: Overvåk autentisering (NextAuth.js og Maskinporten)
 - Logg vellykkede og feilede pålogginger via NextAuth.js (uten å logge sensitiv informasjon).
 - Overvåk integrasjon mot Maskinporten for henting av tokens (responstid og feilkoder).

### Oppgave 2.3: Instrumenter Database-kall (Drizzle)
 - Sørg for at databasekall instrumenteres automatisk.
 - Verifiser at SQL-spørringer dukker opp som "Dependencies" i Application Insights.

---

## Fase 3: Infrastrukturmonitorering

### Oppgave 3.1: Monitorer Azure Container App
 - Konfigurer logginnsamling for containeren til felles Log Analytics Workspace.
 - Overvåk ressursbruk (CPU/Minne) for å identifisere behov for skalering.

### Oppgave 3.2: Databaseovervåking (Azure Database for PostgreSQL)
 - Aktiver overvåking for PostgreSQL-instansen i Azure Portal.
 - Overvåk aktive tilkoblinger, CPU-bruk og IOPS.
 - Konfigurer Query Store for å identifisere trege spørringer fra Drizzle.

---

## Fase 4: Varslingskonfigurasjon

### Oppgave 4.1: Tilgjengelighet og ytelse
 - Sett opp syntetisk test for hovedsiden og kritiske API-ruter under `/api/`.
 - Varsle ved HTTP 5xx-feil > 5 per 5 minutter.
 - Varsle dersom rapportgenerering tar mer enn 30 sekunder.

### Oppgave 4.2: Forretningskritiske varsler
 - Varsle dersom en viktig rapport feiler under generering (selv om API-et svarer 200).
 - Varsle ved unormalt mange mislykkede påloggingsforsøk (potensielt angrep eller problem med Maskinporten).
 - Logg hendelsen `ReportGeneratedSuccess` vs `ReportGeneratedFailure` for å overvåke forretningsverdi.

#### Logging av hendelser i Next.js (Server Side)
```typescript
import { TelemetryClient } from '@microsoft/applicationinsights-node-js';
const client = new TelemetryClient();

export async function generateReport() {
    try {
        // Logikk for generering
        client.trackEvent({ name: 'ReportGeneratedSuccess' });
    } catch (err) {
        client.trackException({ exception: err as Error });
        client.trackEvent({ name: 'ReportGeneratedFailure' });
        throw err;
    }
}
```

---

## Fase 5: Dashboards og visualisering

### Oppgave 5.1: Utrapporteringsbank Dashboard
 - Vis antall genererte rapporter over tid.
 - Vis feilrate for API-endepunkter under `/api/reports`.
 - Vis ytelse for database-spørringer (gjennomsnittlig utførelsestid).

---

## Fase 6: Dokumentasjon og runbooks

### Oppgave 6.1: Runbooks for Utrapporteringsbank
 - Opprett runbook for feilsøking ved manglende data i rapporter.
 - Opprett runbook for problemer med Maskinporten-integrasjon.
 - Se [veiledning](./runbook/runbook-guide.md) og [mal](./runbook/runbook-template.md) for runbooks.

---

## Fase 7: Overvåking av sertifikater og secrets

Utrapporteringsbanken bruker ID-porten og Maskinporten for sikker autentisering, noe som krever nøye overvåking av secrets og sertifikater.

### Oppgave 7.1: Overvåk ID-porten og Maskinporten
- Sørg for at alle client secrets og virksomhetssertifikater er lagret i Azure Key Vault.
- Aktiver "CertificateNearExpiry" og "SecretNearExpiry" varsling i Key Vault.
- Spesielt viktig for:
    - **ID-porten Client Secret** (`IDPORTEN_CLIENT_SECRET`): Må roteres periodisk.
    - **Azure AD Client Secret** (`AZURE_CLIENT_SECRET`): Brukes for autentisering.
    - **Maskinporten Virksomhetssertifikat**: Overvåk utløpsdato nøye for å unngå avbrudd i autentisering.

### Oppgave 7.2: Overvåk SSL og Database
- Sett opp en Availability Test i Application Insights for å overvåke SSL-sertifikatet til `utrapporteringsbank` sitt offentlige endepunkt.
- Overvåk utløp på passord/secrets som brukes for å koble til Azure Database for PostgreSQL via Drizzle.

---

## Fase 8: Spesifikke metrikker og spor (Metrics & Traces)

Dette kapittelet beskriver spesifikke metrikker og spor som er relevante for finspissing av overvåkingsmodellen for Utrapporteringsbank.

### Oppgave 8.1: Implementering
 - Implementer måling av følgende tekniske og funksjonelle metrikker:
    - **Metrikker (Metrics):**
        - `ub.report_generation.duration`: Tid det tar å generere en PDF/Excel-rapport.
        - `ub.db.connection_pool.usage`: Bruk av tilkoblinger mot PostgreSQL-databasen.
        - `ub.auth.maskinporten_latency`: Tid det tar å validere tokens mot Maskinporten.
        - `nodejs.cpu.usage`: CPU-bruk for Node.js-prosessen (viktig ved PDF-generering).
        - `nodejs.eventloop.lag`: Tid det tar før en oppgave i event loopen blir utført.
    - **Sporing (Traces):**
        - `ReportExportTrace`: Sporing av hele eksportløpet fra forespørsel til ferdig fil.
        - `TokenExchangeFlow`: Sporing av autentiseringsprosessen mot Maskinporten.
        - `DatabaseQueryTrace`: Detaljert sporing av tid brukt på komplekse SQL-spørringer via Drizzle.
        - `NextAuthCallbackTrace`: Sporing av callback-håndtering i NextAuth.js.
