


All Localization are loaded in the layout file  - /src/app/layout.tsx

Language are loaded from Optimizely through the getGlobalData function
and are merged with the json files in the i18n folder

the merged result are available on the globalThis object both on server and on client

<Localizations/> component are responsible to make all the localization available for client-components

Localizations & language

globalThis.localization
	.cms = Language from Optimizely
	.system = localization from system.json
	.validation = localization from validation.json
	.accessibility = localization from accessibility.json
    .generic = localization from generic.json

All localization are typed in src\shared\optimizely\globalTypes.ts

example usage:

const globalResources = globalThis?.localization?.cms?.Shared?.GlobalResources;

return (
    <p>{globalResources?.HasExpired}</p>
)


