# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cmsui.retail
import asm.cms.news
from .skin import ISkin
import grok


class Index(asm.cmsui.retail.Pagelet):

    grok.context(asm.cms.news.NewsFolder)
    grok.layer(ISkin)

    def news(self):
        news = list()
        for item in self.context.list():
            edition = asm.cms.edition.select_edition(
                item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            result = dict(edition=edition,
                          news=asm.cms.news.INewsFields(edition))
            news.append(result)
        news.sort(key=lambda x:x['edition'].created, reverse=True)
        return news
