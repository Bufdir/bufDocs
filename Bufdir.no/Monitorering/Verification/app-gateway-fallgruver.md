# Fallgruver ved bruk av Azure Application Gateway og Monitorering

Dette dokumentet beskriver utfordringer og kritiske fallgruver ved bruk av Azure Application Gateway (AGW) sammen med den nye monitoreringsstrategien.

---

### 1. Manglende `ForwardedHeaders` (Kritisk)
Backenden må konfigureres til å stole på headere fra Application Gateway.
*   **Problem:** Uten `UseForwardedHeaders()` ser backenden kun IP-adressen til Application Gateway, ikke den faktiske brukeren. Dette gjør feilsøking i loggene umulig for IP-baserte problemer.
*   **HTTPS-støtte:** Manglende `X-Forwarded-Proto` kan føre til at OIDC-redirects (innlogging) bruker HTTP i stedet for HTTPS, som feiler i nettleseren.

### 2. Støy fra Health Probes (Helsesjekker)
Application Gateway sender hyppige helsesjekker til backend.
*   **Risiko:** Disse genererer store mengder sporingsdata i Azure Monitor, som øker kostnader uten å gi verdi. FSA Backend mangler i dag filtrering for disse.

### 3. WAF-regler og Traceparent
Dersom Web Application Firewall (WAF) er strengt konfigurert, kan den blokkere forespørsler med ukjente headere.
*   **Tiltak:** Verifiser at `traceparent` (W3C standard) er tillatt i WAF-oppsettet for både test og produksjon.

### 4. Miljøforskjeller (Test vs. Prod)
Det har blitt observert at løsninger som fungerer i testmiljøet i Azure, feiler i produksjon.
*   **Sannsynlig årsak:** Forskjeller i Application Gateway-konfigurasjon (f.eks. WAF-modus "Prevention" vs "Detection", eller manglende `KnownProxies`-oppsett i prod).
*   **Anbefaling:** Sjekk at `KnownProxies.Clear()` brukes dersom man stoler på Application Gateway, slik at alle innkommende proxy-headere aksepteres.
