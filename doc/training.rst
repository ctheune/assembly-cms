====================================
Assembly CMS content editor training
====================================

WebCrew -- Enjoying Assembly with a little help from the Web.

.. contents::

Preface
=======

The WebCrew is here to make Assembly better by using Web technology. The
Assembly homepage is an important tool for providing information to the
public (visitors and non-visitors) before, during, and after the Assembly.

We want to make your life easier by providing you with a Web authoring system
that helps you to get this information out as quickly, as easily, and as
accurate as possible.

If you find anything difficult to use or understand, wrong or otherwise in need of
change, please feel free to speak up to us: either personally or via IRC
(!webcrew) or by email (web@assembly.org).

We are happy to make software updates available to you during the event
quickly, we just need you to tell us that you need something. :)

The demo system
===============

A playground has been set up for this training (and after) that allows you to
experiment with the system before making changes to the live website.

Note: Please be aware that editing on the live system causes changes to the
public website immediately. Use the public/draft workflow if you want to keep
your changes private.

The CMS of the demo system is located at:

http://asmdemo.gocept.com/cms

The public view of the demo system is accessible via:

http://asmdemo.gocept.com/public

Frontend vs. Backend
====================

The system is split between a frontend that shows the website with all 
graphical details, typography, imagery, banners, etc. The frontend is 
accessible by the general public and will only provide information that 
has been published.

The backend requires a login and uses a light-weight graphical design that is
intended to allow you to focus on the content editing task while not worrying
too much about the frontend impression. You can access any information stored
in the system when logged in to the backend.

Basics - getting around
=======================

* How to navigate the site

  * Use the "Navigation" button to switch to/from navigation
  * Alternatively use the Escape key to switch
  * The symbol in front of the page name shows the type of the page
  * Click on a page in the tree to select it
  * Click on the + sign in front of a page to open or close the sub-tree of that page.
  * Double-click a page to edit it.

* How to search for content

  * Searches all variations of content
  * Tries to show a bit of a preview
  * The search integrates with the browser address line (OpenSearch)

* Parts of the CMS are hidden if they aren't needed very often. You can
  discover those parts by looking for small up/down arrows.

Editing a page
==============

* Navigate to a page and edit it by double-clicking
* Remember to save!
* Different content types have different editing forms
* Some parts of forms that don't change often (like tags) are hidden by
  default. You can open/close them by clicking on the up/down arrow.

* After making changes you can preview what you did by clicking the preview button.

  * The preview is helpful if you keep it open as a separate window next to the editing.
  * The preview will update when you save automatically.
  * It will also follow you when navigating through the CMS.
  * Warning: this involves some hackery and the preview might stop working every now and then. Please tell us when this happens so we can fix it in the long run.

Creating pages
==============

* Switch to navigation mode.
* Click on the root node.
* Type a name for the new page in the 'Add new page' box.

  * This name will be used for the URL and is thus visible to the user and to
    search engines. Choose it wisely.

* Click 'Add'.
* The page is created and you will be taken to the edit form.

*Every* page can have sub-pages. You can add sub-pages by clicking on the
existing page that will be the parent and then follow the same procedure as
for adding pages to the root.

Uploading images/documents
==========================

Pages can hold different kinds of data, for example a page can also simply be
a file holding an image or document.

To upload an image:

* Switch to navigation mode.
* Click on the page under which you want the image to be stored.
* Type a name for the new page in the 'Add new page' box.
* Select 'File/Image'.
* Click 'Add'.
* The file is created and you will be taken to the edit form where you can
  upload it.

Editions
========

The Assembly website requires two major features that add some complexity to
the process outlined above: multilingual content and workflow.

Until now we have seen pages of different types. To support workflow and
translation of content every page, once created, can have multiple editions of
itself.

Those editions are provided by plugins that assign tags to the editions, like
'this is a draft' or 'this is the english translation'. Those plugins can be
combined freely, but for the Assembly website, we use both translation and
workflow. The possible combinations thus are:

* English/Draft (this is the default)
* Finnish/Draft
* English/Public
* Finnish/Public

When a new page is created it starts with an initial edition that carries the
default tags of each plugin. In our case that means we create an English
draft.

Each plugin also provides some actions that allow you to create new editions
out of existing ones or destroy existing editions.

Translation
===========

The translation plugin allows having a Finnish and English edition of a page.
The English edition also works as the fallback if no Finnish edition is
available, but not the other way around: a user asking for the English edition
will never get to see the Finnish edition.

To create a Finnish translation from an existing English page:

* Navigate to the page to edit it
* Click on 'Finnish' in the language box (it currently says 'not created yet')
* The yellow bar indicating the current language switches to Finnish, the
  comment 'not created yet' disappears.
* The english content is copied over and you can start editing.

Workflow
========

The workflow plugin allows to edit a draft edition of a page before publishing
it.

A page that is only available as a draft is not visible in the public
frontend. If a page has both a draft and a public edition, then only public
edition will be visible in the frontend.

Note: You can edit both the draft and the public edition. However, when
publishing the draft your changes to the public edition will be lost.

The workflow starts with a draft edition when you create a new page. When you
are ready to publish the draft, click the 'publish draft' button. The content
of the draft will be copied to the public edition and the draft will be
deleted.

If you continue editing you will now be editing the public version.

If you want to use a draft instead of directly editing the public version, you
can extend the workflow box using the small down arrow and press the 'create
draft' button. You can then edit the draft and publish as before.

If both a draft and a public version exist, the extended actions also allow
you to revert the draft (copy content from the public version to the draft) or
delete the draft without publishing it.

News items
==========

One further speciality of the Assembly web site are news items.

News items are basically pages that are located within a news section. Did you notice
the news paper icon at the news section?

Every page that is created within this section gets two additional fields:

* Teaser text
* Teaser image

The teaser text is a required field for a news item and thus is always shown.
The teaser image is optional as it is only used for the big news items at the
front page.

Depending on the importance of the news item, you can set different tags:

featured
    to show a news item with a big image at the center stage on the frontpage

frontpage
    to show a news item in the main news listing on the frontpage

Ordering pages
==============

Pages sometimes need to be ordered specifically to appear correctly in
navigation, etc...

You can simply drag and drop pages around in the navigation tree to rearrange
them.

Warning: Please note that this change will be visible to the outside world
immediately.
