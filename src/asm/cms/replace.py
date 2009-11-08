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
        for attribute in ['title', 'content']:
            offset = getattr(self.context, attribute).find(term)
            while offset != -1:
                yield Occurence(self.context, attribute, offset, term)
                offset = getattr(self.context, attribute).find(term, offset+1)


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
