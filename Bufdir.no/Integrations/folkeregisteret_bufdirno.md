# Integrasjon med Folkeregisteret (Freg)

Bufdir har flere tjenester som integrerer med Folkeregisteret (Freg) via Skatteetatens API-er. Integrasjonene bruker Maskinporten for autentisering og autorisasjon.

## Oversikt over integrasjoner

Det er hovedsakelig to ulike scopes og API-endepunkter som benyttes avhengig av tjenestens behov for data:

1. **Offentlig uten hjemmel**: Brukes for å hente grunnleggende informasjon som navn.
2. **Offentlig med hjemmel**: Brukes for å hente mer detaljert informasjon, som familierelasjoner og foreldreansvar.

---

## 1. Utrapporteringsbank

Denne tjenesten bruker Folkeregisteret for å slå opp navn på personer basert på fødselsnummer (PID).

- **Funksjonell gevinst**: Automatiserer utfylling av navn, noe som reduserer manuelle feil ved inntasting og forbedrer datakvaliteten i rapportene. Det gir også en bedre brukeropplevelse ved at brukeren slipper å skrive inn informasjon systemet allerede har tilgang til.
- **Data som brukes**:
    - `navn`: Henter gjeldende fornavn, mellomnavn og etternavn.
- **Hva dataene brukes til**:
    - Verifisere identiteten til personen som rapporterer eller blir rapportert.
    - Vise korrekt navn i brukergrensesnittet og i genererte rapporter.
- **API-type**: Offentlig uten hjemmel
- **Maskinporten-scope**: `folkeregister:deling/offentligutenhjemmel`
- **Kildekode**: `utrapporteringsbank/src/utils/freg/`

---

## 2. Foreldreansvarsavtale (FSA)

FSA-tjenesten har en mer omfattende integrasjon da den har behov for å vite hvem som har foreldreansvar for barn.

- **Funksjonell gevinst**: Sikrer at avtaler om foreldreansvar kun opprettes av personer som faktisk har foreldreansvar ifølge lovverket. Dette automatiserer en ellers tidkrevende og feilutsatt manuell kontrollprosess, forhindrer svindel, og sikrer at barnas rettigheter blir ivaretatt ved at riktige parter inkluderes i avtalen.
- **Data som brukes**:
    - `person-basis`: Grunnleggende personinformasjon.
    - `familierelasjon`: Oversikt over relasjoner (barn, foreldre).
    - `foreldreansvar`: Juridisk status for hvem som har foreldreansvar for et gitt barn.
    - `relasjon-utvidet`: Brukes for å kartlegge komplekse familierelasjoner.
- **Hva dataene brukes til**:
    - Identifisere hvilke barn en innlogget bruker har foreldreansvar for.
    - Hente informasjon om den andre forelderen som skal være part i avtalen.
    - Validere at brukeren har rettslig grunnlag for å starte en avtaleprosess for et spesifikt barn.
- **API-type**: Offentlig med hjemmel
- **Maskinporten-scope**: `folkeregister:deling/offentligmedhjemmel`
- **Kildekode**: `bufdirno-fsa/FSA.Business/Services/NationalPopulationRegisterService.cs`
- **API-endepunkt (Produksjon)**: `https://folkeregisteret.api.skatteetaten.no/folkeregisteret/offentlig-med-hjemmel/api`

---

## Teknisk implementering

### Autentisering
Alle kall mot Folkeregisteret autentiseres ved hjelp av JWT-tokens fra Maskinporten. Bufdir opptrer som konsument og må ha tildelt tilgang til de aktuelle scopene fra Skatteetaten.

### Miljøer
Integrasjonene er konfigurert for ulike miljøer (Test/QA/Prod) via `appsettings.json` i de respektive prosjektene.

- **Test/SITS**: `https://folkeregisteret-api-konsument.sits.no`
- **Produksjon**: `https://folkeregisteret.api.skatteetaten.no`
