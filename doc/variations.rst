==================
Content variations
==================

Content objects are identified by a location in the site hierarchy. However,
depending on the user, different variations of that object may be desired to
be seen:

- a draft version or the published version
- the English or Finnish version

Variations are identifier by tags we call `variation parameters`. Tags are
strings and are grouped by namespaces which are stated with a colon, for
example: "publication:draft", "publication:published", "lang:fi"


Splitting up locations from variations
--------------------------------------

A location represents a specific content object but holds only abstract data
about it:

- the location's name
- sub-locations


Variations are content objects with specific data for one set of variation
parameters and hold the following data:

- the variation parameters
- any content-specific data (the body)
- Meta data: title, creation date, 


Retail behaviour
----------------

The publisher will select a variation for publishing based on the request as
it was post-processed by plug-ins which establish a set of required tags.

A plug-in can return a list of tags which are acceptable in the order of their
priority for showing. For example the publication extension when asked for a
preview of the site will return [set('draft'), set('published')]. When asked
for the public view, it will return [set('published')]. At the same time, the
language feature might return [set('fi'), set('en')] when asked for Finnish
with English as the fall-back language, but will return [set('en')] for English
without a fall-back.

Open issue: how do we prioritize combined fall-back options?


CMS extensions
--------------

CMS extensions provide specific variation uses. They will introduce namespaces
according to their needs. Two extensions we intend to create immediately are:

- translation/language extension
- publication/work-flow extension

Extensions will create new UI elements which allow to interact with variations
according to that extension's semantics. (E.g. add a button to all draft
variations for publishing them.)

Extensions will create a plug-in for request pre-processing to establish a
request parameter giving a set of variation parameters which are required 



Benefits
--------

- Locations stay the same when talking about different variations. This means
  that one piece of content can be displayed to a user's preferences without
  screwing link integrity.

- Preview mode will link correctly, no adjustments to URLs are needed
