# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import grok.index
import asm.cms.cms
import asm.cms.interfaces


class EditionCatalog(grok.Indexes):

    grok.site(asm.cms.cms.CMS)
    grok.context(asm.cms.interfaces.ISearchableText)
    grok.name('edition_catalog')

    body = grok.index.Text()
