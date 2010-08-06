import asm.cms
import asm.cms.edition
import asm.mediagallery.interfaces
import asm.cms.form
import asm.workflow
import grok
import re
import sys
import urllib
import zope.interface
import ZODB.blob


class MediaGallery(asm.cms.Edition):

    zope.interface.implements(asm.mediagallery.interfaces.IMediaGallery)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery'

    title = u''


class Edit(asm.cms.form.EditionEditForm):

    grok.context(MediaGallery)

    main_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select('title')


class Index(asm.cms.Pagelet):

    grok.context(MediaGallery)

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
        return items

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
            items = items[:limit]
        return items


class AssetAnnotation(grok.Annotation, grok.Model):

    grok.implements(asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo)
    grok.provides(asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo)
    grok.context(asm.cms.interfaces.IEdition)

    author = u''
    ranking = None

    def copyFrom(self, other):
        self.author = other.author
        self.ranking = other.ranking

    def __eq__(self, other):
        return (self.author == other.author and
                self.ranking == other.ranking)


def add_gallery_data(edition):
    page = edition.page
    while page:
        if not asm.cms.interfaces.IPage.providedBy(page):
            break
        if page.type == 'mediagallery':
            return asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo
        page = page.__parent__
