# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cgi
import hashlib
import grok
import time
import megrok.pagelet
import asm.cms
import asm.cms.interfaces
import asm.cms.cms
import zope.interface
import hurry.query.query


class HTMLReplace(grok.Adapter):
    """Search and replace support for HTML pages."""

    grok.context(asm.cms.interfaces.IHTMLPage)
    grok.implements(asm.cms.interfaces.IReplaceSupport)

    def __init__(self, context):
        self.context = context

    def search(self, term):
        occurences = Occurences()
        for attribute in ['title', 'content']:
            offset = getattr(self.context, attribute).find(term)
            while offset != -1:
                o = Occurence(self.context, attribute, offset, term)
                occurences.add(o)
                offset = getattr(self.context, attribute).find(term, offset+1)
        return occurences


class Occurences(object):
    """A helper class to allow multiple occurences to work on the same
    object and attributes."""

    def __init__(self):
        self.entries = []

    def add(self, occurence):
        occurence.group = self
        self.entries.append(occurence)

    def rebase(self, occurence, delta):
        """Rebase the offset of all occurences after occurence by <delta>
        characters."""
        for candidate in self.entries:
            if candidate.attribute != occurence.attribute:
                continue
            if candidate.offset <= occurence.offset:
                continue
            candidate.offset += delta

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)


class Occurence(object):
    """An occurence of for search and replace of a term within an HTML
    page."""

    grok.implements(asm.cms.interfaces.IReplaceOccurence)

    def __init__(self, page, attribute, offset, term):
        self.page = page
        self.attribute = attribute
        self.offset = offset
        self.term = term

    def replace(self, target):
        content = getattr(self.page, self.attribute)
        content = (content[:self.offset] + target +
                   content[self.offset+len(self.term):])
        setattr(self.page, self.attribute, content)
        self.group.rebase(self, len(target) - len(self.term))
        zope.event.notify(grok.ObjectModifiedEvent(self.page))

    @property
    def preview(self):
        content = getattr(self.page, self.attribute)
        start = content[max(self.offset-50, 0):self.offset]
        end = content[self.offset+len(self.term):self.offset+len(self.term)+50]
        return (cgi.escape(start) +
                '<span class="match">' + cgi.escape(self.term) + '</span>' +
                cgi.escape(end))

    @property
    def id(self):
        content = getattr(self.page, self.attribute).encode('utf-8')
        content_hash = hashlib.sha1().hexdigest()[:10]
        ids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
        id = ids.getId(self.page)
        return '%s-%s-%s-%s' % (id, content_hash, self.offset, self.term)


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
                occurences = replace.search(self.search)
                self.found += len(occurences)
                if occurences:
                    self.results.append(
                        {'edition': edition,
                         'occurences': occurences})

        self.flash('Found %s occurences.' % self.found)


class Replace(megrok.pagelet.Pagelet):
    """Preform a replace operation given a users search and replace terms and
    a list of matches. Then display the remaining occurences."""

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.search = self.request.form.get('search', '')
        self.replace = self.request.form.get('replace')
        self.replaced = 0
        replace_cache = {}

        ids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
        for occurence_id in self.request.form.get('occurences'):
            id, _, _, _ = occurence_id.split('-')
            if id not in replace_cache:
                edition = ids.getObject(int(id))
                replace = asm.cms.interfaces.IReplaceSupport(edition)
                replace_cache[id] = replace.search(self.search)
            occurences = replace_cache[id]
            for candidate in occurences:
                if candidate.id == occurence_id:
                    candidate.replace(self.replace)
                    self.replaced += 1

    def render(self):
        self.flash('Replaced %s occurences.' % self.replaced)
        self.redirect(self.url(self.context, 'replacepreview',
                               {'search': self.search,
                                'replace': self.replace}))


class ReplaceActions(grok.Viewlet):

    grok.template('actions')
    grok.viewletmanager(asm.cms.Actions)
    grok.context(zope.interface.Interface)
