# RSC status på komponenter i Bufdir-next

Per 16.02.24

## Breadcrumbs

RSC

## CallToAction

RSC

## Carousel

CC Dette er en wrapper rundt BlCarousel/BlResponsiveImage Wrapperen er CC, men
trenger nok ikke være det

## ChildServicesInstitutionCard

RSC (men blir til CC via Result, som ikke trenger å være CC)

## child-services > Filter

CC og må være det, fordi state må holdes gjennom hele løpet.

## child-services > Results

CC Denne er CC, men kan nok blir RSC ved å gjøre knappen som er der om til en
CC, og la resten være RSC

## ChildServicesInstitutionList

RSC Ser ikke ut til å være i bruk. Skal nok inn via noen manglende maler?

## ContactForm

CC Har masse interaksjon og state, så må være det

Se på om vi skal refaktorere det som bruker ContactForm, og splitte den ut av
det som bruker det

- EventSignup
- PostalSearchModal

## ContentTeaser

RSC

## CookieSettings

CC Er CC pga at Footer er parent, men er ikke markert med "use client". Burde
bli det

## EventList

RSC Blir CC når den blir brukt i OfficeEventOverview, PostalSearchHandler og
PostalSearchModal

## EventListTile

RSC Blir kun brukt i Components.tsx

## EventSignup

CC Knapp og modal kunne flyttes til egen komponent som er CC, mens resten kan
være RSC

## Feedback

CC Må være det pga skjema og ting som skjer runtime

## FilterDropdown

CC Må være det for alt skjer runtime i den Note: `updateUrlParameters`,
`getDefaultOptionIds` og `overridePropDefaultsWithUrlDefaults` kan kanskje
skrives om til å bruke next router?

## Footer

CC. Er CC kun pga knapp for å åpne og `CookieSettings` og pga `CookieSettings`.
Kanskje splitte disse ut og gjøre `Footer` til RSC

## Header

CC Kunne ha splitta ut det som er i megamenyen og åpnet for å dytte det inn som
`children` til `Header` i `Layout` Note: `Localizations` komponenten ligger i
`Header` sin mappe, men blir brukt kun i `Layout`. Kanskje flytte denne?

## Hero

RSC Blir bare brukt i page templates, som også er RSC

## Icon\*

RSC 7 stk

## InfoBox

RSC Blir brukt i `SearchResults`, som er CC Ellers brukt i ting som er RSC

## LinkList

CC Er CC pga client side pagination som viser flere ved klikk Kan vurdere om vi
skal ha `LinkList` som er statisk, `LinkListClientPagination` som er CC og
`LinkListPagination` som er CC. Se om `LinkList` er mye i bruk uten pagination,
i så fall lag en egen for disse.

Komponenter som bruker LinkList som ikke bruker pagination

- OfficeLinkList
- ParentSupportedmeasureList

## LinkListPagination

CC Er CC fordi den må reagere på at links propen endrer seg i en `useEffect`.

## Loader

CC SVG only

## LogoBufdir

CC SVG only

## LogoBufdirPride

CC SVG only

## LogoBufetat

CC SVG only

## MediaFlowVideo

CC Må være CC pga script som loades runtime

## NewsLetter

CC Må være det pga skjema med validering

## NoticeBlock

RSC Blir kun brukt i page templates Er bare en wrapper rundt InfoBox, kunne
kanskje brukt InfoBox direkte heller

## OfficeLinkList

RSC Statisk liste med lenker, men bruker LinkList som er CC (LinkList hadde ikke
trengt å være CC her pga ingen pagination)

## OfficeEventOverview

CC, men kan skrives om til RSC. Eneste som er brukt av hooks er for å gjøre 2
fetch kall. Husk å buste cashen i et gitt intervall for disse kallene i RSC

## OnlineLibrary

CC Må nok være det siden ingenting synes (nesten) før man har trigget et søk
client side

## OptimizelyCommunicationScript

CC Må være det fordi den kjører et script client side

## ParentSupportMeasureOverview

Utkommenter - spør Paal, kan nok slettes. Paal har laget ny page template Mappa
inneholder en MainBody som kun sender html til dangerouslySetInnerHTML - her
burde vi nok fjerne denne, og bruke RichText (eller kanskje XHtmlstring, fordi
det er et content area sin verdi som sendes inn til Mainbody) direkte

#delete

## PostalSearchHandler

CC Må sannsynligvis være CC pga søk/filtrering som trigger henting av diverse
lenkelister

## PostalSearchModal

CC Må kanskje være CC pga isOpen state + fetchData som skjer basert på
postnr-søk

## PostalSearchRoute

CC Må være CC fordi den kun inneholder søk (ServiceSearch) som sender deg til ny
side runtime. Note: bruker `window.location.href`, men burde bruke noe NextJs
router ting her

## PostalSearchRouteZero

RSC Er ikke i bruk, kan nok fjernes

## PrintButtonLink

CC hadde nok ikke trengt å være det er en `<a>` tag, burde være `<Link>`
component, med to wrapper divvs og et icon

## Recaptcha

Ikke markert som CC, men burde kanskje være det? brukes kun i Feedback, som er
CC

## ResponsiveImage

RSC Bruker credit og caption fra `<BlResponsiveImage>` og sender bildet videre
til NextJs sin `<Image>` komponent.

## RichText

RSC Parser rå html til jsx

## Search

CC Burde bruke ServiceSearch?

## ServiceSearch

Kun PostalSearchHandler som bruker filterSettings, så kanskje splitte
FilterDropdowns ut av ServiceSearch og bruke direkte i PostalSearchHandler? (Må
refaktorere slik at dem kan være på linje uten å være i samme komponent)

## StatApp

RSC Men egentlig ikke fordi vi bruker `hydrateRoot` for å sette inn
`bufdir_stat` Ikke i bruk, `bufdir_stat` lastes direkte inn i egen page template

#delete

## StatBreadCrumbs

CC Bruker `window.addEventListener` for å kommunisere med `bufdir_stat` Mounted
i `TemplateWrapper` hvis `isStat`

## Survey

CC Alternativ1: Kunne ha laget `SurverQuestions` som egen page med dynamisk
route `id` Alternativ2: kunne kommunisert `mostReccuring` fra `SurverQuestions`
via callback prop opp til `Survey` og kjørt `finishTest` der. Uansett:
`finishTest` burde brukt `useRouter` i stedet for `window.location.href`

## TableOfContentGuideline

CC Kunne nok fått inn `MenuInfo` og `MenuItems` som children/props i `Guideline`
page templaten, slik at de kunne vært RSC. De er direkte importert i
`TableContentMenu` i dag

## TransportLink

RSC Bruker `Link` fra NextJs

## ValidationMessage

RSC Gjenskaper `BlValidation`, ser ikke ut til å være i bruk

#delete

## XHtmlString

RSC

## XHtmlString > Components

RSC
