# Integrasjon med ROS (Rekruttering og Oppfølging av Statlige fosterhjem)

## Innholdsfortegnelse
1. [1. Oversikt](#1-oversikt)
    - [1.1 Arkitektur: Overordnet Flyt](#11-arkitektur-overordnet-flyt)
    - [1.2 Nettverkssoner og Sikkerhet](#12-nettverkssoner-og-sikkerhet)
    - [1.3 Roller og Handlinger per Komponent](#13-roller-og-handlinger-per-komponent)
2. [2. Integrasjonsbeskrivelser](#2-integrasjonsbeskrivelser)
    - [2.1 Postnummervalidering](#21-postnummervalidering)
    - [2.2 Arrangementssynkronisering](#22-arrangementssynkronisering)
    - [2.3 Henvendelseshåndtering](#23-henvendelseshåndtering)
3. [3. Prosesser i ros](#3-prosesser-i-ros)
4. [4. Infrastruktur og Felles Konfigurasjon](#4-infrastruktur-og-felles-konfigurasjon)

Dette dokumentet beskriver hvordan løsningen er integrert med **ROS**, som er Bufetats system for håndtering av fosterhjemsdata og saksbehandling.

## 1. Oversikt
Integrasjonen fungerer som et bindeledd mellom den offentlige webportalen (Bufdir.no) og Bufetats interne systemer. Hovedmålet er å validere brukerdata og sørge for at henvendelser fra publikum havner i riktig region i `ros`.

### Funksjonalitet
Integrasjonen er delt inn i tre hovedområder:
1.  **Postnummervalidering**: `fosterhjemapi` henter og cacher det offisielle registeret fra `ros` for å validere postnummer og mappe dem til riktig kontor.
2.  **Arrangementssynkronisering**: `ros` pusher automatisk nye/endrede kurs og møter til `bufdirno`. `fosterhjemapi` kobler påmeldinger til disse via `eventGuid`.
3.  **Henvendelseshåndtering**: `fosterhjemapi` lagrer henvendelser lokalt, mens `ros` henter (puller) disse asynkront og overfører dem til sitt interne saksbehandlingssystem.

### 1.1 Arkitektur: Overordnet Flyt
Dette diagrammet viser hvordan de ulike delene av `bufdirno` (`Optimizely CMS` og `Next.js`) samhandler med integrasjons-API-et (`fosterhjemapi`) og fagsystemet (`ros`).

```mermaid
graph TD
    subgraph "Offentlig Sone (Nettleser)"
        Browser[Next.js Browser<br/>React / Client-side]
    end
    
    subgraph "Intern Sone (Portal)"
        direction TB
        NextNode[Next.js Node.js<br/>Server-side / SSR]
        Opti[Optimizely CMS<br/>Innholds- og konfigurasjons-master]
        API[fosterhjemapi<br/>Integrasjonslag / .NET]
    end
    
    subgraph "Intern Sone (Bufetat)"
        ROS[ros<br/>Fagsystem / .NET]
    end

    Browser -- "1. Fyller ut skjema" --> NextNode
    NextNode -- "2. Henter sider/config" --> Opti
    Browser -- "3. Innsending" --> API
    API -- "4. Pull/Push" --> ROS
    API -- "5. Geografidata" --> ROS

    %% Styling
    style Browser fill:#10B981,stroke:#059669,color:#fff
    style NextNode fill:#10B981,stroke:#059669,color:#fff
    style Opti fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style API fill:#F59E0B,stroke:#D97706,color:#000
    style ROS fill:#EF4444,stroke:#DC2626,color:#fff
```

### 1.2 Nettverkssoner og Sikkerhet
For å ivareta sikkerhet og kontrollert dataflyt er løsningen delt inn i tre logiske soner:

1.  **Offentlig Sone (Nettleser)**:
    *   **Innhold**: Kjører i brukerens nettleser (**Next.js Browser**). Dette er klientsiden av applikasjonen.
    *   **Sikkerhet**: Har kun tilgang til offentlig eksponerte API-endepunkter. Inneholder ingen hemmeligheter (API-nøkler). All forretningslogikk og validering skjer i de interne sonene.

2.  **Intern Sone (Portal)**:
    *   **Innhold**: 
        *   **Next.js Node.js Server**: Håndterer Server-Side Rendering (SSR) og fungerer som bindeledd mot CMS-et.
        *   **Optimizely CMS**: Administrerer innhold, sidetemplater og integrasjonsinnstillinger (som `isRecipientROS` og `requestType`).
        *   **fosterhjemapi**: Håndterer den faktiske integrasjonslogikken mot `ros` og Oslo Kommune.
    *   **Sikkerhet**: Beskyttet i Azure VNet. Kommunikasjon mellom komponentene her er skjermet fra internett. API-et fungerer som en sikkerhetsbuffer som vasker data før de sendes til `ros`.

3.  **Intern Sone (Bufetat)**:
    *   **Innhold**: Bufetats interne bedriftsnettverk med `ros`-systemet.
    *   **Sikkerhet**: Fysisk og logisk separert. Krever autorisering via API-nøkler lagret i Azure KeyVault for kommunikasjon.

### 1.3 Roller og Handlinger per Komponent

#### **bufdirno - Optimizely CMS** (Backend / .NET)
*   **Konfigurasjon**: Definerer hvilke sider som skal bruke `ros`-integrasjon via egenskaper som `isRecipientROS`.
*   **Masterdata for Web**: Lagrer metadata om kontorer (`rosId`) og arrangementer som brukes til å bygge sidene.
*   **Innholdsleveranse**: Serverer strukturerte data til `Next.js (Node.js)` via API-er.

#### **bufdirno - Next.js (Node.js)** (Server-side)
*   **SSR (Server-Side Rendering)**: Bygger den initiale HTML-en basert på data fra `Optimizely CMS`.
*   **Prop-distribusjon**: Sender nødvendig konfigurasjon (API-stier, forespørselstyper) videre til klientsiden.

#### **bufdirno - Next.js (Browser)** (Client-side / Browser)
*   **Brukergrensesnitt**: Håndterer interaksjon i skjemaer og modaler (f.eks. `PostalSearchModal`).
*   **Validering og Formatering**: Mapper brukerinput til ROS-formatet (`preparePostDataROS`) før innsending.
*   **Innsending**: Sender forespørselen direkte til `fosterhjemapi` fra nettleseren.
*   **Analyse**: Utfører hendelsessporing til Matomo etter vellykket innsending.

#### **fosterhjemapi** (Integrasjons-API / .NET)
*   **Mottak**: Validerer og persisterer alle innkommende skjemaer lokalt.
*   **Mapping**: Kobler web-data til `ros`-ID-er.
*   **Proxy/Buffer**: Tilgjengeliggjør data for `ros` og cacher geografidata.

#### **ros** (Eksternt fagsystem)
*   **Master for Geografi**: Kilde for postnummer og kontorstruktur.
*   **Asynkron Prosessering**: Henter data fra `fosterhjemapi` og utfører saksbehandling.

---

## 2. Integrasjonsbeskrivelser

### 2.1 Postnummervalidering
Denne integrasjonen sørger for at `fosterhjemapi` kun aksepterer henvendelser for geografiske områder som dekkes av `ros`, og mapper postnummer til riktig kontor og region.

### Tekniske Komponenter
*   **`RosZipCodeService`** (`fosterhjemapi` - `Infrastructure/Services/RosZipCodeService.cs`): 
    *   Henter gyldige postnummer fra `ros` via endepunktet `api/ZipCode/list` (linje 81).
    *   Implementerer caching-logikk for å sikre ytelse (linje 61-133).
*   **`ZipCodeController`** (`ros` - `ROS.Web/Api/ZipCodeController.cs`):
    *   Eksponerer det offisielle postnummerregisteret via `List()`-metoden.
*   **`InboundFormController`** (`fosterhjemapi` - `Api/Controllers/InboundFormController.cs`): 
    *   Validerer brukerens postnummer mot ROS-data i `Post`-metoden (linje 68-75).
*   **`Postal Search Modal`** (`Next.js (Browser)` - `PostalSearchModal.tsx`):
    *   Global komponent som aktiveres når brukere søker etter kontorer på forsiden. Bruker integrasjonen for å verifisere gyldighet før innsending.

### Algoritme: Caching-strategi
For å sikre lav responstid brukes en "smart" cache-strategi i `RosZipCodeService` (`fosterhjemapi`):

1.  **Be om postnummer**: En forespørsel om geografisk data mottas av `fosterhjemapi`.
2.  **Cache-oppslag**: `fosterhjemapi` sjekker om data finnes i den distribuerte cachen.
3.  **Håndtering ved tom cache**: Hvis cachen er tom, utføres et synkront API-kall til `ros`. Cachen populeres umiddelbart før data returneres til brukeren.
4.  **Sjekk av alder**: Hvis data finnes, sjekkes tidsstempelet.
5.  **Umiddelbar retur**: Hvis dataene er ferske (under 8 timer), returneres de umiddelbart.
6.  **Bakgrunnsoppdatering**: Hvis dataene er eldre enn 8 timer, returneres de eksisterende dataene umiddelbart for å unngå ventetid, men det startes samtidig en asynkron bakgrunnsoppgave (`Task.Run`) for å hente ferske data fra `ros` og oppdatere cachen for fremtidige forespørsler.

```mermaid
flowchart TD
    A[Start: Be om postnummer] --> B{Finnes i cache?}
    B -- Nei --> C[Synkront kall til ros]
    C --> D[Oppdater cache]
    D --> E[Returner data]
    B -- Ja --> F{Eldre enn 8 timer?}
    F -- Nei --> E
    F -- Ja --> G[Start asynkron bakgrunnsoppgave]
    G --> H[Hent nye data fra ros]
    H --> I[Oppdater cache]
    F -- Ja --> E

    %% Styling
    style A fill:#1D4ED8,stroke:#1E3A8A,color:#fff
    style B fill:#B45309,stroke:#78350F,color:#fff
    style C fill:#B91C1C,stroke:#7F1D1D,color:#fff
    style D fill:#0E7490,stroke:#164E63,color:#fff
    style E fill:#047857,stroke:#064E3B,color:#fff
    style F fill:#B45309,stroke:#78350F,color:#fff
    style G fill:#1D4ED8,stroke:#1E3A8A,color:#fff
    style H fill:#B91C1C,stroke:#7F1D1D,color:#fff
    style I fill:#0E7490,stroke:#164E63,color:#fff
```

### Datakontrakt: `ZipCodeDto`
Representerer geografisk informasjon fra ROS.

| Felt | Type | Beskrivelse |
| :--- | :--- | :--- |
| `ZipCode` | `string`| Postnummeret. |
| `Name` | `string`| Navn på poststed. |
| `AreaId` | `int` | ID for området i ROS. |
| `AreaName` | `string` | Navn på området/kontoret. |
| `RegionId` | `int` | ID for regionen i ROS. |
| `RegionName` | `string` | Navn på regionen. |

---

### 2.2 Arrangementssynkronisering
Denne integrasjonen håndterer flyten når brukere melder seg på kurs eller informasjonsmøter som administreres i `ros`.

### Tekniske Komponenter
*   **`InboundFormController`** (`fosterhjemapi` - `Api/Controllers/InboundFormController.cs`): 
    *   Håndterer kobling mellom web-påmelding og `ros`-arrangement via `EventGuid` (linje 82-103).
    *   Lagrer påmeldingen i den lokale databasen for senere avhenting av `ros`.
*   **`FosterhjemApiService`** (`ros` - `ROS.Application/Services/FosterhjemApiService.cs`):
    *   `EventSync()`: Pusher nye/endrede arrangementer fra `ros` til `fosterhjemapi`.
    *   `FormSync()`: Puller nye påmeldinger fra `fosterhjemapi`.
*   **`FormController`** (`fosterhjemapi` - `Api/Controllers/FormController.cs`):
    *   Tilbyr endepunktet `GET /Form/list` som `ros` bruker for å hente (pull) nye påmeldinger.
*   **`Foster Care Event Page`** (`Optimizely CMS` / `Next.js (Node.js)` / `Next.js (Browser)`):
    *   Sidetemplate for kursdetaljer (URL: `/fosterhjem/kontorer/[kontor]/meetings/[event]`).
    *   Bruker `RequestType.EventBooking` (type 5).
*   **`ContactFormHelpers.ts`** (`Next.js (Browser)`):
    *   Mapper hendelsen til Matomo-analyse for kurspåmelding via `passEventToAnalytics` (linje 8).

### Datakontrakt: `EventDto`
Representerer et arrangement hentet fra `ros`.

| Felt | Type | Beskrivelse |
| :--- | :--- | :--- |
| `ExternalId` | `int?` | Intern numerisk ID i `ros`. |
| `ExternalGuid` | `Guid` | Global unik ID brukt for mapping mot web. |
| `Title` | `string` | Tittel på arrangementet. |
| `Type` | `string` | Kategorisering (f.eks. "Kurs"). |
| `FromDate` | `DateTime` | Starttidspunkt. |
| `ToDate` | `DateTime` | Sluttidspunkt. |
| `Location` | `string` | Oppmøtested eller digital lenke. |
| `Areas` | `List<AreaDto>` | Liste over kontorer knyttet til arrangementet. |

#### Underkontrakt: `AreaDto`
Brukt i `EventDto` for å spesifisere deltakende kontorer.

| Felt | Type | Beskrivelse |
| :--- | :--- | :--- |
| `ExternalId` | `int` | ID for kontoret i `ros`. |
| `Name` | `string` | Navn på kontoret. |
| `Organizer` | `bool` | Markerer om kontoret er hovedarrangør. |

### Algoritme: Arrangementssynkronisering (Frontend)
Denne algoritmen i `Next.js (Browser)` avgjør datakontrakt og ruting før API-kall, samt sporing av konverteringer for kurs og møter:

1.  **Innsending**: Brukeren fyller ut skjemaet og klikker på send-knappen.
2.  **Valg av kontrakt**: `ContactForm` sjekker `isRecipientROS`-flagget (levert av `Optimizely CMS` via `Next.js (Node.js)`).
3.  **Datapreparering**: Hvis mottakeren er `ros`, kalles `preparePostDataROS` for å formatere dataene korrekt (inkludert mapping av `eventGuid`).
4.  **API-kall**: Dataene sendes til `fosterhjemapi` via `POST /InboundForm`.
5.  **Analyse**: Etter at svaret er mottatt fra `fosterhjemapi`, kalles `passEventToAnalytics`.
6.  **Konverteringssporing**: Hvis det er en kurspåmelding (`requestType` 5), sendes en spesifikk hendelse til Matomo med detaljer om arrangementet.
7.  **Tilbakemelding**: Brukeren får se en bekreftelse på at påmeldingen er sendt.

```mermaid
sequenceDiagram
    autonumber
    
    participant U as Bruker
    participant CF as ContactForm
    participant CH as ContactFormHelpers
    participant API as fosterhjemapi

    box "Bruker"
        participant U
    end
    box "Frontend"
        participant CF
        participant CH
    end
    box "Backend API"
        participant API
    end

    rect rgb(243, 244, 246)
        Note over U, CF: Bruker sender påmelding
        U->>+CF: Klikk Send
        CF->>CF: Sjekk isRecipientROS
    end
    
    rect rgb(236, 253, 245)
        alt isRecipientROS == true
            CF->>+CH: preparePostDataROS()
            CH-->>-CF: PostDataROS
        else isRecipientROS == false
            CF->>CF: Map til PostDataBufdir
        end
    end
    
    rect rgb(255, 251, 235)
        CF->>+API: POST /InboundForm
        API-->>-CF: 200 OK / Error
    end
    
    rect rgb(236, 253, 245)
        Note over CF, CH: Analyse av kurspåmelding
        CF->>CH: passEventToAnalytics()
        CF-->>-U: Vis suksess/feilmelding
    end
```

### Algoritme: Arrangementssynkronisering (Backend)
Når en påmelding mottas i `InboundFormController` (`fosterhjemapi`), mappes `EventGuid` til `ros` sin interne ID, og påmeldingen lagres i databasen. `ros` henter deretter ut påmeldingene asynkront:

1.  **Motta påmelding**: `fosterhjemapi` mottar påmeldingsdata med en `EventGuid`.
2.  **Oppslag av arrangement**: `EventService` gjør et oppslag i den lokale databasen for å finne arrangementet.
3.  **Hente ROS-ID**: Systemet henter `ExternalId` (`ros` sin interne ID) som er knyttet til arrangementets `Guid`.
4.  **Persistering**: Påmeldingen lagres i den lokale databasen med status `Pending`.
5.  **Kvittering**: Brukeren får en umiddelbar bekreftelse (`200 OK`).
6.  **Polling**: `ros` poller periodisk `GET /Form/list` endepunktet.
7.  **Datautveksling**: `FormController` returnerer alle nye påmeldinger, og markerer dem som `InTransit`.

```mermaid
sequenceDiagram
    autonumber
    
    participant C as InboundFormController
    participant E as EventService
    participant DB as SQL Database
    participant FC as FormController
    participant R as ros
    
    box "Backend API"
        participant C
        participant E
        participant FC
    end
    box "Data & Cache"
        participant DB
    end
    box "Eksternt System"
        participant R
    end

    C->>+E: GetByExternalGuid(eventGuid)
    E->>+DB: Finn arrangement i lokal database
    DB-->>-E: EventModel (med ExternalId)
    E-->>-C: EventModel
    
    rect rgb(236, 254, 255)
        Note over C, DB: Lagring av påmelding
        C->>C: Sett EventId = ExternalId
        C->>+DB: Lagre påmelding lokalt
        DB-->>-C: OK (Returnerer til bruker)
    end

    rect rgb(254, 242, 242)
        Note over R, FC: ros henter data
        R->>+FC: GET /Form/list
        FC->>+DB: Hent nye påmeldinger
        DB-->>-FC: Liste med påmeldinger
        FC-->>-R: JSON Data
    end
```

---

### 2.3 Henvendelseshåndtering
Dette er den mest omfattende integrasjonen som automatiserer innsending av kontaktforespørsler direkte til Bufetats saksbehandlere.

### Tekniske Komponenter
*   **`InboundFormController`** (`fosterhjemapi`): Mottar skjemadata, validerer postnummer og lagrer henvendelsen lokalt.
*   **`FormController`** (`fosterhjemapi`): Tilbyr endepunkt for at `ros` kan hente nye henvendelser.
*   **`FosterhjemApiService`** (`ros`): Håndterer periodisk avhenting (`FormSync`) og oppdatering av status.
*   **`FormRequestService`** (`ros` - `ROS.Application/Services/FormRequestService.cs`): Lagrer henvendelsen i ROS-databasen via `SaveForm()`.
*   **`ContactForm.tsx`** (`Next.js (Browser)`): Håndterer logikken for å skille mellom `ros` og andre mottakere (linje 227).
*   **`ContactFormHelpers.ts`** (`Next.js (Browser)`): Formaterer data til ROS-spesifikt format i `preparePostDataROS` (linje 45).
*   **Sider** (`Optimizely CMS`): Brukes på `Foster Care Office Page` og `Local Office Contact Page`.

### Algoritme: Henvendelseshåndtering (Backend)
Hovedflyten i `fosterhjemapi` ved mottak av henvendelse og hvordan `ros` henter disse asynkront:

1.  **Motta henvendelse**: `InboundFormController` (`fosterhjemapi`) mottar skjemaet fra `Next.js (Browser)`.
2.  **Validere postnummer**: Postnummeret sjekkes mot listen over gyldige ROS-postnummer fra `RosZipCodeService`.
3.  **Avvisning ved feil**: Hvis postnummeret ikke finnes i `ros`-systemet, returneres `400 Bad Request`.
4.  **Lagring**: Ved gyldig postnummer lagres henvendelsen i den lokale SQL-databasen.
5.  **Bekreftelse**: En suksessmelding returneres til brukeren.
6.  **Avhenting**: `ros` poller `GET /Form/list` for å hente nye henvendelser og overføre dem til sitt eget saksbehandlingssystem.

```mermaid
sequenceDiagram
    autonumber
    
    participant F as Next.js (Browser)
    participant C as InboundFormController
    participant Z as RosZipCodeService
    participant DB as SQL Database
    participant FC as FormController
    participant R as ros
    
    box "Frontend"
        participant F
    end
    box "Backend API"
        participant C
        participant FC
    end
    box "Data & Cache"
        participant Z
        participant DB
    end
    box "Eksternt System"
        participant R
    end

    F->>+C: POST /InboundForm
    
    rect rgb(236, 254, 255)
        Note over C, Z: Postnummervalidering
        C->>+Z: GetAllZipCodes()
        Z-->>-C: Gyldig/Ugyldig
    end
    
    alt Gyldig
        rect rgb(236, 254, 255)
            C->>+DB: Lagre i lokal DB
            DB-->>-C: OK
        end
        C-->>F: 200 OK (Suksessmelding til bruker)

        rect rgb(254, 242, 242)
            Note over R, FC: ros henter data
            R->>+FC: GET /Form/list
            FC->>+DB: Hent skjemaer
            DB-->>-FC: Liste
            FC-->>-R: Data
        end
    else Ugyldig
        C-->>F: 400 Bad Request
    end
```

### 3. Prosesser i ros

Dette kapittelet beskriver hvordan integrasjonen håndteres på `ros`-siden av løsningen (kildekode i `Ros/ros-next`).

### 3.1 FosterhjemApiService
Denne tjenesten (`ros` - `ROS.Application/Services/FosterhjemApiService.cs`) er motoren i integrasjonen på `ros`-siden og kjører asynkrone bakgrunnsjobber for synkronisering.

*   **EventSync**: Identifiserer nye eller endrede arrangementer i `ros`-databasen og sender dem samlet til `fosterhjemapi` via `POST /Event/list`. Dette sikrer at portalen alltid har oppdatert informasjon om kurs og møter.
*   **FormSync**: Poller `fosterhjemapi` (`GET /form/list`) for nye henvendelser og påmeldinger. Etter behandling sender den en kvittering tilbake (`PATCH /form`) med status for hver enkelt form (f.eks. `Sucess`, `Rejected`, `Failed`).

### 3.2 Håndtering av Henvendelser (SaveForm)
Når `ros` mottar en henvendelse via `FormSync`, behandles den av `FormRequestService.cs` før den lagres permanent i `ros`-databasen:

1.  **Duplikatkontroll**: Sjekker om `FormGuid` allerede eksisterer i tabellen `FormRequests` for å unngå dobbeltlagring.
2.  **Geografisk Mapping**: Bruker internt postnummerregister for å finne tilhørende `AreaId` (kontor) og `RegionId` basert på postnummeret i henvendelsen.
3.  **Opprettelse av FormRequest**: Dataene fra portalen mappes til `ros` sin interne domenemodell `FormRequest`.
4.  **Tilgjengeliggjøring**: Henvendelsen blir umiddelbart synlig for saksbehandlere i `ros`-grensesnittet under det aktuelle kontorets oversikt.

### 3.3 Geografiske Data og API-er
`ros` fungerer som "master" for geografisk ruting og Bufetats organisasjonsstruktur:

*   **ZipCodeController**: Eksponerer `api/ZipCode/list`. Dette er kilden `RosZipCodeService` i `fosterhjemapi` bruker for å validere postnummer.
*   **AreaController**: Eksponerer `api/Area/list`. Brukes for å hente oversikt over områder/kontorer og hvilken region de tilhører.

---

### 4. Infrastruktur og Felles Konfigurasjon
Dette er de underliggende komponentene som støtter alle integrasjonsområdene.

### Sentrale Datakontrakter (DTO-er)

#### Datakontrakt: `InboundFormDto`
Denne kontrakten definerer dataene som sendes fra `Next.js (Browser)` til `fosterhjemapi`.

| Felt | Type | Beskrivelse |
| :--- | :--- | :--- |
| `EventGuid` | `Guid?` | Unik ID for arrangementet (påkrevd ved arrangementspåmelding). |
| `PostNumber` | `string` | Brukerens postnummer for ruting til riktig region/kontor. |
| `Name` | `string` | Fullt navn på innsender. |
| `Phone` | `string` | Telefonnummer. |
| `Email` | `string` | E-postadresse. |
| `Type` | `FormType` | Type henvendelse (f.eks. `EventBooking` eller `ContactMe`). |

#### Datakontrakt: `PostDataROS`
Formatert objekt som brukes i `Next.js (Browser)` før innsending til `fosterhjemapi`.

| Felt | Type | Beskrivelse |
| :--- | :--- | :--- |
| `eventGuid` | `string` | Valgfri kobling til et spesifikt arrangement. |
| `type` | `number` | ROS-spesifikk numerisk forespørselstype (f.eks. 4 eller 5). |
| `name` | `string` | Navn på innsender. |
| `email` | `string` | E-postadresse. |
| `phone` | `string` | Telefonnummer. |
| `zipCode` | `string` | Postnummer brukt for geografisk ruting. |

### Tilkobling og Sikkerhet
*   **Oppsett av tilkobling**: 
    *   **`StartupExtensions.cs`**: Konfigurerer `HttpClient` i `fosterhjemapi` med `BaseAddress` og `X-Api-Key` (linje 26-32).
    *   **`HttpClients.cs`**: Definerer navnet `RosHttpClient`.
*   **Geografi-data**: `RosService` (`fosterhjemapi`) henter felles lister over områder og regioner fra `ros` via `api/Area/list` (linje 42).
*   **Sikkerhet**: Tilgangen styres via API-nøkler administrert i Azure KeyVault og base-URL konfigurasjon (`RosApiBaseUrl`).
*   **Arkitektur**: I det overordnede [arkitekturdiagrammet](architecture.md) er `ros` definert som en **External Service** som `fosterhjemapi` kommuniserer med.
