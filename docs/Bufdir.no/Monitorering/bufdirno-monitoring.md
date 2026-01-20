# Monitoreringsoppgaver for bufdirno (hovedportal)

## Gevinst med monitorering (Brukerhistorie)
**Som** produkteier for hovedportalen,
**ønsker jeg** full innsikt i tilstanden til Optimizely CMS og Next.js-frontenden,
**slik at** vi kan minimere nedetid, optimalisere brukeropplevelsen (RUM) og løse tekniske problemer før de påvirker innbyggerne.

### Akseptansekriterier
 - Dashboards viser sanntidsdata for både backend (Optimizely) og frontend (Next.js).
 - Det sendes varsel ved kritiske feil eller treghet i portalen.
 - Distributed tracing fungerer sømløst fra brukerens nettleser til databasen.
 - Tekniske metrikker (Core Web Vitals) er tilgjengelige for ytelsesanalyse.

Dette dokumentet beskriver oppgavene som kreves for å sette opp monitorering spesifikt for **bufdirno** (hovedportalen), som består av en Optimizely CMS backend (.NET) og en Next.js frontend.

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
 - Koble `bufdirno` til den felles Application Insights-ressursen definert i [hovedplanen](./monitoring.md).
 - Verifiser at Instrumentation Key / Connection String er lagt inn i Key Vault.
 - Sett oppbevaringsperiode til 90 dager i Log Analytics.

### Oppgave 1.2: Konfigurer ressurs-tagger
 - Bruk tagger: `environment: prod`, `service: bufdirno`, `project: main-portal`

---

## Fase 2: Applikasjonsinstrumentering

### Oppgave 2.1: Instrumenter Optimizely CMS (.NET)
 - Installer OpenTelemetry NuGet-pakker i `bufdirno` CMS-prosjektet.
 - Konfigurer OpenTelemetry i `Program.cs` for å fange opp Optimizely-spesifikke metrikker og SQL Server-kall.
 - Legg til connection string i `appsettings.json`.

#### Implementasjonsveiledning for OpenTelemetry og SQL Server
For å sette opp OpenTelemetry med SQL Server-overvåking i hovedportalen, legg til følgende pakker:
`OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore`, `OpenTelemetry.Instrumentation.SqlClient`, og `Azure.Monitor.OpenTelemetry.AspNetCore`.

Eksempel på konfigurasjon i `Program.cs`:
```csharp
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

// Ressursnavn for portalen
var serviceName = "Bufdir.Portal.CMS";

builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .AddSource(serviceName)
            .SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(serviceName))
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            // Aktiverer dyp overvåking av SQL Server-kall (viktig for Optimizely CMS)
            .AddSqlClientInstrumentation(options =>
            {
                options.SetDbStatementForStoredProcedures = true;
                options.SetDbStatementForText = true; // Inkluderer selve SQL-spørringen
                options.RecordException = true;
            })
            .AddAzureMonitorTraceExporter(o => o.ConnectionString = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"]);
    })
    .WithMetrics(metrics =>
    {
        metrics
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddRuntimeInstrumentation();
    });
```

### Oppgave 2.2: Instrumenter Next.js Frontend (Node.js & Browser)
 - Installer OpenTelemetry npm-pakker i frontend-mappen:
  ```bash
  npm install @opentelemetry/api @opentelemetry/sdk-node \
    @opentelemetry/auto-instrumentations-node \
    @opentelemetry/sdk-trace-web \
    @opentelemetry/instrumentation-xml-http-request \
    @opentelemetry/instrumentation-fetch \
    @azure/monitor-opentelemetry-exporter
  ```
 - Aktiver OpenTelemetry i `next.config.js` (eller `.ts`) for Server Side:
  ```javascript
  const nextConfig = {
    experimental: {
      instrumentationHook: true,
    },
    // ... andre innstillinger
  };
  ```
 - Opprett `instrumentation.ts` for Server Side (SSR/API).
 - Opprett `otel-client.ts` for Browser-instrumentering.
 - Verifiser korrelasjon mellom browser, Next.js server og backend-traces.

