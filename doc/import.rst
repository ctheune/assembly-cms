=====================
Content import format
=====================

The content import format was created to fill an ``asm.cms`` site quickly with
content from an already existing system.

We tried to keep the import format free from specifics of the previous system
so we have a slight chance of having a re-usable format.

The format is XML with the following structure, given as an example::

<?xml version="1.0">
<import base="/previous/prefix/path">
  <page path="path/after/prefix">
    <edition parameters="lang:en workflow:public"
             title="A fine piece of content"
             tags="news bigscreen"
             created="ISO date in UTC"
             modified="ISO date in UTC"
             >
    ...content encoded in base64...
    </edition>
    <edition parameters="lang:fi workflow:draft">
    </edition>
  </page>
  <asset path="path/after/prefix">
    <edition parameters="lang:fi workflow:draft">
    ...content encoded in base64...
    </edition>
  </asset>
</import>
