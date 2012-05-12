# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from .skin import ISkin, EmbeddedPageContent
from asm.mediagallery.gallery import MediaGallery
from asm.cmsui.retail import Pagelet
from asm.cms.edition import select_edition, NullEdition
from asm.cms.asset import Asset
import grok


class Embedded(grok.Viewlet):
    grok.layer(ISkin)
    grok.context(MediaGallery)
    grok.viewletmanager(EmbeddedPageContent)
    grok.template('embedded')


    def items(self):
        for item in self.context.list_subpages(type=['asset']):
            edition = select_edition(item, self.request)
            if isinstance(edition, NullEdition):
                continue
            yield edition