#### Implementasjonsveiledning for Next.js og OpenTelemetry

For å få full sporing i Next.js (både på serveren og i nettleseren) som sender data til Azure Application Insights, må vi dele opp instrumenteringen.

**1. Server-side (SSR, API-ruter, Middleware): `src/instrumentation.ts`**

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
        [SemanticResourceAttributes.SERVICE_NAME]: 'Bufdir.Portal.Frontend.Server',
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

**2. Klient-side (Browser): `src/components/OTELClient.tsx`**

For å fange opp det som skjer i brukerens nettleser (f.eks. klikk, ressurslasting, og `fetch`-kall), må vi kjøre en egen SDK i browseren.

```tsx
'use client';

import { useEffect } from 'react';
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { getWebAutoInstrumentations } from '@opentelemetry/auto-instrumentations-web';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { AzureMonitorTraceExporter } from '@azure/monitor-opentelemetry-exporter';

export function OTELClient() {
  useEffect(() => {
    const provider = new WebTracerProvider({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: 'Bufdir.Portal.Frontend.Browser',
      }),
    });

    // Merk: AzureMonitorTraceExporter fungerer i browser dersom CORS er satt opp,
    // men pass på eksponering av Connection String i kildekoden.
    const exporter = new AzureMonitorTraceExporter({
      connectionString: "DIN_CONNECTION_STRING_HER", // Bør injiseres via miljøvariabel
    });

    provider.addSpanProcessor(new BatchSpanProcessor(exporter));

    registerInstrumentations({
      instrumentations: [
        getWebAutoInstrumentations({
          '@opentelemetry/instrumentation-fetch': {
            propagateTraceHeaderCorsUrls: [ /api\.bufdir\.no/g ], // Korrelerer mot backend
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
*Legg til `<OTELClient />` i din `RootLayout` for å starte overvåking av alle brukere.*

**Viktige punkter for Bufdirno:**
1. **Service Navn**: Vi skiller mellom `.Server` og `.Browser` for å se nøyaktig hvor tregheten oppstår i Application Map.
2. **Sikkerhet**: Ved browser-monitorering blir Connection String synlig i JS-bundelen. Siden dette kun gir rettighet til å *skrive* telemetri, anses det ofte som en akseptabel risiko i offentlige portaler, men man kan bruke en proxy-gateway hvis man ønsker full kontroll.
3. **W3C Trace Context**: Dette sikrer at `trace-id` følger med fra browser -> Next.js Server -> Optimizely CMS -> Database.

---

## Fase 3: Infrastrukturmonitorering

### Oppgave 3.1: Monitorer Azure App Service
 - Aktiver diagnostikkinnstillinger for `bufdirno` Web App.
 - Konfigurer HTTP-logger og applikasjonslogger.
 - Overvåk App Service Plan (CPU, minne) for å skalere ved behov.

### Oppgave 3.2: Databaseovervåking (Azure SQL)
 - Aktiver overvåking for `bufdirno`-databasen i Azure SQL.
 - Overvåk DTU/vCore-bruk og deadlocks.
 - Konfigurer Query Performance Insight for å finne trege spørringer i CMS-et.

---

## Fase 4: Varslingskonfigurasjon

### Oppgave 4.1: Tilgjengelighetsvarsler
 - Opprett URL ping-test for `https://www.bufdir.no`.
 - Varsle ved utilgjengelighet eller responstid > 3 sekunder.

### Oppgave 4.2: Feilvarsler
 - Varsle ved HTTP 5xx-feil > 10 per minutt.
 - Varsle ved kritiske CMS-feil i loggene.

### Oppgave 4.3: Forretningshendelser og logikkfeil
 - Definer kritiske forretningshendelser i Optimizely (f.eks. "Søk feilet", "Viktig innhold mangler").
 - Implementer logging av Custom Events i C# for disse hendelsene.
 - Sett opp varsel basert på KQL-spørring mot `customEvents`.

