# Offentlig eksponering av interne API-ruter

Dette dokumentet beskriver identifiserte sårbarheter knyttet til utilsiktet offentlig eksponering av API-endepunkter i Bufdir-løsningen.

## 🚨 Kritiske funn

### 1. Utrapporteringsbank (`/api/reports`)
Endepunktet `utrapporteringsbank/src/app/api/reports/route.ts` (Next.js API route) mangler for øyeblikket en autentiseringssjekk på server-siden.

*   **Sårbarhet:** Selv om frontenden kan kreve innlogging, kan selve API-endepunktet kalles direkte av hvem som helst med en `POST`-forespørsel for å hente ut rapportdata.
*   **Risiko:** Potensiell lekkasje av alle data i utrapporteringsbanken.
*   **Anbefalt tiltak:** Legg til en sjekk med `getServerSession(authConfig)` i starten av `POST`-metoden i `route.ts`.

### 2. Strapi API Forwarding (`/api/stat-api-forwarding`)
I `stat-content-strapi5` finnes det en videresendings-mekanisme som sender forespørsler videre til `stat-backend`.

*   **Sårbarhet:** Tjenesten støtter operasjoner som `DELETE` og `POST` (upload). Siden Strapi bruker sin egen `AuthTokenService` for å autentisere seg mot backenden, vil en forespørsel til Strapi-endepunktet bli utført med backenden sine rettigheter.
*   **Risiko:** Hvis ruten i Strapi er satt til "Public" i Strapi-administratoren, kan eksterne brukere i praksis slette eller endre data i statistikk-backenden uten å ha egne rettigheter.
*   **Anbefalt tiltak:** Sikre at denne ruten krever en autentisert sesjon i Strapi og kun er tilgjengelig for autoriserte redaktører (bruke Strapi policies eller sjekke `ctx.state.user`).

### 3. Excel-import i Familievern-API (`/api/ExcelImport`)
Kontrolleren `ExcelImportController` i `bufdirno-familievern-api` mangler eksplisitte autentiseringsattributter.

*   **Sårbarhet:** Ruten er avhengig av det globale flagget `RequireAuthentication` i `Program.cs`. Hvis dette flagget er `false`, er endepunktet åpent for alle.
*   **Risiko:** En angriper kan laste opp vilkårlige Excel-filer som potensielt kan overskrive kontordata (`IOfficeRepository.Update`) eller føre til tjenestenekt (DoS) gjennom store filer.
*   **Anbefalt tiltak:** Legg til `[Authorize]` på klasse-nivå i `ExcelImportController.cs` for å sikre "defense in depth", uavhengig av globale innstillinger.

---

## ⚠️ Andre observasjoner

### MunStat i Statistikk-API (`stat-backend`)
Kontrollerne i `MunStat` (f.eks. `IndicatorDataController`, `GeoClassificationController`) har flere åpne `GET`-ruter.

*   **Status:** Mens `POST`, `PATCH` og `DELETE` er beskyttet med `[Authorize]`, er datahenting (`GET`) offentlig tilgjengelig. Dette er sannsynligvis tilsiktet for statistikk-formål, men bør overvåkes for uventet bruk av ressurser.

### Konfigurerbar autentisering (`RequireAuthentication`)
Flere API-er (`bufdirno-newsletter-api`, `bufdirno-fosterhjem-api`, `familievern-api`) bruker et konfigurasjonsflagg for å styre om autentisering er påkrevd.

*   **Risiko:** Hvis dette flagget ved en feil settes til `false` i et produksjonsmiljø (f.eks. via miljøvariabler), vil hele API-et være åpent.
*   **Tiltak:** Det brukes en `HideInternalResourcesControllerConvention` for å skjule visse interne ressurser i disse API-ene, men dette gir kun begrenset beskyttelse ("security by obscurity") hvis hovedautentiseringen er deaktivert.

### Statistikk-API (`stat-backend`)
Dokumentasjonen beskriver dette som et "offentlig tilgjengelig API".

*   **Status:** Mange `GET`-ruter er åpne for offentligheten (som forventet for statistikk), mens slette- og opplastingsoperasjoner er beskyttet. Den største risikoen her er omgåelse via Strapi sin videresending, som beskrevet i punkt 2. Se også punktet om MunStat over.

---

## ✅ Godt sikrede områder

*   **FSA Backend (`bufdirno-fsa`):** Har implementert en global `FallbackPolicy` som krever autentisert bruker på alle ruter som standard.
*   **Feedback API (`bufdirno-feedback-api`):** Bruker Azure Function-autentisering (`Function`-nivå) som krever API-nøkkel.
