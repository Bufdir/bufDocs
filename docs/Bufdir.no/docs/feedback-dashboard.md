
# Dagens situasjon:

Feedback er 3 functions i en functions app
    - Export 
    - Feedback (POST ny feedback)
    - DeleteOld (Slette feedback eldre enn 6 måneder)
Database med 2 tabeller, Feedback og Pages

Function app kan fjernes når vi har deployet ny versjon

# Ny løsning med dashboard i Opti:

- Vi flytter endepunktene til opti
    - /api/feedback/PostFeedback - endepunkt brukes av frontend for å sende inn nye feedback (Beskyttet av recapthca)
    - /api/feedback/Data - endepunkt for opti-dashboard (Beskyttet av rolle)
    - /api/feedback/Redact - endepunkt for å redigere kommentar på feedback (Beskyttet av rolle)

### Database   

I den forbindelse vil det også være en db-migrering for tillate flere navn pr side (ref at alle statistikk-sider pr idag har samme pageid)

Migrering av db er ikke lagt inn i ci/cd og må utføres manuelt pr nivå. 

(Hvis feedback skal endres ofte så anbefales det at dette legges inn i pipeline og ikke kjøres manuelt)

1. Ta en kopi av Pages tabellen
```
CREATE TABLE [dbo].[PagesBak](
	[Id] [int] NOT NULL,
	[Name] [nvarchar](max) NOT NULL,
	[Url] [nvarchar](max) NOT NULL
)
GO

INSERT INTO PagesBak(Id, Name, Url)
SELECT        Id, Name, Url
FROM            Pages
GO
```
2. dotnet ef migrations script --idempotent -o c:\temp\feedbackmigration.sql
3. Kjør sql migrering
4. Oppdater data i feedback tabell fra PagesBak
```
UPDATE       Feedback
SET                PageName = p.Name, PageUrl = p.Url
FROM            Feedback INNER JOIN
                         PagesBak AS p ON p.Id = Feedback.PageId
```
5. Verifiser at __EFMigrationsHistory har 2 nye oppføringer
6. Verifiser at Feedback har 4 nye kolonner (PageName,PageUrl,Redacted,Updated)

### Dashboard app

Ny react med vite app ligger her: src\Site\feedback-dashboard

Når Backend publiseres så kjører npm i og npm run build for å få bundlet denne inn i backend og denne app blir da mounted inn her: \src\Site\Features\Feedback\Views\Dashboard.cshtml