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

#### Implementasjonsveiledning for Next.js og OpenTelemetry

For å få full sporing i Utrapporteringsbanken (både på serveren og i nettleseren), bruker vi en todelt strategi.

**1. Server-side (SSR, API-ruter, Databasekall): `src/instrumentation.ts`**

```typescript
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { NodeSDK } = await import('@opentelemetry/sdk-node');
    const { AzureMonitorTraceExporter } = await import('@azure/monitor-opentelemetry-exporter');
    const { getNodeAutoInstrumentations } = await import('@opentelemetry/auto-instrumentations-node');
    const { Resource } = await import('@opentelemetry/resources');
    const { SemanticResourceAttributes } = await import('@opentelemetry/semantic-conventions');

    const sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: 'Bufdir.Utrapporteringsbank.Server',
      }),
      traceExporter: new AzureMonitorTraceExporter({
        connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING,
      }),
      instrumentations: [
        getNodeAutoInstrumentations({
          '@opentelemetry/instrumentation-fs': { enabled: false },
        }),
      ],
    });

    sdk.start();
  }
}
```

**2. Klient-side (Browser): `src/components/MonitorInit.tsx`**

Fanger opp brukerinteraksjoner og ytelse i nettleseren.

```tsx
'use client';

import { useEffect } from 'react';
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { getWebAutoInstrumentations } from '@opentelemetry/auto-instrumentations-web';
import { AzureMonitorTraceExporter } from '@azure/monitor-opentelemetry-exporter';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

export function MonitorInit() {
  useEffect(() => {
    const provider = new WebTracerProvider({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: 'Bufdir.Utrapporteringsbank.Browser',
      }),
    });

    const exporter = new AzureMonitorTraceExporter({
      connectionString: "DIN_CONNECTION_STRING_HER",
    });

    provider.addSpanProcessor(new BatchSpanProcessor(exporter));

    registerInstrumentations({
      instrumentations: [
        getWebAutoInstrumentations({
          '@opentelemetry/instrumentation-fetch': {
            propagateTraceHeaderCorsUrls: [ /utrapporteringsbank\.bufdir\.no/g ],
          },
        }),
      ],
      tracerProvider: provider,
    });

    provider.register();
  }, []);

  return null;
}
```

**Viktige punkter:**
1. **Hvorfor experimental?** 
   Dette flagget er nødvendig fordi Next.js-teamet fortsatt anser instrumentation-funksjonaliteten som et eksperimentelt API. Det er likevel den anbefalte måten å fange opp server-side telemetri på.
2. **Todelt overvåking**: Ved å skille mellom `.Server` og `.Browser` kan vi identifisere om treghet i rapportgenerering skyldes selve server-prosessen eller overføring til klienten.
3. **Korrelasjon**: Browser-sporet kobles sammen med server-sporet og databasekallene (Drizzle) via W3C Trace Context.

### Oppgave 2.2: Overvåk autentisering (NextAuth.js og Maskinporten)
 - Logg vellykkede og feilede pålogginger via NextAuth.js (uten å logge sensitiv informasjon).
 - Overvåk integrasjon mot Maskinporten for henting av tokens (responstid og feilkoder).

### Oppgave 2.3: Instrumenter Database-kall (Drizzle)
 - Sørg for at `pg` (node-postgres) instrumenteres automatisk via `getNodeAutoInstrumentations`.
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
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('utrapporteringsbank-logic');

export async function generateReport() {
    try {
        // Logikk for generering
        tracer.startActiveSpan('ReportGeneratedSuccess', (span) => {
            span.end();
        });
    } catch (err) {
        tracer.startActiveSpan('ReportGeneratedFailure', (span) => {
            span.recordException(err as Error);
            span.end();
        });
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

Utrapporteringsbanken bruker Maskinporten for autentisering og kommuniserer med en PostgreSQL-database. Begge deler krever overvåking av legitimasjon.

### Oppgave 7.1: Overvåk Maskinporten-sertifikater
- Dersom virksomhetssertifikat eller private nøkler for Maskinporten er lagret i Key Vault, må det settes opp varsling for utløpsdato.
- Verifiser at autentiseringsflyten varsler (custom event) dersom Maskinporten returnerer feil relatert til utløpt legitimasjon.

### Oppgave 7.2: Overvåk Database-secrets
- Overvåk utløp på passord/secrets som brukes for å koble til Azure Database for PostgreSQL.

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
