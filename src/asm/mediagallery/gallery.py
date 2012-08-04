from asm.mediagallery.interfaces import IMediaGallery
from asm.mediagallery.interfaces import IMediaGalleryAdditionalInfo
import asm.cms
import asm.cms.edition
import asm.cmsui.form
import asm.cmsui.retail
import asm.cmsui.tinymce
import asm.mediagallery.externalasset
import asm.workflow
import grok
import random
import sys
import zope.interface
import zope.publisher.interfaces


TYPE_MEDIA_GALLERY = 'mediagallery'
LIMIT_GALLERY_ITEMS = 27


class MediaGallery(asm.cms.Edition):

    zope.interface.implements(IMediaGallery)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery'

    title = u''


class Edit(asm.cmsui.form.EditionEditForm):

    grok.context(IMediaGallery)

    main_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select('title')


class Index(asm.cmsui.retail.Pagelet):

    grok.context(IMediaGallery)

    ITEMS_PER_PAGE = LIMIT_GALLERY_ITEMS

    items = []

    sort_items = True

    @property
    def max_items(self):
        return self.ITEMS_PER_PAGE

    def update(self):
        self.skip = self.offset = int(self.request.get('offset', 0))
        self.show = self.max_items
        self.info = IMediaGalleryAdditionalInfo(self.context)

        items = []
        for item in self.context.list_subpages(type=[
                'asset', asm.mediagallery.externalasset.TYPE_EXTERNAL_ASSET]):
            edition = asm.cms.edition.select_edition(item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            items.append(dict(
                edition=edition,
                gallery=IMediaGalleryAdditionalInfo(edition)))

        if self.sort_items:
            items.sort(key=lambda x: x['gallery'].ranking or sys.maxint)
        self.items = items
        self.total = len(items)

    def list_categories(self):
        for category in self.context.list_subpages(type=[TYPE_MEDIA_GALLERY]):
            edition = asm.cms.edition.select_edition(category, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def list_items(self):
        for item in self.items:
            if self.skip:
                self.skip -= 1
                continue
            if not self.show:
                return
            yield item
            self.show -= 1

    def list_category_items(self, category, limit=None):
        items = []
        for media in category.list_subpages(type=[
                'asset', asm.mediagallery.externalasset.TYPE_EXTERNAL_ASSET]):
            edition = asm.cms.edition.select_edition(media, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            items.append(dict(
                edition=edition,
                gallery=IMediaGalleryAdditionalInfo(edition)))
        items.sort(key=lambda x: x['gallery'].ranking or sys.maxint)
        if limit and len(items) > 0:
            if items[0]['gallery'].ranking is None:
                random.shuffle(items)
            items = items[:limit]
        return items


class AssetAnnotation(grok.Annotation):

    grok.implements(IMediaGalleryAdditionalInfo)
    grok.provides(IMediaGalleryAdditionalInfo)
    grok.context(asm.cms.interfaces.IEdition)

    author = u''
    ranking = None
    thumbnail = None
    description = u''

    def copyFrom(self, other):
        self.author = other.author
        self.ranking = other.ranking
        self.thumbnail = other.thumbnail
        self.description = other.description

    def __eq__(self, other):
        return (self.author == other.author and
                self.thumbnail == other.thumbnail and
                self.ranking == other.ranking and
                self.description == other.description)


class TextIndexAssetAnnotation(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.ISearchableText)
    grok.context(asm.cms.interfaces.IEdition)

    def __init__(self, edition):
        if edition.tags is not None and "hide-search" in edition.tags:
            self.body = ""
            return

        result = [
            edition.title,
            ]

        if edition.tags is not None and len(edition.tags):
            tags = edition.tags.split(' ')
            result.extend(["tag:" + x for x in tags])

        try:
            asset_annotation = IMediaGalleryAdditionalInfo(edition)
        except LookupError:
            pass
        else:
            result.extend([
                asset_annotation.author,
                asset_annotation.description,
                ])
        self.body = ' '.join(filter(None, result))


def add_gallery_data(edition):
    page = edition.page
    while page:
        if not asm.cms.interfaces.IPage.providedBy(page):
            break
        if page.type == TYPE_MEDIA_GALLERY:
            return IMediaGalleryAdditionalInfo
        page = page.__parent__


class Thumbnail(grok.View):

    grok.context(asm.cms.interfaces.IEdition)

    info = None

    def update(self):
        self.info = IMediaGalleryAdditionalInfo(
            self.context)
        if self.info.thumbnail is None:
            raise zope.publisher.interfaces.NotFound(
                self, self.__name__, self.request)

    def render(self):
        return open(self.info.thumbnail.committed())


def get_relative_to_this_gallery_item(context, from_this, request):
        all = [x.__name__ for x in context.page.__parent__.subpages]
        current = all.index(context.__parent__.__name__)
        wanted_position = current + from_this
        if 0 <= wanted_position and wanted_position < len(all):
            next = context.__parent__.__parent__[all[wanted_position]]
            return asm.cms.edition.select_edition(next, request)


class GalleryNavBar(grok.View):
    grok.context(asm.cms.interfaces.IEdition)

    def next(self):
        return get_relative_to_this_gallery_item(
            self.context, +1, self.request)

    def previous(self):
        return get_relative_to_this_gallery_item(
            self.context, -1, self.request)
