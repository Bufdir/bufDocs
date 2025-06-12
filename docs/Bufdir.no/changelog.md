# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to
[Semantic Versioning](http://semver.org/spec/v2.0.0.html).

See ./docs/release.md for release description. See README.md for release
description.

## [unreleased] - 2025-06-02

### Fixed

- Fix info page rendering when main body has a block
- Fix search button on mobile

### Added

- Implement default template for info meetings
- Implement below event list area in Office page (familievern)

### Removed

### Changed

- Bump bufdir_stat to v.8.1.1 - globalUnitsName save fix
- Remove common content from info meeting page

## [3.16.5] - 2025-06-02

### Fixed

- Add null check in ReplaceProp method
- AccordionList header dynamic class based on headingLevels
- Bump bufdir_stat to v.8.1.0 - Respect ".." and show only decimals gt 0
- Pride logo animation fix

### Added

### Removed

- Second event signup button in information meeting and course pages under
  familievern and fosterhjem

### Changed

- Event signup button type and styling in information meeting and course pages
  under familievern and fosterhjem

## [3.16.4] - 2025-05-09

### Fixed

- Redirect urls with docId parameter to url with docId as segment

### Changed

- Updated CSP with new mediaflow entries

## [3.16.3] - 2025-05-22

### Fixed

- Revert removal of /api/framework/GetBufdirFramework endpoint
- Added Next <Link> back in Megamenu missing changes

### Changed

- refactor code: Footer, CookieSettings
- added cookie settings hook
- created context for cookie settings
- Improve overview over unused blocks and media
- Event signup button type and styling in information meeting and course pages
  under familievern and fosterhjem

## [3.16.2] - 2025-05-05

### Fixed

- Added Next <Link> back in Megamenu

## [3.16.1] - 2025-04-29

### Fixed

- MegaMenu not closing when clicking a link

## [3.16.0] - 2025-04-29

### Fixed

- NewsList list header from heading instead of name
- Header levels in some accordions

### Added

### Removed

### Changed

- Bump Buflib to v.6.4.6 - Accordion bugs fixed
- Bump bufdir_stat to v.8.0.8 - Stat Accordions adjustments
- Removed unused APIs
- Protect public APIs with bearer token, Optimizely authorization or reCaptcha
- Report pages uses path based URLs instead of query parameters
- Implement canonical tags

## [3.15.0] - 2025-04-22

### Added

- disableCookieModalAutoOpenUrls

### Changed

- Cookies UU - Adapt to small screens
- Cookies UU - Focus on top
- Cookies UU - Don't show on exceptionsPage - disableCookieModalAutoOpenUrls
- Refactored EventDuration into a reusable component
- Family services event duration display
- Bump buflib to v.6.4.2 - New Accordions
- Bump bufdir_stat to v.8.0.4 - New Accordions
- sending eventLevels to the new BlAccordion
- Display "Finner ikke artikkel" as title when document isn't found on
  DocumentDetailsPage
- Use standard code TinyMCE plugin for WebAdmins

### Fixed

- Fix displaying report when there is one header in abstract
- Fix aria-hidden attribute in breadcrumbs

## [3.14.0] - 2025-03-18

### Changed

- NextJs upgrade to 14.2.25 to include a security patch
- Visning av dato og klokkeslett på familie kursene

### Changed

- Refactored EventDuration into a reusable component
- Cookie modal allways on top and visible in mobile
- Cookie modal links and buttons focusable first
- Added [disableCookieModalAutoOpenUrls] field in Optimizely Footer section

## [3.14.0] - 2025-03-18

### Changed

- NextJs upgrade to 14.2.25 to include a security patch
- Date and time display in family services courses

## [3.13.0] - 2025-03-18

### Added

- Generere dokumentstruktur fra worddokument med liste av kapitler

## [3.13.0] - 2025-03-18

### Fixed

- Image carousel responsive image mapping
- Empty markup when <ul> lists are empty

### Added

- new style breadcrumb

### Removed

- Old menu code

## [3.12] - 2025-03-07

### Fixed

- Localization on close megamenu
- matomoscript src from .env
- correct head title on 404
- heading spacing in guidelines

## [3.11.0] - 2025-03-04

### Fixed

- "Utgiver" filter on rapporter
- Width on header for servicestart-pages
- Back-button on document page in rapporter

### Added

- added region icons for welcome blocks
- metadata for breadcrumb added to CDA

## [3.10.0] - 2025-02-25

### Fixed

- change priority for ingress in link list block so that locally set ingress
  triumphs linked ingress
- disable preview content from appearing on stats pages
- increased z-index so that "Go to content / menu works"

### Added

- implemented filtering on onlinelibrary
- implemented termlist/search/record fetch in next-js backend

### Removed

- removed reindex code from cms-backend

### Changed

- removed external link icon from menu links

- added more options to the remove format button

- upgrade Buflib 6.1.1

## [3.9.0] - 2025-02-05

### Fixed

- upgrade bufdir stat to 8.0.0 for switching to strapi 5

## [3.8.0] - 2025-02-03

### Fixed

- upgrade bufdir stat to 7.1.0 which fixes switching graphs not working for
  downloading, and icons not displaying on graph buttons
- removed empty h2 tags from video blocks
- Fix hypenation issue on title in the Footer component via buflib 6.0.0 upgrade
- Remove empty list (EventListComponent)

### Added

- Add robots meta tag to all pages with a default value and overwrites from
  Optimizely
- Add matomo tracking when opening signup form

### Changed

- Updated version of unused blocks and media
- Upgraded buflib to 6.0.0

## [3.7.0] - 2025-01-16

Note: 3.6.0 is not released at the time of writing, but starting new unreleased
section so that the log lines don't mix upon finishing the started release.

### Fixed

- Fixed issue with robots.txt not returning anything
- fixed issue with shadow not showing no sticky top on menu v2
- Fixed issue with metadata description not being presented which was provided
  by optimizely
- Updated buflib to v6 beta (highlights: new button styles, new media query
  breakpoints)
- Document details page: display text as abstract when supported by reIndex
- Add a 300ms delay before showing loading state on button for contact forms,
  feedback, newsletters and postal searches
- Fixed styling for CTA buttons
- Fixed styling for all buttons that do not use the BlButton component

### Changed

- Started using the Portal component in the EventSignup, PostalSearchModal and
  CookieSettings components

## [3.6.0] - 2024-12-20

### Fixed

- Fixed bug where side menu showed in front of menu
- Fixed search in page on mobile, which did not show any more when triggered
- fixed issue with stats pages not displaying 404 when pages not found

### Added

- New global menu configuration
- New global menu GUI
- Feature toggle for new global menu

## [3.5.1] - 2024-11-28

### Fixed

- Feedback dashboard: fix filter-bug when editing feedback
- Guideline pages: Fixed bug where hits were still marked after closing search
  on mobile and desktop
- Guideline pages: Fixed bug where accordion icon was visible in front of the
  search in page on mobile
- Frontend tests: Added tests for the Xhtmlstring component (render method of
  content areas and rich text areas)

### Changed

- Feedback dashboard: preserve filter-state
- Feedback dashboard: width on filter-inputs increased
- Feedback dashboard: new column - Oppdatert
- Feedback dashboard: moved expander button from own column to inside comment
  column
- Feedback dashboard: break-word and white space to show more of the feedback
- Guideline pages: Updated the design on table of contents on mobile

## [3.5.0] - 2024-11-20

### Fixed

- fixed header/footer (layout) to work correct on no/en pages
- refactored feedback-props
- feedback dashboard
- feedback endpoints moved from function apps into feedbackapicontroller
- fixed header/footer (layout) to work correct on no/en pages
- refactored feedback-props
- new design on search in page on mobile
- feedback dashboard
- feedback endpoints moved from function apps into feedbackapicontroller

### Added

- added big links option for linklist block
- added tests for PostalSearchHandler
- added tests for PostalSearchModal

### Removed

- removed customized handling of 404,500 from Optimizely
- removed customized handling of 404,500 from Optimizely

### Changed

### Added

- changed new layout into the survey result page
- added input result message to detailed table of contents in guideline pages

## [3.4.0] - 2024-11-04

### Fixed

- guideline search: show number of hits, even when search term has below 3 chars
- guideline search: do not show separate hits for separate words in the same
  search term
- Guideline: moved page info from side menu to below guideline heading
- fix search from menu issues with menu not closing and query terms not updating
- updated buflib to v5.1.3 (fix for carousel caption in full screen, 1px pointer
  link hover issue and accordion list toggle-all z-index issue)
- remove underline from pointer links ("enkeltstående lenke") and cta links
  ("call to action") in rich text

### Added

- added matomo tracking of global search and online library search

- added support for ingress in linklistblock and add job to migrate to new
  property

- Guideline pages: added detailed table of content with search/filter

### Removed

- removed old views for pages which were used when optimizely was responsible
  for rendering pages

## [3.3.1] - 2024-10-21

### Fixed

- fix a bug in online library due to url change and possibly due to enabling
  trailing slashes

## [3.3.0] - 2024-10-18

### Added

- guideline pages: added search hits per section
- added CSP Rules to allow Hotjar fonts and images
- added Feedback (Fant du det du lette etter?) to all statistics pages

### Changed

- changed trailing slash to be default because links from optimizely has it

## [3.2.0] - 2024-10-10

### Fixed

- fix simple address not redirecting to actual url
- fix pdf pages not displaying on transport page
- increase max upload file size to 140 MB
- guideline pages: drop side menu heading from focus order
- guideline pages: fix focus styling for side menu links

### Added

- added Link styles in tinymce editor
- guideline pages: added search to side menu
- added subtext field to WelcomeBlock

### Removed

- removed media button from tinymce editor
- removed all code concerning youtube

### Changed

- running each page of bufdir_stat in dedicated Nextjs routes
- guideline pages: updated styling on side menu, using "menu links"
- TranportLink/WelcomeBlock: updated styling according to new design
- moved aria-live for child service results to h2
- updated buflib to v5 (new links and teasers)
- updated bufdir_stat to version 6 (better NextJs support and support for buflib
  v5)

## [3.1.0] - 2024-09-02

### Fixed

- remove space under block if is rich-text followed by another rich-text block
- fixed html rendering without content (missing/lacking null checks)
- hide unused fields in guideline chapter page
- add icons and favico files - add link to manifest file
- fixed wss csp issue for hotjar
- Bug 42751: Veiledere: interne lenker er brutt
- fixed html rendering without content (missing/lacking null checks)
- add missing application insights key
- fixed bug where carousel was rendered even when images were missing
- add hotjar domain to csp
- upgrade node version of frontendcontainer to handle memory leak
- update license for qa and production

### Added

- upgrades to veileder mal to handle rettsdata content
- add new fields to guideline section

## [3.0.1] - 2024-08-21

### Fixed

- Exception on imageblock when key is missing on dictionary
- Guidelinepager failing on external links
- Mediaflow - CSP error

### Added

- Additional logging on CDA errors

## [3.0.0] - 2024-08-20

### Fixed

- #42644 - fix barnevern-filter
- #42186 - add print button to focus order
- Wrong number of search items shown in online library
- Changed survey result wording for take test again

### Added

- Added title of current environment in the top bar in edit mode
- Added siteimprove script

### Removed

- Removed Bing Ads and Google Floodlight scripts
- Remove flag useSecondary from the Link List block (needs to be cleaned from db
  manually via cms gui)

### Changed

- relase.md updated to new procedure
- Rewrote the frontend framework from ReactJs.NET to Next.js
- Making headers in yellow tile areas smaller.
- Slightly changed the design of the guideline page to be able to have alot
  cleaner code.

## [2.31.0] - 2024-02-05

### Fixed

- Prevent error box from blinking in document details for online library

## [2.30.0] - 2024-02-01

### Fixed

- Wrong number of search items shown in online library
- guidelinechaptercontent error
- Fix Application Insights config bug
- Wrong error message displayed when document is not found in online library

### Added

- Show only tagged/whitelisted documents from online library
- go to main content and main menu links
- logic for conditional rendering of small teaser
- forced teaserlist to be small
- Spacing to Guidline page

### Removed

- Remove Archive Page template/controller

### Changed

- Disabled PermanentLinkKeeper Init code from Bufdir.SEO

- Updated buflib to 3.1.6

## [2.29.0] - 2023-01-15

### Fixed

- Wrong number of documents sometimes shown when using online library
  pagination.

### Added

- Online Library step 3 (document page, pagination)
- Redesigned Search page and zero hits
- Added tracking of search terms
- Added tracking to nettbibliotek search and clicks
- margin bottom to accordion list

### Changed

- Updated Buflib to 3.1.5

## [2.28.0] - 2023-12-20

### Fixed

- Navigation issue caused by using relative routes instead of absolute routes in
  nettbibliotek
- Fixed UU issues on foreldrestiltest
- Wrong number of documents sometimes shown when using online library
  pagination.

### Added

- Online Library step 3 (document page, pagination)
- Redesigned Search page and zero hits
- Added google site verification file
- Added tracking of search terms
- Added tracking to nettbibliotek search and clicks

### Changed

- Updated bufdir_stat to version 3.0.5

## [2.27.0] - 2023-12-06

### Fixed

- Change how V8 engine is created to avoid cache issues

## [2.26.0] - 2023-11-30

### Fixed

- Fixed issue with tabs in component props

### Changed

- Replaced IMemoryCache with IObjectInstanceCache

- Updated buflib

## [2.25.0] - 2023-11-23

### Fixed

- made notfound handler available for all editors

### Added

- Online Library with pseudo pagination (Step 2)

## [2.24.0] - 2023-11-03

### Fixed

- Fixed bug with linklist block not supporting horizontal mode and hide arrows
- Upgraded to optimizely 12.23
- Updated License file for test

### Added

- added functionality to preview blocks
- Added (dedicated) pagetype for contacting foster care offices

### Changed

- Start using new fosterhjem api in test environment

## [2.23.0] - 2023-10-13

### Fixed

- Reconfigured Serilog to log to new seq-instance
- Changed how title is displayed for program block program items
- updated bufdir_stat to v3.0.2
- fixed issue where megamenu do not follow header on desktop
- fixed issue where user could scroll behind megamenu on mobile
- fixed event-sync-bug, pages now created with "no" culture as default
- contentLanguage added to get correct language on frontend-translations
- fixed bug with duplicate ids being generated in guideline pages
- fixed bug with best bets tab not showing in elasticsearch
- fixed sorting and title on continous meetings on officepage
- Reduce number of teaser views, and point all to the teaser react component
  instead of having custom html for each
- Fixed bug where linklist title isn't in bold after adding support for teaser
  text
- Fixed bug causing inability to scroll on megamenu on tablets

### Added

- updated buflib to 3.0.2
- Added mapped role for elastic search addon editors
- Added block type for making seminar schedules
- updated bufdir_stat to 3.0.3

### Removed

- Removed unstyled list styles
- added support for displaying teasers in linklistblock
- Removed phone numbers from FostercareOfficePage and FamilyServicesOfficePage
- Deleted VideoTeaserListBlock from the code

### Changed

- Changed how tinymce applies bold to nested items
- Changed from h4 to p tag in eventsignup
- Changed Cookie settings to approve/reject all cookies.

## [2.22.0] - 2023-09-25

### Fixed

- Added ingress for Foreldrestøttede Tiltak
- Fixed bug where elasticsearch prevented deletion of blocks
- Fixed bug where unpublished pages showed in search results
- fixed bug where preview text returned was wrong in search results
- Fixed bug where image description and attribution on a local office article
  started showing in listings due to Imageblock refactoring
- Fixed bug where image description on a local office article started showing in
  listings due to Imageblock refactoring
- Sidemenu overflowing feedback
- ContentTeaser: Don't produce space (empty div) if no header is provided

### Added

- Infobox for listing out field errors in ContactForm if more than one field is
  invalid, else focus on the invalid field
- Added language button for tinymce
- Added support for mediaflow on seminar page and on video block
- Updated buflib and bufdir_stat packages to v3 and fix breaking changes
- Field errors list above form in ContactForm
- Added Bing Ads pixel script
- Added Google Floodlight pixel script
- Hotjar script is running only when all cookies are accepted
- Added Bing Ads pixel script (running when all cookies accepted)
- Added Google Floodlight pixel script (running when all cookies accepted)
- Added plugin for read-only viewing source code in tinymce
- Added context plugin for removing content language set using span tags in
  tinymce.
- Added context plugin for removing content language set using span tags in
  tinymce.
- Added global padding for bd-article\_\_intro

### Changed

- Changed to aria-describedby on ServiceSearch
- Update License files because the previous ones are about to expire
- moved hr inside <li> element instead of as a child of <ul> in MenuItems
- Header menu is now fixed
- Set position relative on footer wrapper
- Disable cookies on Application Insights
- Changed from bl-p-y-7 to bl-p-b-7 on NewsArticle wrapper

## [2.21.0] - 2023-08-30

### Fixed

- Fixed bug with eventsignup checkbox
- Added ingress for Foreldrestøttede Tiltak
- Fixed bug where elasticsearch prevented deletion of blocks
- Added span on accordion list for screen reader to read out loud on
  AccordionList
- Fix bug that stopped backend validation from showing in context of the field
  that failed
- Updated bufdir_stat package to get new accessability fixes
- Wrapped teaser titles in h2 tags
- Maximum-scale from 1 to 5
- Updated Buflib to 2.7.2

### Added

- Added language button for tinymce
- Added tools unused blocks / images
- Css for making long words break with hyphens
- Added code to automiatcally set language code on links in footer if the links
  seems to be to another language
- Added showing time for events, in listings for Fostercare, which are on the
  same day.

### Changed

- Switched out formValidation for react-hook-form with zod

## [2.20.0] - 2023-08-11

### Fixed

- Update EPiServer.CMS to v12.22.3
- Update buflib to v2.6.5 (accessability and styling fixes)
- Using Node v16 instead of v14 in azure pipeline
- Now running typescript check in npm build command
- Fixed structure for feedback analytics in Matomo
- Fixed test id attribute name for dropdowns
- PostalSearchModal: fixed bug where the modal would not open again after it had
  been closed
- Removed pages which google cannot see from language stats module
- LinkList: set focus on the first of the new links when "show more" is clicked
- ChildServicesInstitutionList: set focus on the first of the new links when
  "show more" is clicked
- InfoBox: remove header tag from title
- Feedback: set focus on the text input that appears when user clicks the
  negative response button
- Fixed tab navigation for "Go to main menu" link
- Fixed tab focus for "go to top" button
- ServiceSearch: accessibility improvements
- Filters: accessibility improvements
- ChildServicesInstitutionList: Added aria-live="polite" result section
- PostalSearchHandler: Added aria-live="polite" result sections
- Removed h2 from search result title
- Changed div tags to h3 tags due to accessibility
- Changed div tags to aside for feedback due to accessibility
- Removed h tags from Accordion header elements
- Expiry date for cookie consent
- Not setting EpiStateMarker cookie anymore

### Added

- Added SR/SEO Heading for front page
- Added heading to search page
- Added Hotjar script (explicitly)
- Added Matomo tracking event for foster care contact form submission

### Removed

- Deleted all code concerning Google Analytics and Google Tag Manager

### Changed

- Switched out Jest with Vitest for testing frontend components

## [2.19.2] - 2023-06-28

### Fixed

- Removed H3-tag from consultation block since it messed with the heading
  hierarchy which is bad for a11y
- FilterDropdowns: show title even if no results, and do not show warning when
  result type is "generic"
- Newsletter signup - fixed styling for feedback on success and error
- Parental supported measures: Made filter and result titles editable in the cms
- Focus lock on menu
- update buflib to v2.5.0

### Added

- Added Matomo tracking for signup, survey and feedback
- Added test-id attributes for testers on filterdropdown/multiselect

### Changed

- CSS word break and hyphens on list item
- aria-labels and nav elements in header
- replaced Modal with TileModal in EventSignup, PostalSearchModal, and added id
  to modal in CookieSettings

### Removed

## [2.19.1] - 2023-06-22

### Fixed

- FilterDropowns: show title even if no results, and do not show warning when
  result type is "generic"
- Newsletter signup - fixed styling for feedback on success and error
- Parental supported measures: Made filter and result titles editable in the cms
- update buflib to v2.5.0

## [2.19.0] - 2023-06-19

### Fixed

- FilterDropdowns: Displaying how many options are selected in multi selects
- Footer: Refactored CookieSettings to use buflibs TileModal and put Footer and
  CookieSettings together in react
- Updated bufdir_stat to v2.0.11

### Added

- Added result title to new filter page
- Added flag to show pride logo with animation in start page site settings
- Added admin plugin for seeing stats about nynorsk usage
- Added Geta Not found handler
- Added property for tracking intent for call to action block
- Added selenium test id to filter dropdowns

## [2.18.1] - 2023-06-13

- Update bufdir_stat from v2.0.4 to v2.0.10

## [2.18.0] - 2023-06-07

### Fixed

- ServiceSearch: if only filters, make them take one third width each
- Removed role=tab from Table of contents component
- Fixed bug where it was possible to submit newsletter signup without valid
  e-mail
- Updated to buflib v.2.2.0 (transparent accordion background, no vertical
  centering in teasers)
- Removed all grid column centering (bl-grid--center)
- Changed font size of event signup location
- Fixed bug where alternate text was returned instead of attribution
- Fixed font size for event signup modal
- ServiceSearch: fixed the issue where all inputs appeared short
- Ordered accordion list: updated css class to get the correct style back
- Made reusable phone formatter (frontend) and used it for phone number in
  PostalSearchModal and ChildServiceInstitutionCard
- Fixed instability in FilterDropdowns for better reusability
- Turn SSR back on for header, newsletter, sticky side menu (normerende) and
  transport link
- Added support for multiselect in PostalSearchHandler/FilterDropdowns

### Added

- Added property to all page types for marking content as Nynorsk (which sets
  the language code in html tag)
- Added code for matomo tag manager and property to set the instance ID
- Added draft page templates for "Foreldrestøttede tiltak"

### Changed

- Upgraded optimizely to 12.18

## [2.17.0] - 2023-05-04

### Fixed

- Updated buflib and bufdir_stat packages to v2 and fix breaking changes
- Added block ID on sensible tags for link-list, accordion and accordion
  collection so that top links might anchor link to them
- Child service institutions - open external institution links in new tab
- Child service institutions - style fixes
- Using bl-accordion-list\_\_toggle styling from buflib instead of custom for
  bufdir.no
- Ingress size 4 (not 3) for Article, NewsArticle, Process, InstitutionOverview,
  FosterCareEventList, SeminarList, and OfficeList
- Update buflib (Carousel full screen position fixes and color fixes for warning
  validations)
- Site locked at bottom scroll position if cookie settings pops up

### Added

- Added custom breadcrumbs for bufdir_stat in header
- Added support for retrieving alt text, description, attribution from
  underlying image file if it is not provided in the image block

## [2.16.2] - 2023-04-20

### Fixed

- bufdir_stat: Added slash to base-url prop

## [2.16.1] - 2023-04-20

### Fixed

- Updated bufdir_stat to v2

## [2.16.0] - 2023-04-18

### Fixed

- fixed issue with single image in carousel
- Fixed accordion print overlay issue
- Updated buflib to v2 alpha and fixed breaking changes
- Modal UU fixes (tabbing, body disable scroll when open, focus on open)
- Removed internal text link appearing when printing pages logged in as an
- removed internal text link appearing when printing pages logged in as an
  editor

### Added

- Added support for marking courses as full in family services

### Removed

### Changed

## [2.15.0] - YYYY-MM-DD

### Fixed

- Fixed icon spacing
- Fixed missing colons on child service institutions
- Fixed possible bug when in edit mode with xhtml string fields
- fixed bug where alt text wasn't showing in page teaser
- Fixed bug where adding seminar page failed if call to action link text wasn't
  provided
- Fixed bug where footer was partly in english
- Hotfixed sort order not considering norwegian sorting on child service
  institutions

### Added

- Added field for family service events which do not have end date
- Added support for always displaying sign up button for courses which are
  continous
- Added frontend-support for second required name field in ContactForm,
  EventSignup and PostalSearchModal
- Hide cookie consent box in edit mode
- Added max length to CTA button text
- Added support for specifying individual course signup e-mail recipient on
  family services
- added support for two attendeed on family service course

- Added field for family service events which do not have end date
- Added support for always displaying sign up button for courses which are
  continous
- Hide cookie consent box in edit mode
- Added max length to CTA button text
- Added support for specifying individual course signup e-mail recipient on
  family services
- added support for two attendeed on family service course
- Added page type for parent child centers

### Removed

- Added support for always displaying sign up button for courses which are
  continuous

### Changed

- Made field for start time of seminars required
- Changed the way family service events are filtered
- Changed the way simple addresses are handled - now redirecting to real address
- Changed upload size limit to 40 megabyte
- Changed the way family service events are filtered

## [2.14.0] - 2023-02-21

## [2.14.0] - 2023-03-10

### Fixed

- Hotfixed a bug for xhtml string fields
- Fixed frontend test warning about missing window.scrollTo function
- Upgraded storybook to v7.0.0-beta.40
- Switched out Webpack for Vite when building Storybook
- Switched out esbuild for Vite when building bundles
- Upgraded optimizely to 12.15
- Fixed check for empty array. If array was empty "0" was rendered
- Fix logo not linking to correct startpage for current language
- Fix ordering of institutions

### Added

- Added alt text and description fields for imagefile
- Added functionaly for automatically adding language specific alt texts On
  images in xhtmlstring

### Added

- Added alt text and description fields for imagefile
- (Removed again in hotfix) Added functionaly for automatically adding language
  specific alt texts On images in xhtmlstring

### Changed

- Changed the way robots/crawlers are blocked, now for all envs except
  production
- Changed the way carousel images retrieve alt text, attribution and description

## [2.13.0] - 2023-02-02

### Fixed

- Added checks for undefined on "toLowercase" function in case value was null
- Possible to enter "other information" for the short description of an
  institution.
- Header for the short discription of institution should not be visible if no
  info added.
- Phone and E-mail in Institutions are clickable
- Article lists should not show image description.
- Remove empty structured data script tag because google crawler complains
- Fixed that all last accordions in a list get a spacing bottom class.

- Better handling of cases in header and footer when content has not been added
  to various properties
- Re-enabled feedback export for authenticated users and added menu item to
  optimizely admin panel. Implemented "permissions to functions" for granular
  access management.

### Added

- Added newsletter block
- Support for validating recaptcha tokens before passing requests to internal
  resources.

### Removed

- Misc old cruft

### Changed

- Change how the back to start page link is created in bread crumb
- made several properties on the start page unique per language to support
  localization
- Updated reCaptcha keys
- Updated bufdir configuration to Options pattern
- Rewrote foster care events and zip codes to use internal resources so the
  configuration could be further streamlined.

## [2.12.0] - 2023-01-13

### Fixed

- Phone and E-mail in Institutions are clickable
- Month names aren't capitalized in event dates
- Scrolling user up to contact submit success message after submit
- Institutions now shows contact info even if only address info is set
- Removed punctuation after day in foster care event listing.
- Updated bufdir_stat package from 1.1.9 to v1.1.11.
- Updated Statistics.ApiUrl to <https://statistikk.bufdir.no> in the production
  app settings.

### Removed

- `Infrastructure/InternalResources` was replaced with nuget package and
  necessary adjustments made.

### Changed

- Family services course registrations now contains more information.
- Hero block has a different logic for determining when it should be visible

### Added

- Service start page has mainintro field

- Added teaser info to seminar, foster care office and family services office
  pages
- Added teaser info, main intro, main body, bottom content and adjusted styling
  on seminar list page
- Added main intro to foster care office and event list page

## [2.11.0] - 2022-12-07

### Fixed

- Updated bufdir_stat package from 1.1.7 to v1.1.9.

### Added

- Statistics page type for Statistics root page
- Model for Statistics subpages
- Partial routing to Statistics subpages
- temporary endpoint for editors to see how blocks are used
- Teaser image - when provided is used as an open graph image

### Removed

- Removed existing controller routing to statistics pages

## [2.10.1] - 2022-11-24

### Fixed

- Bug causing bufdir logo to appear on private institution

## [2.10.0] - 2022-11-04

### Fixed

- Added a [markdown file](/docs/release.md) with notes for releasing and
  deploying this project.
- Updated bufdir_stat package from 1.1.6 to v1.1.7.
- Added qa and prod api urls for bufdir_stat in the appsettings.
- Updated the license for test.
- Events would not show in listing before they were finished.
- [Hotfix] 404 handling improved in application insights

### Added

- Add logic to hide several page types from external search engines, yet keep
  them visible for internal search engine.

## [2.9.2] - 2022-10-20

### Fixed

- Seminars are shown until seminar end time on listing page
- Seminar end time is shown properly on seminar page

## [2.9.1] - 2022-09-26

### Fixed

- Routing logo and breadcrumb start to relative root, instead of <www.bufdir.no>

## [2.9.0] - 2022-09-23

### Fixed

- Accidental container classes within container classes will not produce extra
  space on the sides (buflib).

### Added

- Image counter for Carousel component (buflib).

## [2.8.0] - 2022-09-?

Missing changelog documentation...

## [2.7.0] - 2022-08-22

### Fixed

- Foster care: changes on meetings and courses lists
- Api/frontend communication: fixed validation messages from backend

### Added

- Buflib carousel for use in Razor
- Institution page
- Contact forms: More options for editors

## [2.6.2] - 2022-08-15

### Fixed

- Fixed response handling in Postal Search Route frontend component

## [2.6.1] - 2022-08-10

### Fixed

- Fixed limit on (FosterCare)EventListBlock

## [2.6.0] - 2022-08-10

### Fixed

- Updated most frontend packages [^1] (not react or packages that needs react
  v18 to update).
- Style fix for SurveryResultPageIndex: added the required buflib prefix for the
  wysiwyg css class in survery result body content.
- Fixed links on search results for guideline pages. They now point to the root
  chapter instead of an anchor-link to the specific guideline as requested.

  [^1]

| Package                 | From    | To      |
| ----------------------- | ------- | ------- |
| bufdir_stat             | 1.1.5   | 1.1.6   |
| bulma                   | 0.9.3   | 0.9.4   |
| @babel/core             | 7.17.7  | 7.18.9  |
| @babel/preset-react     | 7.16.7  | 7.18.6  |
| @types/jest             | 27.4.1  | 28.1.6  |
| concurrently            | 7.0.0   | 7.3.0   |
| core-js                 | 3.21.1  | 3.24.1  |
| dotenv                  | 16.0.0  | 16.0.1  |
| esbuild                 | 0.14.27 | 0.14.51 |
| esbuild-sass-plugin     | 2.2.5   | 2.3.1   |
| eslint                  | 8.11.0  | 8.21.0  |
| eslint-plugin-mdx       | 1.16.0  | 2.0.2   |
| eslint-plugin-storybook | 0.5.12  | 0.6.1   |
| jest                    | 28.1.0  | 28.1.3  |
| jest-environment-jsdom  | 28.1.0  | 28.1.3  |
| msw                     | 0.39.2  | 0.44.2  |
| prettier                | 2.6.0   | 2.7.1   |
| sass                    | 1.49.9  | 1.54.0  |
| sass-loader             | 12.6.0  | 13.0.2  |
| ts-jest                 | 28.0.2  | 28.0.7  |
| typescript              | 4.6.2   | 4.7.4   |

### Added

- Added InternalResources segment to appsettings.json QA and Prod
- Configged up feedbackAPI for both qa and prod
- Added episerver.labs.gridview package for demo/testing purposes
- Made it possible for editor to overwrite the default text on the survery
  result page read more button

### Changed

- Changed approach to generating preview text for search results. Instead of
  hard-coding the search order for each page type, we derive the order from the
  [Display]-attribute on earch field to approximate the first occurrence of the
  search term for the end user.

## [2.5.0] - 2022-06-27

### Fixed

- Possibility for adding multiple FactBox blocks on the front page.
- Style fixes.
- Bug fix for lists with filter url parameters.

### Added

- Variants of Factbox block.
- Automatic archive functionality.
- Frontend tests

### Changed

- Removed "place" from digital meetings in the gui.

## [2.4.1] - 2022-06-07

### Fixed

- Dotnet 6.0 upgrade on main solution

### Added

- new page template for news list
- new page template for news articles
- logic for auto-archiving and tagging old/expired news articles

## [2.4.0] - 2022-05-31

### Fixed

- Visual bugfixes
- Better naming for page templates

### Added

- New page templates: Kurs og konferanser
- Component test for ContactForm component
- Set up page template with react component for Statistics pages

### Removed

- Removed some old blocks from migration of normative

## [2.3.1] - 2022-05-20

### Fixed

- Cleaned up json serialization settings to a single place to ensure consistent
  camel case serialization behavior.

## [2.1.0] - 2022-03-28

### Fixed

- Role access in episerver
- Missing tabs in episerver
- Frontend spacing issues
- Transformations
- Search fixes

### Added

- Feedback component and cms options for displaying it on pages (frontend
  commented out for this release, since api backend is not 100%)
- Call to Action block

## [2.0.0] - 2022-03-21

### Fixed

- Style fixes
- Spacing fixes
- Loads and loads of code smell fixes
- UU fixes
- Refactor CSS for smaller payload

### Added

- New Front End build for production
- Migrated normative content (Normerende)
- Teaser list 3 columns
- Added tests for solution

### Removed

- Removed old styleguide

### Changed

- Upgraded backend to dotnet 5.0
- Upgraded CMS to new version
- Lots of changes to Elastic Search implementation
  - Moved away from Epinova module, now custom implementation.

## [1.3.1] - 2022-02-DD

### Fixed

- Added hook to tinymce to remove rogue div tags

## [1.3.0] - 2022-02-DD

### Fixed

- Hero block was too wide when no image was added
- Removed source field from fact box block
- New episerver role "Publisist"

## [1.2.1] - 2022-01-27

### Fixed

- Icons in solution now shows again
- Copy paste in blocks

### Added

- Migrations of "Normerende" area

## [1.1.4] - 2022-01-15 - Hotfix

### Fixed

- Listing title on "Kurs" pages

### Added

- New role group, "Publisist"

## [1.1.3] - 2022-01-11

### Fixed

- Tests
- manifest.json
- config settings elastic QA

### Added

- Teaser block
- Content Teaser
- Word-break: initial on tables

### Removed

- Errorvault
- Developertools

### Changed

- Accordion
- Console warnings, duplicate keys
- Tests
- Logic for isvisible

## [1.1.2] - 2021-12-15

- Fosterhjem stuff made generally reusable
- Responsive images fixes
- Fosterhjem URL on meetings
- Refactoring ajax calls
- Recaptcha v3
- favicons and SEO
- More deployment pipeline fixes
- Search fixed, elastic running.

## [1.1.1] - 2021-12-07

### Fixed

- Fixed tracking of contact forms not working.

## [1.1.0] -2021-12-01

- Major pipeline changes
  - Config changes to KV secrets
  - ES6 building frontend
  - Npm cache
- Structure reformatting in frontend
- Oslo integration
- "Fant du det du lette etter" started
- Foreldrestiltest page
- RTE features turned on

## [1.0.3] - 2021-11-19

- Technical YELL
- Bugfixes
  - Fosterhjem release bugs
- Authentication to API
- GTM changes
- Package management
- Front End unit tests
- Backend unit tests
- Cards block
- Fosterhjem.API changes

## [1.0.2] - 2021-11-01

- Sprint 39 changes
- gui fixes based on design feedback on live fosterhjem
- technical dept
- xhtml string to accordiancontentblock
- Table overflow fix
- Change event location to "Digitalt" or "Fysisk(<location>)" depending on event
  type
- Support for embeded video in main body

## [1.0.1] - 2021-10-25

- Hot fixes kurs page

### Added

## [1.0.0] - 2021-10-21

### Added

- Fostercare section (fosterhjem)
- Product section (normerende produkter)

## [Unreleased] - YYYY-MM-DD

### Fixed

### Added

### Removed

### Changed
