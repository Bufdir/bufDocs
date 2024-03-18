# Converting from Razor to Next.js

## Introduction

This guide will help you convert your existing Razor views which are consuming
the Optimizely model directly (or via view models) to Next.js page templates
consuming Optimizely Content Delivery API (CD API for short).

## TL;DR

1. Create a new page template in `src/NextJs/src/page-templates` with the same
   name as the Razor view, but drop the naming convention with "Page" and
   "Index" suffixes.
2. Find usages of the Razor view in the CMS GUI and query the CD API for the
   content of the page.
3. Add data, css classes, and epi data attributes to the page template.
4. Register the page template in the `TemplateWrapper` component.
5. Check that you have all the content by refreshing the page in the browser and
   comparing the new and the old page.

## Razor view

Let's start with the front page of fosterhjem. The Razor view is at the of
writing located at
`src/Site/Features/Shared/ServiceStart/ServiceStartIndex.cshtml`. It's a view
that renders the page title, a hero image, a main intro and the main content of
the page.

```razor
@using EPiServer.Web.Mvc.Html
@inject EPiServer.Web.IContextModeResolver ContextModeResolver

@model RoutableContentViewModel<BufdirWeb.Site.Features.Shared.ServiceStart.ServiceStartPage>
<div class="bd-service-start-index">
    <h1 class="bl-size-1 bl-text-center bl-p-b-5">@Html.PropertyFor(x => x.CurrentContent.Heading)</h1>
    @if (Model.CurrentContent.HeroHeading.IsVisible())
    {
        <div class="bl-p-b-7">
            @Html.PropertyFor(x => x.CurrentContent.HeroHeading)
        </div>
    }
    <div class="bl-container bl-container--medium">
        @if (!string.IsNullOrWhiteSpace(Model.CurrentContent.MainIntro) || ContextModeResolver.CurrentMode == EPiServer.Web.ContextMode.Edit)
        {
            <div class="bl-size-3 bl-p-b-7">
                @Html.PropertyFor(m => m.CurrentContent.MainIntro)
            </div>
        }
        <div class="bl-p-b-6">
            <div class="bl-grid bl-grid--big-row-gap">
                @Html.PropertyFor(x => x.CurrentContent.MainContent)
            </div>
        </div>
    </div>
</div>
```

## Next.js page template

All Next.js page templates that represents an Optimizely view should be located
in the `src/NextJs/src/page-templates` folder, and must be registered in the
`TemplateWrapper` component. The `TemplateWrapper` component will pass the page
data and the global translations.

Let's make the Next.js page template for the fosterhjem front page
(ServiceStart).

### Get Started

First we need to create a new file in the `src/NextJs/src/page-templates`. We
call it the same as in the Razor view, `ServiceStart.tsx`, but drop the naming
convention "Index" indicating that this is a page template, as we know this by
the parent folder name ("page-templates").

We start by defining the component and adding the prop type `PageTemplateProps`
like this:

```tsx
const ServiceStart: FC<PageTemplateProps> = async ({ data, translations }) => {
  return <div className="bd-service-start-page"></div>;
};

export default ServiceStart;
```

Note 1: we add a css class to the wrapping div, this is to make it easier to
debug the page template in the browser (just as with other components).

Note 2: there are, at the time of writing, two ways to get use the global
translations in a page template. Either by using the custom i18next
`useTranslations` hook, or by passing the `translations` prop. We will use the
`translations` prop in this example.

### Add data

To see the Content Delivery API data for this page template, we need to go to
the CMS GUI and find the usage of the page template. In this case, the page
template is used by the fosterhjem front page, so we can use Postman to query
Content Delivery API for the content of this page, on this url:
`https://localhost:44320/api/episerver/v3.0/content?ContentUrl=/no/fosterhjem`.

### Add the page title

The page title is located in the `data` prop, and can be accessed like this:

```tsx
<h1>{data.name}</h1>
```

### See the template in action

To see the page template in action, we need to register it in the
`TemplateWrapper` component. Open the `TemplateWrapper.tsx` file and import the
page template:

```tsx
import ServiceStart from './ServiceStart';
```

then add the template to the switch statement:

```tsx
switch (pageTemplate) {
  case 'ServiceStartPage':
      TemplateComponent = ServiceStart;
      break;
```

Note: the case value must be the same as the contentType name in the CD API
response.

and now we can navigate to the fosterhjem front page and see the page template
on `https://localhost:3000/no/fosterhjem`.

### On page editing

Let's add the styling from the Razor view, and also add the `data-epi-edit`
attribute to tell Optimizely which property this is, so it can be edited in the
preview mode.

```tsx
<h1 data-epi-edit="Heading" className="bl-size-1 bl-text-center bl-p-b-5">
  {data.name}
</h1>
```

You can test this by going to the page in preview mode in the CMS and hover over
the title, and click the edit icon.

### Add the hero

The hero is a block and we can see that this block is implementing the Hero
react component.

