## Arbeidsdokument

Retningslinjer web
	- Personvern i sentrum
		- Løsninger på web skal bygges med hensyn til personvern
		- Alle løsninger skal ha plan for data og håndtering
	- Sikkerhet
		- Alle endepunkter skal i utgangspunktet sikres med autentisering
			- Unntak skal dokumenteres og være behovsprøvd
		- Data krypteres at rest
		- Nytter IDPorten som autentisering ved behov for sikker innlogging
		- Azure AD som auth ellers
	- Integrasjoner
		- Integrasjoner skal primært gjøres gjennom felles løsning (Bambus)
			- Unntak, eller tilfeller hvor det ikke er felles interesse for integrasjonen, er ok.
		- Ved integrasjoner skal det dokumenteres avhengigheter og ansvarsfordeling
		- Tredjeparter holdes ansvarlig for sine deler av integrasjonen
	- Dokumentasjon
		- Teknisk dokumentasjon gjøres i repo i .md filer
			- Andre formater: excel, png, docx osv er også ok
	- Tredjeparts kode
		- Tredjeparts kode innhentes fra godkjente områder som NuGet og NPM, og skal kontrolleres og være statisk.
		- Løsninger skal ikke åpne for at tredjepart kan styre kode utenfra. 
			- Dette med bakgrunn i sikkerhet, forvaltbarhet og personvern.
		- 
