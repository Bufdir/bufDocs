# OpenTelemetry og Monitorering i Bufdir.no

---

## Agenda

1. Monitoreringsstrategi
2. Hva er OpenTelemetry?
3. Muligheter for Overvåkning
4. Varsling og Respons
5. Kostnadsbilde
6. Oppsummering

---

## Monitoreringsstrategi

**Komplett observabilitet:**

- **Frontend (Nettleser):** Real User Monitoring (RUM)
  - Brukeropplevelse og klient-side feil
- **Backend (.NET & Node.js):** OpenTelemetry
  - Industristandard, leverandørnøytral
- **Korrelasjon:** W3C Trace Context
  - Følg requests fra browser til database

---

## Hva er OpenTelemetry?

**Industristandard for moderne backend-instrumentering**

- Åpen standard for innsamling av telemetri
- Leverandørnøytral (ikke låst til én leverandør)
- Omfattende økosystem for databaser, køer, eksterne API-er
- Bedre ytelse på serveren
- Primær anbefaling fra Microsoft for moderne arkitekturer

---

## Fleksibilitet: Velg ditt eget backend

**OpenTelemetry støtter mange backends:**

- **Azure Application Insights** (vårt valg)
- **Grafana + Loki + Tempo**
- **Prometheus + Jaeger**
- **Datadog**
- **New Relic**
- **Elastic Stack (ELK)**

**Fordelen:** Du kan bytte backend senere uten å endre koden!

