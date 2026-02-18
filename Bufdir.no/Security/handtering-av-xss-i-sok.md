# Håndtering av XSS-sårbarhet i søkefunksjon

Denne dokumentasjonen beskriver hvordan man skal håndtere og utbedre XSS-sårbarheten (Cross-Site Scripting) som er identifisert under penetrasjonstesting av søkefunksjonen på `qa.bufdir.no`.

## 1. Problemstilling
Under pentest av QA-miljøet ble det avdekket en XSS-sårbarhet i søkefunksjonen. Dette skyldes at brukerinput (søketermer) i visse tilfeller reflekteres på siden uten tilstrekkelig koding eller sanitering, noe som gjør det mulig for en angriper å injisere ondsinnet skriptkode.

## 2. Anbefalte tiltak

For å lukke sårbarheten raskt og oppnå NSM-compliance (Nasjonal sikkerhetsmyndighet), anbefales følgende lavkost-tiltak:

### A. HTML-escaping og sanitering (Frontend)
Hovedforsvaret mot XSS er å sørge for at all data fra brukeren blir behandlet som tekst, ikke som kjørbar kode.

*   **Filstier:**
    *   `bufdirno/src/NextJs/src/components/search/SearchResults.tsx`
    *   `bufdirno/src/NextJs/src/components/search/Search.tsx`

*   **Standard koding:** Bruk alltid standard React-rendring for søketermer (f.eks. `{query}`). React sørger automatisk for HTML-escaping av alle verdier.
    *   **Eksempel fra `SearchResults.tsx` (linje 36):**
        ```tsx
        {searchResources?.HitsOn} {`"${query}"`}
        ```

*   **Sanitering ved behov:** Hvis man må rendre brukerinput som en del av en HTML-streng (f.eks. via `dangerouslySetInnerHTML`), må verdien alltid saneres først.
    *   **Bibliotek:** Bruk `isomorphic-dompurify`.
    *   **Eksempel fra `SearchResults.tsx` (linje 24):**
        ```tsx
        // SIKKER RENDERING VED INGEN TREFF:
        <InfoBox
          header={searchResources?.NoHits}
          richText={'"' + DOMPurify.sanitize(query) + '"'}
          state="warning"
        />
        ```
*   **Kontroll:** Gå gjennom alle komponenter som håndterer søkeresultater og verifiser at ingen verdier fra URL-parametere eller API-responser rendres uten koding/sanitering.

### B. Strengere Content Security Policy (CSP)
En streng CSP fungerer som et ekstra sikkerhetslag som kan stoppe skriptkjøring selv om en sårbarhet skulle eksistere i koden.

*   **Konfigurasjonsfil:** `bufdirno/src/NextJs/next.config.js` (linje 22-38)
*   **Innstramminger:**
    1.  **Fjern `unsafe-inline`:** Dette er det viktigste tiltaket for å stoppe Reflected XSS. Det krever at alle skript ligger i egne filer eller er merket med en sikkerhets-nonce.
        *   *Merk:* `bufdirno/src/NextJs/src/app/layout.tsx` (linje 48 og 53) bruker i dag `dangerouslySetInnerHTML` for inline-skript, som må flyttes til eksterne filer eller få nonces.
    2.  **Fjern `unsafe-eval`:** Hindrer bruk av `eval()` og lignende usikre funksjoner.
    3.  **Stram inn domener:** Sørg for at `script-src` og `connect-src` kun tillater eksplisitte, betrodde domener.
    4.  **Behold `object-src 'none'`:** Hindrer lasting av utdaterte og usikre plugins som Flash.

## 3. Implementeringsplan

1.  **Revisjon av kode:** Sjekk alle steder i Next.js-frontend der `query` (søketermen) brukes.
2.  **Oppdatering av CSP:** Juster `cspHeader` i `next.config.js` for å fjerne `unsafe-inline` der det er teknisk mulig, eller innfør nonces.
3.  **Testing på QA:**
    *   Utfør søk med "skadelige" strenger som `<script>alert('XSS')</script>`.
    *   Verifiser at skriptet ikke kjører, og at CSP-headeren blokkerer eventuelle forsøk på uautorisert skriptkjøring.
4.  **Fullfør NSM-compliance:** Dokumenter endringene som en del av sikkerhetsarbeidet for løsningen.

---
**Status:** Tiltakene er lavkost, raske å implementere og vil fullføre kravene til NSM-compliance for dette punktet.
