# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import megrok.pagelet
import asm.cms
import asm.cms.cms
import zope.interface
import hurry.query.query


class Replace(object):

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

    def __init__(self):
        self.entries = []

    def add(self, occurence):
        occurence.group = self
        self.entries.append(occurence)

    def rebase(self, offset, delta):
        """Rebase the offset of all occurences after <offset> by <delta>
        characters."""
        for occurence in self.entries:
            if occurence.offset <= offset:
                continue
            occurence.offset += delta

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)


class Occurence(object):

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
        self.group.rebase(self.offset, len(target) - len(self.term))


class SearchAndReplace(megrok.pagelet.Pagelet):

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')


class ReplacePreview(megrok.pagelet.Pagelet):

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.search = self.request.form.get('search', '')
        # Meh. Searchpreview wants 'q'
        self.request.form['q'] = self.search
        self.results = hurry.query.query.Query().searchResults(
            hurry.query.Text(('edition_catalog', 'body'), self.search))

    def predict_matches(self, candidate):
        text = asm.cms.interfaces.ISearchableText(candidate)
        return text.body.count(self.search)


class ReplaceActions(grok.Viewlet):

    grok.template('actions')
    grok.viewletmanager(asm.cms.Actions)
    grok.context(zope.interface.Interface)