![OpenTelemetry Collector Architecture](https://opentelemetry.io/docs/collector/img/otel-collector.svg)

*Eksempel: OpenTelemetry Collector kan eksportere til flere backends samtidig*

---

## W3C Trace Context

**Sømløs korrelasjon på tvers av hele systemet**

En forespørsel kan følges fra:
1. Brukerens første klikk i nettleseren
2. Gjennom alle mikrotjenester
3. Helt ned til den enkelte SQL-spørring
4. Eller eksterne tjenestekall

**Resultat:** Full innsikt i hele request-flyten

![Application Insights Distributed Tracing](https://learn.microsoft.com/en-us/azure/azure-monitor/app/media/app-insights-overview/app-insights-overview-blowout.svg)

*Eksempel: Application Insights bruker W3C Trace Context for å korrelere telemetri på tvers av alle lag*

---

## Overvåkningsmuligheter: Frontend (RUM)

**Real User Monitoring gir innsikt i:**

- **Faktisk brukeropplevelse**
  - Lastetider
  - Rendering-ytelse (Core Web Vitals)
  - Nettverksforsinkelse fra klientens ståsted

- **Klient-side feil**
  - JavaScript-unntak
  - Feilede API-kall

- **End-to-end sporing**
  - Fra klikk til databasespørring

![Application Insights User Flows](https://learn.microsoft.com/en-us/azure/azure-monitor/app/media/usage/user-flows-pane.png)

*Eksempel: User Flows viser hvordan brukere navigerer gjennom applikasjonen*

---

## Overvåkningsmuligheter: Backend

**OpenTelemetry i backend gir:**

- **Tekniske metrikker**
  - CPU, minne, responstider
  - Node.js event loop delay
  - SQL-responstider

- **Distribuert sporing (Distributed Tracing)**
  - Følg requests på tvers av mikrotjenester
  - Identifiser flaskehalser

- **Custom instrumentering**
  - Tilpasset forretningslogikk

![Application Insights Live Metrics](https://learn.microsoft.com/en-us/azure/azure-monitor/app/media/live-stream/live-metric.png)

*Eksempel: Live Metrics viser sanntids backend-ytelse med 1-sekunders latens*

---

## Overvåkningsmuligheter: Forretningslogikk

**Fang opp forretningskritiske hendelser**

- **Custom Events**
  - ApplicationSubmitted
  - ReportGenerated
  - Fullføringsgrad for søknader

- **Custom Exceptions**
  - Forretningsfeil som krever oppfølging
  - "Bruker har ikke tilgang til skjema"
  - "Ugyldig dataformat fra ekstern part"

**Resultat:** Proaktiv optimalisering før flaskehalser oppstår

---

## Application Map

**Visuell oversikt over hele systemet**

- Se alle komponenter og deres relasjoner
- Identifiser treghet og feil raskt
- Hver tjeneste har unikt navn (`service.name`)
- Skiller mellom `.Server` og `.Browser`

**Takket være W3C Trace Context og felles Application Insights-ressurs**

![Application Map Example](https://learn.microsoft.com/en-us/azure/azure-monitor/app/media/app-insights-overview/app-insights-overview.png)

*Eksempel: Application Map viser alle komponenter som noder, og HTTP-kall som linjer mellom dem*

---

## Varsling: Typer

**Azure Monitor Alerts gir proaktiv respons:**

1. **Metric Alerts**
   - Infrastruktur og ytelse (CPU > 80%, Responstid > 2s)
   - Nesten sanntid

2. **Log Search Alerts**
   - Feilrater og forretningslogikk
   - KQL-spørringer hvert 5. minutt
   - Eks: Unntak > 10 de siste 5 minuttene

3. **Availability Alerts**
   - Syntetiske tester fra flere steder i verden

![Azure Monitor Alerts Architecture](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/media/alerts-overview/alerts.png)

*Eksempel: Hvordan Azure Monitor alerts fungerer - fra overvåking til varsling*

---

## Varsling: Action Groups

**Hvem skal varsles og hvordan?**

- **Prio 1 (Kritisk)**
  - Vakttelefon (SMS/Push) + E-post
  - Nedetid eller totale systemfeil

- **Prio 2 (Advarsel)**
  - Kun e-post
  - Ytelsesdegradering

- **Automation**
  - Azure Function eller Logic App
  - Automatisk gjenoppretting (restart)

![Action Group Configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/media/action-groups/action-group-2-notifications.png)

*Eksempel: Konfigurasjon av notifikasjoner i en Action Group*

---

## Varsling: Kanaler

**Hvordan kan varsler mottas?**

- **E-post** - Gratis
- **SMS** - Ca. 0.30 kr per melding
- **Push-notifikasjoner** - Azure Mobile App (gratis)
- **Microsoft Teams** - Webhook til Teams-kanal (gratis)
- **Slack** - Webhook til Slack-kanal (gratis)
- **Webhook** - Egendefinert HTTP endpoint (gratis)
- **Azure Logic App** - Avansert routing og integrasjoner
- **ITSM** - ServiceNow, BMC Remedy

---

## Varsling: Kostnader

**Hva koster varsling?**

- **Varselsregler:**
  - Metric Alert Rules: Ca. 1 kr per regel per måned
  - Log Search Alerts: Ca. 5 kr per regel per måned

- **Notifikasjoner:**
  - E-post: Gratis
  - SMS: Ca. 0.30 kr per melding
  - Voice call: Ca. 0.80 kr per minutt
  - Push/Teams/Slack/Webhook: Gratis

- **Estimat:** 20-100 kr per måned for typisk oppsett

---

## Varsling: Beste Praksis

**Unngå varslingstretthet:**

- Ikke varsle på ting som ikke krever handling
- Bruk "Suppress Alerts" for gjentatte meldinger
- Koble til Runbooks
  - Lenke til handlingsplan i hvert varsel
  - Mottageren vet nøyaktig hva de skal gjøre

---

## Overvåking av Sertifikater og Secrets

**Unngå uventet nedetid**

- **Azure Key Vault Overvåking**
  - Event Grid varsler ved utløp
  - Log Analytics for alle aksesser

- **SSL/TLS Sertifikater**
  - App Service & Container Apps
  - Virksomhetssertifikater (Maskinporten)

- **Automatisering**
  - IaC (Infrastructure as Code)
  - Azure Policy

---

## Kostnadsbilde: Oversikt

**Azure Monitor prising (North Europe)**

- **Log Analytics & Application Insights:** Ca. 25-30 kr per GB
- **Datalagring utover 31 dager:** Ca. 1.20 kr per GB per måned
- **Varsling:**
  - Metric Alert Rules: Ca. 1 kr per regel per måned
  - Log Search Alerts: Ca. 5 kr per regel per måned
  - SMS: Ca. 0.30 kr per stykk (E-post gratis)

---

## Kostnadsbilde: Estimat

**Forventet kostnad for Bufdir.no (7 moduler: portal + 5-6 API-er)**

| Kategori | Lavt estimat | Høyt estimat | Ved Daily Cap (5GB/dag) |
|----------|--------------|--------------|-------------------------|
| Datainnsamling | 250 kr | 1 200 kr | 4 500 kr |
| Lagring (90 dager) | 20 kr | 100 kr | 360 kr |
| Varsling & Tester | 80 kr | 250 kr | 250 kr |
| **Sum per måned** | **350 kr** | **1 550 kr** | **5 110 kr** |

**Datamengde:** 2-10 GB per måned per miljø (test/prod)

---

## Kostnadsstyring

**Slik holder du kostnadene nede:**

- **Juster logging level**
  - Unngå logging av all SQL-tekst i produksjon
  - Detaljert logging kun ved debugging

- **Daily Cap**
  - Sett maksimumsgrense (f.eks. 5GB/dag)
  - Forutsigbar kostnad

- **Retention policy**
  - 31 dager gratis
  - 90 dager anbefalt (marginal merkostnad)

---

## Strategisk Verdi

**Fra "kjører systemet?" til "fungerer forretningen optimalt?"**

- **Sammenhengende feilsøking**
  - Fra treghet i browser til SQL-spørring

- **Proaktiv optimalisering**
  - Cache hit rate, query complexity
  - Optimaliser før flaskehalser oppstår

- **Forretningsinnsikt**
  - Identifiser hvor brukere faller fra
  - Ingen komplekse analyseverktøy nødvendig

---

## Oppsummering

**OpenTelemetry + Azure Application Insights = Komplett observabilitet**

✓ Industristandard og leverandørnøytral
✓ Full korrelasjon fra browser til database
✓ Proaktiv varsling med Action Groups
✓ Overvåking av sertifikater og secrets
✓ Forutsigbare kostnader (350-1550 kr/mnd)
✓ Skalerbar og fremtidsrettet

**Resultat:** Optimal brukeropplevelse og driftssikkerhet

---

## Spørsmål?
