import asm.cms
import asm.cms.edition
import asm.cms.form
import asm.cms.tinymce
import asm.mediagallery.interfaces
import asm.workflow
import grok
import random
import re
import sys
import urllib
import ZODB.blob
import zope.interface
import zope.publisher.interfaces

class MediaGallery(asm.cms.Edition):

    zope.interface.implements(asm.mediagallery.interfaces.IMediaGallery)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery'

    title = u''

    description = u''

    def copyFrom(self, other):
        self.description = other.description
        super(MediaGallery, self).copyFrom(other)

    def __eq__(self, other):
        if not super(MediaGallery, self).__eq__(other):
            return False
        return self.description == other.description


class Edit(asm.cms.form.EditionEditForm):

    grok.context(MediaGallery)

    main_fields = grok.AutoFields(MediaGallery).select(
        'title', 'description')
    main_fields['description'].custom_widget = asm.cms.tinymce.TinyMCEWidget


class Index(asm.cms.Pagelet):

    grok.context(MediaGallery)

    def update(self):
        self.skip = self.offset = int(self.request.get('offset', 0))
        self.show = 27

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
        if limit and len(items) > 0:
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

    info = None

    def update(self):
        self.info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(
            self.context)
        if self.info.thumbnail is None:
            raise zope.publisher.interfaces.NotFound(self, self.__name__, self.request)

    def render(self):
        return open(self.info.thumbnail.committed())


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
