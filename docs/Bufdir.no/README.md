# BufdirWeb

BufdirWeb is the solution containing the codebase for the web portal Bufdir.no -
a site built with Optimizely and NextJs.

# Prerequisites

## General

1. Visual Studio/Code (optional)
2. The .Net version used by the solution installed
3. The NodeJS version used by the solution installed
4. Make sure you have the appropriate access rights for running the solution,
   administered in Azure. This includes:

   - Appropriate app role access in the solution's Azure AD Enterprise
     application.
   - Access to the Azure SQL Server instance from your IP.
   - Access to list/get values in the solution's Azure keyvault.

   Contact Bufdir's IT contact for appropriate access configuration in Azure.

5. Log in to Azure from the terminal to recieve an authentication token:

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

6. Copy `src/NextJs/.env.example` into a new file called `.env.local` in the
   same location and fill in the secrets that you need (ask someone on your team
   that has the solution running, or find them in Azure in the settings for the
   container running the NextJs image).

# Getting Started

## General

Remember to authenticate with the nuget feed. Install the credential provider
from here:
https://github.com/microsoft/artifacts-credprovider#azure-artifacts-credential-provider

1. Build the solution (right click the "Site" project and click "Build" in
   Visual Studio or `dotnet restore --interactive` and `dotnet build` in CLI)
2. Run the site by using the menus in VS or Ctrl+F5 or `dotnet run` or
   `dotnet watch`
3. In src/NextJs run `npm i`, then `npm run dev` or launch the Next.js debugger
   in vscode (with bufdirno root opened in the IDE).
4. Check that your Optimizely login works for your user (and that you have the
   correct access rights in Azure) by going to the path
   https://localhost:44320/EPiServer/Cms and checking that you can access
   EPiServer edit mode after logging in.
5. Check that your frontend is working on https://localhost:3000

# Pre-commit-actions

## Backend Devs

Before pushing changes to the repo, please run and verify that all unit tests
run successfully. If not, please fix these issues before pushing your changes.

## Frontend Devs

Before pushing changes to the repo, please run and verify that all component
tests run successfully (`npm test`). If not, please fix these issues before
pushing your changes.

## Further reading

See the docs under the folder ./docs to read up on how to do
releases/deployments, best practices used in this project, etc.
