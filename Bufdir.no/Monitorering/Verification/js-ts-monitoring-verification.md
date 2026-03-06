# Verifisering av JS/TS Monitorering

Dette dokumentet beskriver verifiseringen av monitorerings-implementasjonen for JavaScript/TypeScript (Next.js, React, Node.js).

---

### 1. Sikkerhetsrisiko: Eksponering av `ConnectionString`
I `FSA.Frontend.React` har det blitt funnet kode som logger hele `connectionString` (inkludert Authorization Keys) til konsollen i nettleseren dersom OpenTelemetry feiler under initialisering.
*   **Tiltak:** Fjern alle `console.log` av `connectionString` i produksjonskode.

### 2. Loggstøy i Strapi (Node.js)
Strapi-prosjektene bruker `CustomConsoleSpanExporter` og `DiagConsoleLogger`.
*   **Problem:** Dette skaper enorme mengder støy i loggene (stdout) i Azure, som gjør det vanskelig å finne ekte applikasjonsfeil.
*   **Tiltak:** Deaktiver disse i produksjon.

### 3. Aggressiv Filtrering (`ErrorOnlySpanExporter`)
Mange Node.js-prosjekter bruker en `ErrorOnlySpanExporter` som KUN sender data til Azure dersom statuskoden er over 400.
*   **Konsekvens:** Vi mister all oversikt over normale "suksessfulle" forespørsler og ytelsen på disse (p95, p99).
*   **Anbefaling:** Bruk standard **Sampling** (f.eks. 10%) i Azure Monitor i stedet for å filtrere bort 100% av suksessene i koden.
