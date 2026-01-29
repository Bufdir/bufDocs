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

### Hybrid Monitoreringsstrategi (Anbefalt)
Bufdirno benytter en hybrid tilnærming for monitorering:
1.  **Frontend (Next.js Browser): Azure Application Insights SDK**
    *   **Hvorfor:** Gir best innsikt i brukeropplevelse (RUM), sidevisninger, og klientside-exceptions. Det er optimalisert for nettlesere og krever ingen kompleks proxy-infrastruktur.
2.  **Backend (Optimizely / Node.js Server): OpenTelemetry**
    *   **Hvorfor:** Industristandard for server-side telemetri. Sikrer høy ytelse, leverandørnøytralitet og dyp integrasjon med moderne skyplattformer.
3.  **Sammenheng:** Ved å bruke **W3C Trace Context** på tvers av både AI SDK og OpenTelemetry, oppnår vi sømløs korrelasjon og et komplett "Application Map" i Azure.

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
 - Installer Application Insights NuGet-pakke i `bufdirno` CMS-modulen.
 - Konfigurer Application Insights i `ConfigureCoreServices.cs` for å fange opp Optimizely-spesifikke metrikker og SQL Server-kall.
 - Legg til connection string i `appsettings.json`.

#### Implementasjonsveiledning for OpenTelemetry (.NET)
For å sette opp OpenTelemetry i hovedportalen, legg til følgende pakke:
`Azure.Monitor.OpenTelemetry.AspNetCore`.

Eksempel på konfigurasjon i `ConfigureCoreServices.cs`:
```csharp
using Azure.Monitor.OpenTelemetry.AspNetCore;
using OpenTelemetry.Resources;

// I AddCoreServices:
services.AddOpenTelemetry()
    .ConfigureResource(resource => resource.AddService("Bufdir.Portal.CMS"))
    .UseAzureMonitor(options =>
    {
        options.ConnectionString = configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];
    });
```

### Oppgave 2.2: Instrumenter Next.js Frontend (Server & Browser)
 - Installer Application Insights SDK-er:
  ```bash
  npm install @microsoft/applicationinsights-web @microsoft/applicationinsights-node-js
  ```
 - Opprett `instrumentation.ts` for Server Side (SSR/API).
 - Opprett `OTELClient.tsx` (eller `AIClient.tsx`) for Browser-instrumentering.

#### Implementasjonsveiledning for Next.js og Application Insights

For å få full sporing i Next.js (både på serveren og i nettleseren), bruker vi Application Insights SDK-er direkte.

**1. Server-side (SSR, API-ruter, Middleware): `src/instrumentation.ts`**

```typescript
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { NodeSDK } = await import('@microsoft/applicationinsights-node-js');
    // Konfigurer for Node.js
  }
}
```

**2. Klient-side (Browser): `src/components/AIClient.tsx`**

```tsx
'use client';

import { useEffect } from 'react';
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

export function AIClient() {
  useEffect(() => {
    const appInsights = new ApplicationInsights({
      config: {
        connectionString: "DIN_CONNECTION_STRING_HER",
        enableAutoRouteTracking: true,
      }
    });
    appInsights.loadAppInsights();
    appInsights.trackPageView();
  }, []);

  return null;
}
```

**Viktige punkter for Bufdirno:**
1. **Sikkerhet**: Ved browser-monitorering blir Connection String synlig. Dette er normal praksis for RUM.
2. **W3C Trace Context**: Sikrer korrelasjon mellom browser og backend.

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

Eksempel på logging med Application Insights:
```csharp
private TelemetryClient _telemetryClient;

public void ProcessAction(string actionName)
{
    _telemetryClient.TrackEvent("BusinessActionCompleted", new Dictionary<string, string> { { "Action", actionName } });
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
- Spesielt viktig for:
    - **Azure AD Client Secret** (`InternalResources:ClientSecret`): Brukes for OAuth2-autentisering. Utløper typisk etter 24 måneder.
    - **SendGrid API Key** (`FeedbackApi:Mail:SendGridKey`): Brukes for e-postvarsler. Bør roteres årlig.
    - **Application Insights Connection String**: Sikre at denne er gyldig og tilgjengelig.

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
