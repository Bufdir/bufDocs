# Veiledning: Hvordan opprette gode Runbooks

En runbook er et dokumentert sett med prosedyrer for å løse et spesifikt operasjonelt problem. I Bufdirno-prosjektet bruker vi runbooks for å sikre rask respons ved feil i produksjon.

## Hva er en runbook?
I Azure kan "runbooks" referere til to forskjellige konsepter:
1.  **Manuelle Runbooks (Dokumentasjon):** Markdown-filer (som denne) som beskriver steg for et menneske.
2.  **Automatiserte Runbooks (Azure Automation):** Skript (PowerShell/Python) som utfører handlinger automatisk.

Se [veiledning for oppsett i Azure](./azure-automation-runbook-setup.md) for detaljer om begge typene.

## Hvorfor trenger vi runbooks?
- **Reduserer MTTR (Mean Time To Repair):** Ved å ha ferdige steg sparer man tid på analyse i en stresset situasjon.
- **Deler kunnskap:** Ekspertise fra senioreutviklere gjøres tilgjengelig for alle som har vakt.
- **Konsistens:** Sikrer at feilsøking gjøres på en strukturert og trygg måte.

## Slik skriver du en god runbook

### 1. Vær spesifikk
Hver runbook bør dekke ett konkret scenario (f.eks. "Treghet i databasen" fremfor "Noe er galt").

### 2. Bruk sjekklister
Bruk kulepunkter slik at den som utfører prosedyren kan følge stegene systematisk.

### 3. Inkluder ferdige kommandoer og spørringer
Ikke be brukeren "sjekke loggene". Gi dem den nøyaktige KQL-spørringen (Kusto Query Language) de skal lime inn i Azure Log Analytics.

### 4. Beskriv varslingstegn
Svar på spørsmålet: "Hvordan vet jeg at det er akkurat denne runbooken jeg trenger nå?". Referer til spesifikke varsler (alerts) fra Application Insights.

### 5. Hold den oppdatert
En utdatert runbook er farligere enn ingen runbook. Se over runbooks etter hver hendelse (incident).

### 6. Bruk av Forretningshendelser (Custom Events)
Hvis problemet er knyttet til forretningslogikk (f.eks. "bruker får ikke sendt skjema"), bør runbooken inneholde spørringer som filtrerer på `customEvents`. 
Dette hjelper med å skille mellom tekniske feil (nettverk/database) og logiske feil (ugyldig data/konfigurasjon).

## Kom i gang
1. Kopier [Runbook-malen](runbook-template.md).
2. Start med de mest kritiske feilscenariene som er identifisert i monitoreringsplanen.
3. Lagre den nye runbooken i prosjektets dokumentasjonsmappe (f.eks. under `/docs/runbooks/`).
4. Lenk til runbooken fra de relevante varslene (alerts) i Azure.

## Eksempler på runbooks vi trenger for Bufdirno:
- `rb-bufdirno-cms-high-latency.md`: Feilsøking ved treghet i Optimizely.
- `rb-newsletter-api-failed-jobs.md`: Håndtering av feilede utsendelser.
- `rb-fsa-db-connection-errors.md`: Problemer med PostgreSQL-koblinger i FSA.
