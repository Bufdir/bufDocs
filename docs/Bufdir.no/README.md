# BufdirWeb

BufdirWeb is the solution containing the codebase for the web portal Bufdir.no -
an average/normal CMS site based on Episerver.

# Prerequisites

## General

1. Visual Studio/Code (optional)
2. Current .Net used by the solution installed
3. Node/Npm installed
4. EPiServer Nuget feed set up as source in nuget package manager:
   http://nuget.episerver.com/feed/packages.svc/
5. Bufdirno_feed Nuget feed set up as source in nuget package manager:
   https://pkgs.dev.azure.com/Smidig/Bufdir.no/_packaging/bufdirno_feed/nuget/v3/index.json
6. Make sure you have the appropriate access rights for running the solution,
   administered in Azure. This includes:

   - Appropriate app role access in the solution's Azure AD Enterprise
     application.
   - Access to the Azure SQL Server instance from your IP.
   - Access to list/get values in the solution's Azure keyvault.

   Contact Bufdir's IT contact for appropriate access configuration in Azure.

7. Log in to Azure from the terminal to recieve an authentication token:

   Windows:

   ```shell
   choco install azure-cli
   az login
   ```

   Mac:

   ```shell
   brew install azure-cli
   az login
   ```

   If your account is a member of multiple tenants, you can use the `--tenant`
   flag to specify which tenant you want to log in to (fantomet). Read about
   this flag
   [here](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli#sign-in-with-a-different-tenant).

## Frontend Devs

9. Visual Studio Code installed (Read about settings and plugins
   [here](https://bufdir.atlassian.net/wiki/spaces/BUF/pages/2149974017/Frontend))
10. Make [certificates for localhost](https://web.dev/how-to-use-local-https/)
    Windows:

    ```shell
    choco install mkcert -y [Windows]
    mkcert -install
    mkcert 127.0.0.1
    mkcert localhost
    ```

    Mac:

    ```shell
    brew install mkcert [Mac]
    mkcert -install
    mkcert 127.0.0.1
    mkcert localhost
    ```

11. Open Chrome and navigate to chrome://flags/ and turn on flag: "Allow invalid
    certificates for resources loaded from localhost".

# Getting Started

## General

1. Run `npm i`, then `npm run build` or `npm run watch`
2. Build the solution (right click the "Site" project and click "Build" in
   Visual Studio or `dotnet restore --interactive` and `dotnet build` in CLI)
3. Run the site in IISExpress by using the menus in VS or Ctrl+F5 or
   `dotnet run` or `dotnet watch`
4. Check that login works for your user/that you have the correct access rights
   in Azure by going to the path "/episerver/cms" and checking that you can
   access EPiServer edit mode after logging in.

## Frontend Devs

5. Use Storybook stories as GUI for your component during development and make
   sure that it runs in the .NET project before making a PR

# Pre-commit-actions

## Backend Devs

Pre committing/pushing changes to the repo, please run and verify that all unit
tests run successfully. If not, please fix these issues before pushing your
changes.

## Frontend Devs

Pre committing/pushing changes to the repo, please run and verify that all
component tests run successfully (`npm test`). If not, please fix these issues
before pushing your changes.

## Further reading

See the docs under the folder ./docs to read up on how to do
releases/deployments, best practices we use, etc.
