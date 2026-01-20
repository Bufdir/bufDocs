# Mal for Runbooks i Bufdirno

Dette dokumentet fungerer som en standardmal for runbooks (feilsøkingsveiledninger) i Bufdir-prosjektene. En god runbook skal være kortfattet, handlingsorientert og lett å følge under press.

---

# [Tittel: f.eks. Gjenoppretting ved databasefeil i bufdirno]

## 1. Oversikt
- **Tjeneste:** [Navn på tjeneste, f.eks. Optimizely CMS]
- **Alvorlighetsgrad:** [Kritisk/Høy/Middels]
- **Beskrivelse:** Kort forklaring på hva problemet er og hvordan det manifesterer seg (f.eks. "Brukere får 500-feil ved forsøk på å laste nettsiden").

## 2. Identifisering (Slik bekrefter du feilen)
- **Metrikker/Grafer:** [Lenke til Azure Dashboard eller Application Insights-spørring]
- **Loggsøk:** [Spørring i Log Analytics for å bekrefte feilen]
  ```kusto
  exceptions
  | where timestamp > ago(1h)
  | where problemId == "SpecificErrorId"
  ```

## 3. Umiddelbare tiltak (Quick Fixes)
 - Sjekk om tjenesten kan startes på nytt (Restart Web App).
 - Sjekk Azure Service Health for generelle Azure-problemer.
 - [Annet spesifikt tiltak]

## 4. Feilsøkingssteg
1. **Sjekk databaseforbindelse:** Forsøk å koble til via Query Editor i Azure Portal.
2. **Sjekk ressursbruk:** Er CPU eller minne på 100%?
3. **Sjekk siste deploy:** Ble det rullet ut ny kode rett før feilen startet?

## 5. Gjenoppretting
- **Steg 1:** [Beskriv steg for å fikse, f.eks. skalere opp databasen]
- **Steg 2:** [Beskriv steg for å verifisere, f.eks. kjør en test-spørring]

## 6. Eskalering
Hvis problemet ikke er løst innen [X] minutter, kontakt:
- **Teknisk ansvarlig:** [Navn/Rolle]
- **Infrastruktur-team:** [Kontaktinfo]
- **Tredjepart:** [f.eks. Optimizely Support]

## 7. Etterarbeid
- Opprett en post-mortem rapport.
- Oppdater denne runbooken dersom prosedyren må forbedres.
