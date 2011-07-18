==================
A CMS for Assembly
==================

History
=======

The Assembly website has been run using Plone since fall of 2003. In those
past 6 years it was run relatively successfully without major outages.
However, webcrew's (and the CMS editors') experience hasn't been free from
negative experiences:

- Upgrading Plone is a tedious effort and thus has not happened.

- Plone's rich environment is overly complex for trying to add small features
  to the website in an agile matter.

- Archiving required us to keep a copy of a full Zope/Plone installation
  running, consuming memory on the servers and requiring separate
  administrative attention.

- Managing content in multiple languages has had annoying bugs hindering
  editors of updating content.

- Plone's UI tended to be overly complex for editors "just trying to change a
  sentence".


Vision
======

I envision a CMS which does less, but does the things it does in a clean
fashion.

The CMS will:

- have less code
- no features nobody uses
- a simple but efficient content model and editing UI
- a powerful styling story which allows us to introduce dramatic changes to
  the retail UI whenever we want without changing the content (model)
- a core as small as possible (but not smaller) with a flexible extension
  story to enhance the retail and editor's experience

Feature chart
=============

Content model
-------------

- Content only has a name and a body and sub-content

- XHTML-Page
- Asset (Any file: image, media, ...)
- Micro-Application
- Multi-language content objects (How to create translated objects in retail
  UI? How do micro applications fit in? Assets not translated? General
  approach to "multi version/multi aspect content?")

- Very lightweight meta-data model: Title, last changed, created, tags
- Automatically extract meta-data for pages: title via <h1>


Layout / Styling
----------------

- Allow skins to define new templates for content objects and allow content
  objects to choose which template to use for retail display


Editing
-------

- Always select the edit view
- Show editor + sub-pages side by side
- Most simple security: logged in or not, define principals in ZCML/buildout for now
  - do user-management based on SSO later
- Simple publication work-flow (working copy editing?)
  -> preview of things currently in working copy

CMS plug-ins
------------

- LMS support
- Smart folders/saved searches as content?
- Search
- Import content from Plone/LinguaPlone. Import archived content?
- Banner rotation system, editable by content authors
- Site guide

Retail plugins
--------------

- Custom skins
  - multiple skin variants: mobile, regular
- News listing
- Schedule (micro application)
  - ical export
- Portlets
  - news
  - upcoming events
  - forums (latest posts)
- Search
- Party counter

Operational requirements
------------------------

- Store all content of the various parties in a single installation and database using multiple
  instances of the CMS
- Avoid in-database-configuration as far as possible (skin selection, anything
  else?)
- Try to implement consistency-ensuring checks when changes are applied or a
  new version of the software is started
