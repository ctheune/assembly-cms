# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import grok.index
import asm.cms.cms
import asm.cms.interfaces
import megrok.pagelet
import hurry.query.query


class EditionCatalog(grok.Indexes):

    grok.site(asm.cms.cms.CMS)
    grok.context(asm.cms.interfaces.ISearchableText)
    grok.name('edition_catalog')

    body = grok.index.Text()


class Search(megrok.pagelet.Pagelet):

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)

    def update(self):
        q = self.request.form.get('q', '')
        self.results = hurry.query.query.Query().searchResults(
            hurry.query.Text(('edition_catalog', 'body'), q))