Eksempel på logging med OpenTelemetry:
```csharp
// Bruk ActivitySource for OpenTelemetry
private static readonly ActivitySource _activitySource = new ActivitySource("Bufdir.Portal.CMS");

public void ProcessAction(string actionName)
{
    using var activity = _activitySource.StartActivity("BusinessActionCompleted");
    activity?.SetTag("Action", actionName);
    activity?.SetTag("UserType", "Internal");
    // ... logikk ...
}
```

---

## Fase 5: Dashboards og visualisering

### Oppgave 5.1: Opprett bufdirno-dashboard
 - Vis besøksstatistikk vs. feilrate.
 - Vis ytelse for Optimizely-sider.
 - Vis status for databaseforbindelser.

---

## Fase 6: Dokumentasjon og runbooks

### Oppgave 6.1: Runbooks for bufdirno
 - Opprett runbook for feilsøking ved treghet i Optimizely CMS (bruk [mal](./runbook/runbook-template.md)).
 - Opprett runbook for gjenoppretting ved databasefeil.
 - Se [veiledning for runbooks](./runbook/runbook-guide.md) for beste praksis.

---

## Fase 7: Overvåking av sertifikater og secrets

Denne fasen fokuserer på å forhindre nedetid for hovedportalen på grunn av utløpte tekniske nøkler.

### Oppgave 7.1: Overvåk SSL-sertifikater for bufdir.no
- Opprett en Availability Test i Application Insights for `https://www.bufdir.no`.
- Verifiser at testen varsler dersom SSL-sertifikatet er ugyldig eller utløper om mindre enn 14 dager.

### Oppgave 7.2: Aktiver varsling for Key Vault secrets
- Konfigurer Diagnostic Settings for Key Vault til å sende logger til Log Analytics.
- Opprett en Log Search Alert som sjekker for `SecretNearExpiry`-hendelser.
- Spesielt viktig for: Client Secrets til Azure AD App Registrations som brukes av Optimizely og Next.js.

---

## Fase 8: Spesifikke metrikker og spor (Metrics & Traces)

Dette kapittelet beskriver spesifikke metrikker og spor som er relevante for finspissing av overvåkingsmodellen for bufdirno.

### Oppgave 8.1: Implementering
 - Implementer måling av følgende tekniske og funksjonelle metrikker:
    - **Metrikker (Metrics):**
        - `cms.cache.hit_rate`: Treffprosent i Optimizely-cachen (viktig for ytelse).
        - `frontend.hydration.duration`: Tid det tar for Next.js å hydrere på klienten.
        - `frontend.page_load.time`: Total lastetid for kritiske sider sett fra brukerens nettleser.
        - `cms.content.publish_frequency`: Hvor ofte innhold publiseres (aktivitetsindikator).
        - `nodejs.eventloop.delay`: Forsinkelse i Node.js event loop (indikerer CPU-flaskehalser i SSR).
        - `nodejs.memory.heap.usage`: Minnebruk for Next.js server-prosessen.
        - `nodejs.gc.duration`: Tid brukt på garbage collection (identifiserer minne-stress).
    - **Sporing (Traces):**
        - `SearchRequest`: Sporing av søkeforespørsler for å se ytelse og eventuelle feil i søkemotoren.
        - `NavigationRequest`: Sporing av menynavigasjon og ruting-ytelse.
        - `MiddlewareExecution`: Sporing av Next.js Middleware (autentisering, omdirigeringer).

#### Implementasjonsveiledning for metrikker i C#
```csharp
using System.Diagnostics.Metrics;

private static readonly Meter _meter = new Meter("Bufdir.Portal.CMS");
private static readonly Counter<long> _cacheHitCounter = _meter.CreateCounter<long>("cms.cache.hit_rate");

public void GetData(string key)
{
    var data = _cache.Get(key);
    if (data != null) {
        _cacheHitCounter.Add(1, new TagList { { "cache_type", "memory" } });
    }
}
```
