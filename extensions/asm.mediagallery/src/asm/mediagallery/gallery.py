import asm.cms
import asm.cms.edition
import asm.mediagallery.interfaces
import asm.cmsui.form
import asm.cmsui.retail
import asm.workflow
import grok
import re
import sys
import urllib
import zope.interface
import ZODB.blob
import random

class MediaGallery(asm.cms.Edition):

    zope.interface.implements(asm.mediagallery.interfaces.IMediaGallery)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery'

    title = u''


class Edit(asm.cmsui.form.EditionEditForm):

    grok.context(MediaGallery)

    main_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select('title')


class Index(asm.cmsui.retail.Pagelet):

    grok.context(MediaGallery)

    def update(self):
        self.skip = self.offset = int(self.request.get('offset', 0))
        self.show = 18

    def list_categories(self):
        for category in self.context.list_subpages(type=['mediagallery']):
            edition = asm.cms.edition.select_edition(category, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def list_items(self):
        items = []
        for item in self.context.list_subpages(type=['asset', 'externalasset']):
            edition = asm.cms.edition.select_edition(item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            items.append(dict(
                edition=edition,
                gallery=asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)))
        items.sort(key=lambda x:x['gallery'].ranking or sys.maxint)
        self.total = len(items)
        for item in items:
            if self.skip:
                self.skip -= 1
                continue
            if not self.show:
                return
            yield item
            self.show -= 1

    def list_category_items(self, category, limit=None):
        items = []
        for media in category.list_subpages(type=['asset', 'externalasset']):
            edition = asm.cms.edition.select_edition(media, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            items.append(dict(
                edition=edition,
                gallery=asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)))
        items.sort(key=lambda x:x['gallery'].ranking or sys.maxint)
        if limit:
            if items[0]['gallery'].ranking is None:
                random.shuffle(items)
            items = items[:limit]
        return items


class AssetAnnotation(grok.Annotation, grok.Model):

    grok.implements(asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo)
    grok.provides(asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo)
    grok.context(asm.cms.interfaces.IEdition)

    author = u''
    ranking = None
    thumbnail = None

    def copyFrom(self, other):
        self.author = other.author
        self.ranking = other.ranking
        self.thumbnail = other.thumbnail

    def __eq__(self, other):
        return (self.author == other.author and
                self.thumbnail == other.thumbnail and
                self.ranking == other.ranking)


def add_gallery_data(edition):
    page = edition.page
    while page:
        if not asm.cms.interfaces.IPage.providedBy(page):
            break
        if page.type == 'mediagallery':
            return asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo
        page = page.__parent__


class Thumbnail(grok.View):

    grok.context(asm.cms.interfaces.IEdition)

    def render(self):
        info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(
            self.context)
        return open(info.thumbnail.committed())


class GalleryNavBar(grok.View):
    grok.context(asm.cms.interfaces.IEdition)

    def next(self):
        all = [x.__name__ for x in self.context.page.__parent__.subpages]
        current = all.index(self.context.__parent__.__name__)
        if len(all) > current+1:
            next = self.context.__parent__.__parent__[all[current+1]]
            return asm.cms.edition.select_edition(next, self.request)

    def previous(self):
        all = [x.__name__ for x in self.context.page.__parent__.subpages]
        current = all.index(self.context.__parent__.__name__)
        if current > 0:
            prev = self.context.__parent__.__parent__[all[current-1]]
            return asm.cms.edition.select_edition(prev, self.request)
