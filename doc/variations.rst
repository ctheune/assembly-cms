================
Content editions
================

Content objects are identified as a "page" in the site hierarchy. However,
depending on the user, different editions of that object may be desired to be
seen:

- a draft or public edition
- the English or Finnish edition

Editions are identified by tags we call "edition parameters". Parameters are
opaque strings, but we recommend using namespaces with colons to separate
parameters that are introduced by distinct extensions. Examples:
"publication:draft", "publication:published", "lang:fi"


Splitting up pages from editions
--------------------------------

A page represents a specific piece of content as in "web page". However, the
object only holds abstract data:

- the page's name
- the sub-pages

Editions are objects with specific data for one set of parameters and hold the
following data:

- the edition parameters
- any content-specific data (e.g. the body)
- meta data: title, creation date, modification date, content tags

Retail behaviour
----------------

The Zope publisher will select an edition to publish based on the request as
it was post-processed by plug-ins which establish a set of required tags.

XXX Describe fall-back mechanism here. 


CMS extensions
--------------

CMS extensions provide specific semantics for editions. Two extensions we
intend to create immediately are:

- multi-lingual content (translations) 
- work-flow

Extensions will create new UI elements which allow to interact with editions
according to that extension's semantics. (E.g. add a button to all draft
editions for publishing them.)

Extensions will create a plug-in for request pre-processing to establish a
determine the edition parameters that are acceptable for editions to publish.


Benefits
--------

- Pages stay the same when talking about different editions. This means that
  one piece of content can be displayed according to a user's preferences
  without screwing link integrity.

- Preview becomes simple to implement, no adjustments to URLs are needed.
