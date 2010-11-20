# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import megrok.pagelet
import grok
import asm.cms.cms
import asm.cmsui.interfaces
import hurry.query.query


class Search(megrok.pagelet.Pagelet):

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.keyword = q = self.request.form.get('q', '')
        self.results = hurry.query.query.Query().searchResults(
            hurry.query.Text(('edition_catalog', 'body'), q))


class PublicSearch(megrok.pagelet.Pagelet):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailSkin)
    grok.name('search')

    def update(self):
        self.keyword = q = self.request.form.get('q', '')
        results = hurry.query.query.Query().searchResults(
            hurry.query.Text(('edition_catalog', 'body'), q))

        self.results = []
        for result in results:
            if result is asm.cms.edition.select_edition(result.page, self.request):
                self.results.append(result)


class OSDDEdition(grok.View):
    grok.context(asm.cms.interfaces.IEdition)
    grok.name("osdd.xml")
    grok.template("osdd")

    def title(self):
        return self.context.title


class OSDDCMS(grok.View):
    grok.context(asm.cms.interfaces.ICMS)
    grok.name("osdd.xml")
    grok.template("osdd")

    def title(self):
        edition = asm.cms.edition.select_edition(self.context, self.request)
        return edition.title + u" CMS"
