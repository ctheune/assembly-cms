==================
A CMS for Assembly
==================

History
=======





Vision
======


CMS

- Make a very simple content/asset model
    -> page (xhtml), folder
    -> asset (file, image, media)
    -> micro-application
    - select additional layouts for an object from skin
- Simple security
- Simple publication workflow/copy editing
- Get multi-language right
- Very simple editing UI
    - name of page
    - language/translation
    - xhtml body
- Simple post-processing of content
    -> generate metadata from content? e.g. title, description, ...
- Allow to write mini-applications for retail on top of content easily
    -> calendar
    -> "portlets", like a
    -> search
    -> saved searches
- Allow to sanely write UI extensions for the CMS UI
    - link checker
    - search
    - search folders

- import content from plone and linguaplone

Management

- Store all content of the various parties in a single application and database using multiple
  instances of the CMS
- Only simple database-configuration: choose which extensions are enabled
  (skins)
- Skins as egg extensions
