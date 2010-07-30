# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.cms
import asm.cms.interfaces
import cgi
import grok
import hashlib
import hurry.query.query
import megrok.pagelet
import time
import urllib
import zope.interface


class HTMLReplace(grok.Adapter):
    """Search and replace support for HTML pages."""

    grok.context(asm.cms.interfaces.IHTMLPage)
    grok.implements(asm.cms.interfaces.IReplaceSupport)

    def __init__(self, context):
        self.context = context
        ids = zope.component.getUtility(
            zope.app.intid.interfaces.IIntIds)
        self.context_id = ids.getId(self.context)

    def search(self, term):
        occurrences = Occurrences()
        for attribute in ['title', 'content']:
            offset = getattr(self.context, attribute).find(term)
            while offset != -1:
                o = Occurrence(self.context, self.context_id,
                              attribute, offset, term)
                occurrences.add(o)
                offset = getattr(self.context, attribute).find(
                    term, offset + 1)
        return occurrences


class Occurrences(object):
    """A helper class to allow multiple occurrences to work on the same
    object and attributes."""

    def __init__(self):
        self.entries = []

    def add(self, occurrence):
        occurrence.group = self
        self.entries.append(occurrence)

    def rebase(self, occurrence, delta):
        """Rebase the offset of all occurrences after occurrence by <delta>
        characters."""
        for candidate in self.entries:
            if candidate.attribute != occurrence.attribute:
                continue
            if candidate.offset <= occurrence.offset:
                continue
            candidate.offset += delta

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)


class Occurrence(object):
    """An occurrence of for search and replace of a term within an HTML
    page."""

    grok.implements(asm.cms.interfaces.IReplaceOccurrence)

    PREVIEW_AMOUNT = 50

    def __init__(self, page, page_id, attribute, offset, term):
        self.page = page
        self.page_id = page_id
        self.attribute = attribute
        self.offset = offset
        self.term = term

        # Only compute the ID initially. Due to rebase behaviour we have to
        # keep the same ID for later replaces that still refer to the old IDs.
        self.set_id()

    def replace(self, target):
        content = getattr(self.page, self.attribute)
        content = (content[:self.offset] + target +
                   content[self.offset + len(self.term):])
        setattr(self.page, self.attribute, content)
        self.group.rebase(self, len(target) - len(self.term))
        zope.event.notify(grok.ObjectModifiedEvent(self.page))

    @property
    def preview(self):
        content = getattr(self.page, self.attribute)
        start = content[max(self.offset - self.PREVIEW_AMOUNT, 0):self.offset]
        end = content[self.offset + len(self.term):
                      self.offset + len(self.term) + self.PREVIEW_AMOUNT]
        return (cgi.escape(start) +
                '<span class="match">' + cgi.escape(self.term) + '</span>' +
                cgi.escape(end))

    def set_id(self):
        content = getattr(self.page, self.attribute).encode('utf-8')
        content_hash = hashlib.sha1().hexdigest()[:10]
        self.id = '%s-%s-%s-%s' % (self.page_id, content_hash, self.offset,
                                   urllib.quote(self.term.encode('base64')))


class SearchAndReplace(megrok.pagelet.Pagelet):
    """Present the user a form to allow entering search and replace terms."""

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')


class ReplacePreview(megrok.pagelet.Pagelet):
    """Given a users search and replace terms show a list of all matches."""

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.search = self.request.form.get('search', '')

        self.found = 0
        self.results = []
        pages = [self.application]
        while pages:
            page = pages.pop()
            pages.extend(page.subpages)
            for edition in page.editions:
                try:
                    replace = asm.cms.interfaces.IReplaceSupport(edition)
                except TypeError:
                    continue
                occurrences = replace.search(self.search)
                self.found += len(occurrences)
                if occurrences:
                    self.results.append(
                        {'edition': edition,
                         'occurrences': occurrences})

        self.flash('Found %s occurrences.' % self.found)


class Replace(megrok.pagelet.Pagelet):
    """Perform a replace operation given a users search and replace terms and
    a list of matches. Then display the remaining occurrences."""

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.search = self.request.form.get('search', '')
        self.replace = self.request.form.get('replace')
        self.replaced = 0
        replace_cache = {}

        ids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
        occurrences = self.request.form.get('occurrences')
        if isinstance(occurrences, basestring):
            occurrences = [occurrences]
        for occurrence_id in occurrences:
            id, _, _, _ = occurrence_id.split('-')
            if id not in replace_cache:
                edition = ids.getObject(int(id))
                replace = asm.cms.interfaces.IReplaceSupport(edition)
                replace_cache[id] = replace.search(self.search)
            occurrences = replace_cache[id]
            for candidate in occurrences:
                if candidate.id == occurrence_id:
                    candidate.replace(self.replace)
                    self.replaced += 1

    def render(self):
        self.flash('Replaced %s occurrences.' % self.replaced)
        self.redirect(self.url(self.context, 'searchandreplace'))


class ReplaceActions(grok.Viewlet):

    grok.template('actions')
    grok.viewletmanager(asm.cms.NavigationToolActions)
    grok.context(zope.interface.Interface)
