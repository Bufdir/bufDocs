# Dokumentasjon av Monitorering i bufdirno-fsa-content

Dette dokumentet gir en oversikt over hvordan monitorering er implementert i `bufdirno-fsa-content` (Strapi CMS).

## Oversikt

Løsningen er basert på **OpenTelemetry** og er konfigurert for å sende telemetridata (traces og metrics) til **Azure Application Insights**. Implementasjonen er delt inn i tre hoveddeler: SDK-initialisering, global feilsporing (middleware) og tjeneste-sporing (service tracer).

## Komponenter

### 1. SDK-initialisering (`src/monitoring/instrumentation.js`)

Dette er inngangspunktet for OpenTelemetry-oppsettet. Den utfører følgende oppgaver:

- **Ressursdefinisjon:** Identifiserer tjenesten som `Bufdir.FSA.Content.NodeJS.Backend`.
- **Automatisk instrumentering:** Bruker `@opentelemetry/auto-instrumentations-node` for å automatisk fange opp telemetri fra:
  - `http`: Alle utgående og innkommende HTTP-kall.
  - `koa`: Strapi kjører på Koa, og denne fanger opp forespørselshåndtering.
  - `pg` / `mysql`: Database-spørringer til PostgreSQL eller MySQL.
- **Eksportører:**
  - **Azure Monitor:** Bruker `AzureMonitorTraceExporter` hvis `APPLICATIONINSIGHTS_CONNECTION_STRING` er satt.
  - **Lokal konsoll:** Bruker en `CustomConsoleSpanExporter` for å skrive forenklede sporingsdata til loggen under lokal utvikling.
- **Filtrering:** Inneholder en `ErrorOnlySpanExporter` som sørger for at **kun feil** (HTTP-status >= 400 eller spans med feilstatus) blir sendt til Azure for å begrense mengden data og kostnad.
- **Ignorerte endepunkter:** Forespørsler til `/admin`, `/favicon.ico` og `/_health` blir automatisk filtrert ut for å unngå unødvendig støy.

### 2. Feilsporings-middleware (`src/middlewares/error-tracking.js`)

En global Strapi-middleware som sikrer at alle forespørsler blir sporet riktig gjennom systemet.

- Den starter en aktiv "span" for hver forespørsel.
- Legger til metadata som `http.method`, `http.url` og `user.id`.
- Ved unntak (exceptions) blir feilen logget med full stack-trace og markert som en feil i OpenTelemetry, noe som gjør det enkelt å finne rotårsaken til feil i Azure.

### 3. Service Tracer (`src/utils/service-tracer.js`)

Dette er et verktøy for å legge til dypere instrumentering i Strapi sine tjeneste-metoder. **Merk:** Per nå er ikke denne i aktiv bruk i tjenestene i `bufdirno-fsa-content`.

- Funksjonen `withTracing(uid, service)` pakker inn standard CRUD-metoder (`find`, `create`, `update`, etc.) i en tjeneste.
- Dette gir innsikt i hvor lang tid hver spesifikke operasjon tar inne i applikasjonen, uavhengig av HTTP-laget.

## Vurdering av kompleksitet og nødvendighet

Implementasjonen er omfattende fordi den er skreddersydd for å balansere detaljrikdom mot kostnad i Azure. Her er en vurdering av de enkelte delene:

### SDK-oppsett (`instrumentation.js`)
- **Nødvendighet:** Høy (hvis man ønsker tracing i Azure).
- **Potensial for forenkling:** Den nåværende koden bruker mye "boilerplate". Microsoft har nå en enklere pakke, `@azure/monitor-opentelemetry`, som kan erstatte store deler av denne filen med en enkel kommando (`useAzureMonitor()`).
- **Kostnadskontroll:** `ErrorOnlySpanExporter` er en bevisst løsning for å spare penger ved å kun sende feil (400+) til Azure. Dette reduserer datamengden betraktelig.

### Middleware (`error-tracking.js`)
- **Nøvendighet:** Medium/Høy.
- **Verdi:** Den automatiske instrumenteringen fanger ikke alltid opp `user.id` eller detaljerte feilmeldinger fra Strapi på en god måte. Denne middleware-en sikrer at man har kontekst (hvilken bruker?) når feil oppstår.

### Service Tracer (`service-tracer.js`)
- **Nødvendighet:** **Lav**.
- **Vurdering:** Siden denne ikke er i bruk i noen aktive tjenester, kan den teknisk sett fjernes for å forenkle prosjektet. Den bør kun legges til hvis man opplever ytelsesproblemer som krever dypere analyse av interne metodekall.
- **Historikk og kjente feil:** Tidligere forsøk på å bruke `withTracing` i tjenestene førte til problemer (se commit `8db036c`). Hovedårsaken var en bug i `wrapMethod` knyttet til "closure" og `this`-kontekst. Fordi `wrapMethod` brukte en arrow-funksjon og kalte den originale metoden uten `.apply(this, args)`, mistet Strapi sine kjerne-tjenester tilgang til sin egen kontekst (f.eks. `this.getFetchParams` ble undefined).

Hvis dette verktøyet skal tas i bruk igjen, må `wrapMethod` endres til å bevare konteksten:
```javascript
const wrapMethod = (serviceName, methodName, method) => {
  return async function (...args) { // Bruk 'function' for å bevare 'this'
    return tracer.startActiveSpan(`${serviceName}.${methodName}`, async (span) => {
      try {
        const result = await method.apply(this, args); // Bind 'this' korrekt
        // ... resten av logikken
```

## Konfigurasjon

### Miljøvariabler

- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Nødvendig for å sende data til Azure Application Insights. Hvis denne mangler, vil applikasjonen kun logge sporingsdata til konsollen lokalt.

### Aktivering

Per dags dato er OpenTelemetry-instrumenteringen kommentert ut i `src/index.js`:

```javascript
// Initialize OpenTelemetry
//require('./monitoring/instrumentation');
```

For å aktivere monitoreringen må denne linjen avkommenteres, eller instrumenteringsfilen må inkluderes via `node --require ./src/monitoring/instrumentation.js` i oppstartsskriptet.

Middleware-en er konfigurert i `config/env/production/middlewares.js` og `config/env/development/middlewares.js` som `global::error-tracking`.

## Bruk lokalt

Når du kjører applikasjonen lokalt uten en tilkoblingsstreng til Azure, vil du se logger i konsollen som ligner på dette:

```json
{
  "logLevel": "Trace information",
  "traceId": "...",
  "name": "GET /api/articles",
  "durationMs": 45.2,
  "resource": { ... },
  "attributes": { ... }
}
```
