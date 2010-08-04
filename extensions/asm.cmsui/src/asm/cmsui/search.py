# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

class Search(megrok.pagelet.Pagelet):

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.keyword = q = self.request.form.get('q', '')
        self.results = hurry.query.query.Query().searchResults(
            hurry.query.Text(('edition_catalog', 'body'), q))

