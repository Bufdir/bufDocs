# Implementering av Opt-in og reCAPTCHA for nyhetsbrev

Dette dokumentet beskriver beste praksis for implementering av Opt-in og reCAPTCHA i Bufdir.no-løsningen, spesielt rettet mot nyhetsbrevabonnement.

## 1. Oversikt
Løsningen benytter en de-koblet arkitektur (Decoupled Architecture) der Optimizely CMS fungerer som innholdsmotor og en Next.js-applikasjon fungerer som frontend. Nyhetsbrevabonnement håndteres gjennom et dedikert API (`bufdirno-newsletter-api`) som fungerer som en bro mot den eksterne tjenesten Dialog API (Make).

## 2. Hvorfor er denne løsningen bedre? (Sammenligning)

Dagens løsning har visse svakheter knyttet til bot-beskyttelse og datakvalitet. Den foreslåtte løsningen forbedrer dette på flere punkter:

| Funksjon | Dagens løsning | Foreslått løsning (Beste praksis) |
| :--- | :--- | :--- |
| **Påmeldingstype** | Single Opt-in (bruker blir aktiv umiddelbart) | Double Opt-in (krever e-postbekreftelse) |
| **reCAPTCHA** | Sendes fra frontend, men valideres ikke i backend | Valideres strengt i backend med score-sjekk |
| **Datakvalitet** | Risiko for falske/feilstavede adresser | Høy (kun verifiserte adresser blir aktive) |
| **GDPR** | Svakere dokumentasjon på samtykke | Sterk dokumentasjon via bekreftet e-post |
| **Bot-sikring** | Lav (enkelt å sende falske forespørsler til API) | Høy (stopper automatiserte påmeldinger) |

### Viktige fordeler:
- **Redusert spam:** Uten backend-validering av reCAPTCHA kan roboter fylle opp listene med søppel-e-post.
- **Bedre leveringsrate:** Ved å bruke Double Opt-in unngår man å sende e-post til adresser som ikke eksisterer, noe som beskytter Bufdir sitt rykte som avsender (Sender Reputation).
- **Juridisk trygghet:** Double Opt-in er den anbefalte metoden for å møte kravene til samtykke i GDPR.

## 3. reCAPTCHA (Bot-beskyttelse)

For å forhindre automatisert spam-påmelding skal alle abonnementsskjemaer beskyttes med Google reCAPTCHA v3.

### Implementering i Frontend (Next.js)
Frontend må generere et reCAPTCHA-token før forespørselen sendes til backend.

```typescript
// Eksempel på bruk i en React/Next.js-komponent
const executeRecaptcha = async () => {
  if (!window.grecaptcha) return;
  const token = await window.grecaptcha.execute(RECAPTCHA_SITE_KEY, { action: 'subscribe' });
  return token;
};

const handleSubscribe = async (email: string, mailingListId: string) => {
  const token = await executeRecaptcha();
  const response = await fetch('/api/newsletter/subscribe', {
    method: 'POST',
    body: JSON.stringify({ email, mailingListId, recaptchaToken: token }),
  });
  // ... håndter respons
};
```

### Validering i Backend
Backend-API-et (`bufdirno-newsletter-api` eller proxy i hovedapplikasjonen) må validere tokenet mot Google sine servere før påmeldingen prosesseres.

1. Mottatt token sendes til `https://www.google.com/recaptcha/api/siteverify`.
2. Sjekk at `success` er true og at `score` er over en akseptabel terskel (f.eks. 0.5).

## 4. Opt-in (Samtykkehåndtering)

For å sikre samsvar med personvernlovgivning (GDPR) og god skikk for e-postmarkedsføring, skal Double Opt-in (bekreftet påmelding) benyttes.

### Hvorfor Double Opt-in?
- Sikrer at e-postadressen faktisk tilhører brukeren.
- Reduserer risikoen for "spam traps" og dårlig leveringsrate.
- Dokumenterbart samtykke i henhold til GDPR.

### Flyt for Double Opt-in via Dialog API
I Bufdir-løsningen er det den eksterne tjenesten Dialog API (Make) som håndterer utsendelse av bekreftelses-e-post.

1. **Bruker melder seg på:** Brukeren skriver inn e-posten sin på nettsiden.
2. **API-kall:** Frontend kaller `bufdirno-newsletter-api`.
3. **Trigger i Dialog API:** API-et sender en kommando til Dialog API for å legge til abonnenten med status "Unconfirmed".
4. **Bekreftelses-e-post:** Dialog API sender automatisk en e-post til brukeren med en unik lenke.
5. **Bruker bekrefter:** Brukeren klikker på lenken i e-posten.
6. **Aktiv status:** Abonnenten endrer status til "Active" i Dialog API, og er nå formelt påmeldt.

### Tekst og Samtykke
Sørg for at skjemaet inneholder tydelig informasjon om:
- Hva brukeren abonnerer på.
- At de vil motta en e-post for å bekrefte abonnementet.
- Hvordan de kan melde seg av (lenke til personvernerklæring).

## 5. Feilhåndtering og Tilbakemelding
- Gi brukeren en klar melding om at de må sjekke e-posten sin for å fullføre påmeldingen.
- Håndter feilmeldinger fra API-et (f.eks. dersom e-postadressen er ugyldig eller allerede blokkert).
- Ved reCAPTCHA-feil, vis en nøytral feilmelding som ikke gir for mye informasjon til roboter, men som veileder brukeren til å prøve igjen.

## 6. Referanser
- `bufdirno-newsletter-api`: Integrasjonslag for nyhetsbrev.
- [Dialog API Dokumentasjon](https://subscribers.dialogapi.no/api/public/v2/swagger/ui/index): For detaljer om abonnenthåndtering.
- [Google reCAPTCHA v3 Dokumentasjon](https://developers.google.com/recaptcha/docs/v3): For implementeringsdetaljer.
