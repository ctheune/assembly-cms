# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from .skin import ISkin, EmbeddedPageContent
import asm.mediagallery.interfaces
from asm.mediagallery.gallery import MediaGallery
from asm.cmsui.retail import Pagelet
from asm.cms.edition import select_edition, NullEdition
from asm.cms.asset import Asset
import grok
import zope.component

class Embedded(grok.Viewlet):
    grok.layer(ISkin)
    grok.context(MediaGallery)
    grok.viewletmanager(EmbeddedPageContent)
    grok.template('embedded')

    def domId(self):
        intids = zope.component.getUtility(zope.intid.IIntIds)
        return "embedded-%d" % intids.getId(self.context)

    def items(self):
        for item in self.context.list_subpages():
            edition = select_edition(item, self.request)
            if isinstance(edition, NullEdition):
                continue
            yield edition

class CarouselItemExternalAsset(grok.View):
    grok.context(asm.mediagallery.interfaces.IExternalAsset)
    grok.name("carouselitem")

    def update(self):
        location_url = None
        for location in self.context.locations:
            if location.service_id == "download":
                location_url = location.id
                break
        self.content_location = location_url

        edition = asm.cms.edition.select_edition(self.context, self.request)
        info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)
        self.label = "%s by %s" % (self.context.title, info.author)
        self.description = info.description


class CarouselItemAsset(grok.View):
    grok.context(Asset)
    grok.name("carouselitem")

    def update(self):
        edition = asm.cms.edition.select_edition(self.context, self.request)
        info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)
        self.label = self.context.title
        if info.author is not None:
            self.label += " by %s" % info.author
        self.description = info.description