All blocks should have a mapper function to map the block data from CDAPI to the
component props. The mapper function is located in
`src/NextJs/src/shared/optimizely/blockToComponentMappers.ts`. Let's add the
mapper function for the hero block:

```tsx
const heroData = mapBlock.toHero(data?.heroHeading);
```

and then we can add the hero component:

```tsx
{
  heroData?.values?.imageUrl && (
    <div className="bl-p-b-7">
      <Hero
        title={heroData.values.title}
        ingress={heroData.values.ingress}
        isSecondary={heroData.values.isSecondary}
        imageUrl={heroData.values.imageUrl}
        imageAltText={heroData.values.imageAltText}
        imageCredit={heroData.values.imageCredit}
        linkText={heroData.values.linkText}
        linkUrl={heroData.values.linkUrl}
      />
    </div>
  );
}
```

Note: we add the `data-epi-edit` attribute to the wrapping div, this is to make
it easier to edit the hero block in the CMS.

### Add the main intro

The main intro is a string property, and we can access it like this:

```tsx
{
  data?.mainIntro?.value && (
    <div className="bl-size-4 bl-p-b-7">{data.mainIntro.value}</div>
  );
}
```

### Add the main content / working with content areas and rich text with block support

The main content is a content area. Content areas and rich text properties with
block support should be passed to the `Xhtmlstring` components block prop. The
`Xhtmlstring` component will render the blocks in the content area or rich text
property.

```tsx
{
  data?.mainContent?.value && (
    <div className="bl-p-b-6">
      <div className="bl-grid bl-grid--big-row-gap">
        <Xhtmlstring blocks={data.mainContent.value} />
      </div>
    </div>
  );
}
```

Note: until we release the Next.js project, you will see blocks that are not yet
supported by the `Xhtmlstring` component by the blocks name in large blue
letters on the page. It will also be logged to the terminal. Make a task to add
support for the block in the `Xhtmlstring` component, and add it to the sprint
board.

### The finished result

```tsx
import React, { FC, Suspense } from 'react';
import Xhtmlstring from '../components/xhtmlstring/Xhtmlstring';
import Hero from '../components/hero/Hero';
import mapBlock from '@/shared/optimizely/blockToComponentMappers';
import { PageTemplateProps } from './PageTemplateProps';

/**
 * This is a the page template ServiceStart
 *
 * example url: https://localhost:3000/fosterhjem
 */
const ServiceStart: FC<PageTemplateProps> = async ({ data }) => {
  const heroData = mapBlock.toHero(data?.heroHeading);
  const mainContentBlocks = data?.mainContent?.value;

  return (
    <div className="bd-service-start-page">
      <div>
        <h1
          data-epi-edit="Heading"
          className="bl-size-1 bl-text-center bl-p-b-5"
        >
          {data.name}
        </h1>
        {heroData?.values?.imageUrl && (
          <div data-epi-edit="HeroHeading" className="bl-p-b-7">
            <Hero
              title={heroData.values.title}
              ingress={heroData.values.ingress}
              isSecondary={heroData.values.isSecondary}
              imageUrl={heroData.values.imageUrl}
              imageAltText={heroData.values.imageAltText}
              imageCredit={heroData.values.imageCredit}
              linkText={heroData.values.linkText}
              linkUrl={heroData.values.linkUrl}
            />
          </div>
        )}
        <div
          data-epi-edit="MainIntro"
          className="bl-container bl-container--medium"
        >
          {data?.mainIntro?.value && (
            <div className="bl-m-b-4 bl-size-4">{data.mainIntro?.value}</div>
          )}

          {mainContentBlocks && (
            <div className="bl-p-b-6">
              <div
                data-epi-edit="MainContent"
                className="bl-grid bl-grid--big-row-gap bl-p-b-7"
              >
                <Xhtmlstring blocks={mainContentBlocks} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ServiceStart;
```

Note: we add an example url in the comments to make it easier to debug the
template. We do not include /no/ in the url, because this will be removed in
before releasing to production.

## Final notes

### Check that you have all the content

You can check that you have all the content from the Razor view by comparing the
two pages in the browser. The equivalent Razor view will have the same
parameters as the Next.js page template, but on port 44320 instead of 3000.

### What to do about missing data

This was a fairly straight forward page template to implement, but you will find
that some page templates are more complex.

Issues you might run into:

- Some blocks are not yet supported by the `Xhtmlstring` component. Make a task
  to add support for the block in the `Xhtmlstring` component, and add it to the
  sprint board.
- Some Razor views have view models and controllers that get data from other
  sources than the Optimizely page model, that is not mapped to the CD API. Make
  a task to add support for the data in the CD API, and add it to the sprint
  board.
  - Example: NewsListPageIndex.cshtml lists all it's children pages. In this
    case you can use the `getPageChildrenData` helper function to get the
    children pages from the CD API.
  - Example 2: LocalOfficeArticleIndex.cshtml includes assets from the media
    archive. In this case you can use the `getCommonPageData` helper function to
    get the common data associated with that page, but the endpoint might need
    to be implemented for the specific page type in the backend.
