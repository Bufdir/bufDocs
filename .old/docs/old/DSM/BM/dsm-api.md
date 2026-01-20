# DSM Api

Web api for filing mediation requests to family services.
Uses azure service bus to read mediation questionnaire and familievern offices, and for sending questionnaire responses to fado/famo.

## Overview

The solution consists of 7 projects:

- Abstractions
- Api
- Application
- Data
- Notification
- ServiceBus
- Tests

### Abstractions

`Abstractions` contains all the `dtos` used by `Api` (and `Application`). We currently use the same objects for both application and data transfer, but that could change in the future if the need arises.

`Abstractions` is a separate project as we reuse some of the objects in the `FSA` project to enrich the questionnaire from the client with data from the population register. Thus, `Abstractions` has [a separate build pipeline](abstraction-pipeline.yml) to build a `Bufdir.DsmApi.Abstractions` package and deploy it to the [library artifacts feed](https://dev.azure.com/Smidig/Bufdir.no/_artifacts/feed/Api.Library).

### Api

`Api` hosts the application itself and contains the web api controllers for searching family services offices, retrieving differentiation questionnaire and filing new mediation requests/amend mediation cases with answers from parent2.

### Application

`Application` contains application layer logic such as validators, services for
reading/writing the data used by the controllers via the `Data` layer etc. It also contains some mapping code not (yet) moved to AutoMapper. The services for reading/writing family services and corresponding zipcodes are so simple that they are handled by a common generic `SimpleDataService`.

### Data

`Data` is the persistence layer that uses ef core to store the various entities in a SQL server database.

### Notification

`Notification` contains the code used to publish messages to the [notifications api](https://dev.azure.com/Smidig/Bufdir.no/_git/Bufdir.Notifications.API) when mediation cases are filed or amended.

### ServiceBus

`ServiceBus` uses [MassTransit](https://masstransit-project.com/) to read family services offices, zip codes and differentiation questionnaires and write mediation cases to azure service bus.

### Tests

^^^^^^^^ The title is self-explanatory `ò_Ó`

## Getting Started

`appsettings.json` has a local db connection string. To set up a local environment, download [Sql Server developer edition](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) and install the [`ef core` tools](https://learn.microsoft.com/en-us/ef/core/cli/dotnet). Create a `dsmapi` database (for instance using [SSMS](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16)) and run `dotnet ef database update` in the `Data` project directory to apply the database schema.

### Key vault

`appsettings.Development.json` is configured to use the `kv-dsmapi-devtest` keyvault on `Fantomet`. As long as you have a valid `az login` token, it should be able to read the app registration etc from it.

### Devtest environment

Each merge to the `develop` branch gets deployed to [dmsapi-devtest](https://dmsapi-devtest.azurewebsites.net). Its corresponding app registration in Fantomet azure ad is `DsmApi dev`, with a corresponding `dsmapi dev client` with access granted to the api.
Oauth2 token endpoint is `https://login.microsoftonline.com/1fb73343-87a4-4ba0-88b8-4452ec55d7f5/oauth2/v2.0/token` and scope is `api://2d37a1a0-467e-4ac2-a4f6-7a9714211ef4/.default`
Client id and secret for the client for testing has been added to the key vault. Retrieve using

```bash
az keyvault secret show --name "testclient-id" --vault-name "kv-dsmapi-devtest" --query "value"
az keyvault secret show --name "testclient-secret" --vault-name "kv-dsmapi-devtest" --query "value"
```

### User id validation

In addition to the client credentials flow protecting the web api, we needed a tamper-proof way of passing the clients person number.
We do this by adding a `x-bufdir-personno` http header containing a salted hash of the current users person number in the FSA backend. We can then verify that the person number in the header matches the person number in the json body, and that the header was added by the FSA using a secret preshared salt.

# Database
The version of EF core tools are defined in the manifest file `dotnet-tools.json`. To get the correct version of EF core tools execute the CLI command `dotnet restore`.
When changing the database model a new migration file can be created by executing the CLI command; `dotnet ef migrations add <ChangeDescription>`.