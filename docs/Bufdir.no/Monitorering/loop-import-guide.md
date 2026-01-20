# Veiledning for import til Microsoft Loop

Dette dokumentet forklarer hvordan du flytter monitoreringsdokumentasjonen fra disse modulene over til [Microsoft Loop](https://loop.cloud.microsoft).

## Metoder for import

Microsoft Loop støtter import av innhold på flere måter. Siden dokumentasjonen her består av Markdown-filer, anbefales følgende fremgangsmåte:

### 1. Opprette sider fra Markdown (Anbefalt)
Loop har nylig forbedret støtten for Markdown. Du kan i mange tilfeller lime inn Markdown-innhold direkte, og Loop vil formatere det automatisk.

1.  Åpne den relevante `.md`-filen i en teksteditor (f.eks. VS Code).
2.  Marker all tekst (`Ctrl+A`) og kopier den (`Ctrl+C`).
3.  Gå til din Workspace i Microsoft Loop.
4.  Opprett en ny side.
5.  Lim inn teksten (`Ctrl+V`). Loop vil gjenkjenne overskrifter, lister og kodeblokker.

### 2. Bruke "Paste as" funksjonalitet
Hvis du limer inn og formateringen ikke ser riktig ut, kan du prøve å høyreklikke og se etter alternativer for å lime inn som formatert tekst.

### 3. Struktur i Loop
For å beholde sammenhengen mellom dokumentene, anbefales det å bygge opp strukturen i Loop slik:

*   **Hovedside:** Monitorering (Innholdet fra `monitoring.md`)
    *   **Underside:** bufdirno - Hovedportal (`bufdirno-monitoring.md`)
    *   **Underside:** bufdirno-fsa - FSA (`bufdirno-fsa-monitoring.md`)
    *   **Underside:** API-er (Egen side eller undersider for `familievern-api`, `fosterhjem-api`, `newsletter-api`)
    *   **Underside:** stat-system - Statistikksystem (`stat-system-monitoring.md`)
    *   **Underside:** Utrapporteringsbank (`utrapporteringsbank-monitoring.md`)
    *   **Underside:** Runbooks (Innholdet fra `runbook/`-mappen)
        *   Mal for runbooks
        *   Veiledning for runbooks
        *   Teknisk oppsett i Azure

## Viktige justeringer etter import

Etter at innholdet er limt inn i Loop, bør du sjekke følgende:

1.  **Interne lenker:** Relative lenker som `[hovedplanen](./monitoring.md)` vil ikke fungere i Loop. Du bør erstatte disse med interne lenker mellom Loop-sidene (bruk `@`-symbolet i Loop for å lenke til andre sider).
2.  **Kodeblokker:** Verifiser at syntaksutheving (C#, TypeScript, Bash) ser riktig ut i Loops kodeblokker.
3.  **Bilder:** Hvis dokumentene hadde inneholdt bilder med relative stier, måtte disse lastes opp manuelt til Loop.

## Hvorfor Loop?
Ved å ha dokumentasjonen i Loop oppnår teamet:
*   **Sanntids-samhandling:** Flere kan redigere monitoreringsrutiner samtidig.
*   **Loop Components:** Du kan dele spesifikke sjekklister (f.eks. fra en runbook) direkte inn i Microsoft Teams-chatter under en hendelse.
*   **Tilgjengelighet:** Dokumentasjonen er lett tilgjengelig for alle i organisasjonen uten behov for tilgang til kildekoden.
