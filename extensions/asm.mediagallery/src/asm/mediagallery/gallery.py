import asm.cms
import asm.cms.edition
import asm.mediagallery.interfaces
import asm.workflow
import grok
import re
import sys
import urllib
import zope.interface
import ZODB.blob

TYPE_GALLERY_ROOT = 'mediagalleryroot'
TYPE_GALLERY_CATEGORY = 'mediagallerycategory'
TYPE_GALLERY_ITEM = 'mediagalleryitem'
THUMBNAIL_IMAGE = 'thumbnail-image'

class MediaGalleryRoot(asm.cms.Edition):
    zope.interface.implements(asm.mediagallery.interfaces.IMediaGalleryRoot)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery root'

    title = u''

    compo_data = None

    def list_categories(self, base=None):
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == TYPE_GALLERY_CATEGORY:
                yield page

    def list_items(self, base=None):
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == TYPE_GALLERY_ITEM:
                yield page


def normalize_name(string):
    result = string.strip().lower()
    result = re.sub("[^a-z0-9]", "-", result)
    result = re.sub("-+", "-", result)
    result = result.strip("-")
    return result


class RootEdit(asm.cms.EditForm):

    grok.context(MediaGalleryRoot)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.mediagallery.interfaces.IMediaGalleryRoot).select(
        'title', 'compo_data')

    def _add_category(self, category_name):
        category_id = normalize_name(category_name)

        category = self.context.page.get(category_id)
        if category is None:
            category = asm.cms.page.Page(TYPE_GALLERY_CATEGORY)
            self.context.page[category_id] = category

        # Get the first edition.
        for edition in category.editions:
            category_edition = edition
            break

        category_edition.title = category_name

        zope.event.notify(grok.ObjectModifiedEvent(category_edition))
        if asm.workflow.WORKFLOW_DRAFT in category_edition.parameters:
            asm.workflow.publish(category_edition)

        return category


    def _add_item(self, category, line):
        category_parts = line.split("|")

        item_name = None
        item_author = None
        item_thumbnail = None
        item_view = None

        item_attributes = []

        for part in category_parts:
            name, value = part.split(":", 1)
            if name == 'name':
                item_name = value
            elif name == 'author':
                item_author = value
            elif name == 'thumbnail':
                item_thumbnail = value
            elif name == 'view':
                item_view = value

            item_attributes.append(part)

        item_id = normalize_name(item_name) + u"-by-" + normalize_name(item_author)

        item = category.get(item_id)
        if item is None:
            item = asm.cms.page.Page(TYPE_GALLERY_ITEM)
            category[item_id] = item

        # Get the first edition.
        for edition in item.editions:
            item_edition = edition
            break

        item_edition.name = item_name
        item_edition.author = item_author
        item_edition.attributes = "\n".join(item_attributes)

        item_edition.thumbnail = item_thumbnail
        item_edition.view = item_view

        zope.event.notify(grok.ObjectModifiedEvent(item_edition))
        if asm.workflow.WORKFLOW_DRAFT in item_edition.parameters:
            asm.workflow.publish(item_edition)

    @grok.action(u'Add compos')
    def add_compos(self, compo_data=None, title=None):
        self.context.title = title

        if not compo_data:
            self.flash('Saved changes.')
            return

        current_category = None

        for line in compo_data.split("\n"):
            line = unicode(line.strip(), "UTF-8")

            if line == "" or line[0] == "#":
                continue
            elif line[0] == "!":
                category_name = line[1:].strip()
                current_category = self._add_category(category_name)
            else:
                item = self._add_item(current_category, line)


class RootIndex(asm.cms.Pagelet):
    grok.context(MediaGalleryRoot)
    grok.name('index')

    def list_categories(self):
        for category in self.context.list_categories():
            edition = asm.cms.edition.select_edition(category, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def list_items(self):
        for item in self.context.list_items():
            edition = asm.cms.edition.select_edition(item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def list_category_items(self, category, limit=None):
        maxLimit = limit
        if maxLimit == None:
            maxLimit = sys.maxint
        returned = 0
        for media in category.list():
            edition = asm.cms.edition.select_edition(media, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition
            returned += 1
            if returned >= maxLimit:
                break


class MediaGalleryCategory(asm.cms.Edition):
    zope.interface.implements(asm.mediagallery.interfaces.IMediaGalleryCategory)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery category'

    def list(self, base=None):
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == TYPE_GALLERY_ITEM:
                yield page


class CategoryEdit(asm.cms.EditForm):

    grok.context(MediaGalleryCategory)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')


class CategoryIndex(asm.cms.Pagelet):
    grok.context(MediaGalleryCategory)
    grok.name('index')

    def list(self):
        for media in self.context.list():
            edition = asm.cms.edition.select_edition(media, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition


class MediaGalleryItem(asm.cms.edition.Edition):

    zope.interface.implements(asm.mediagallery.interfaces.IMediaGalleryItem)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Media gallery item'

    author = u''
    name = u''
    content = u''
    attributes = u''
    _thumbnail = u''
    _view = u''

    MEDIA_WIDTH = 560.0

    def get_attributes(self):
        if self.attributes is None:
            return {}
        attributes = self.attributes.split("\n")
        result = {}
        for attribute in attributes:
            attribute = attribute.strip()
            if ":" not in attribute:
                continue
            attributeType, value = attribute.split(":", 1)
            result[attributeType] = value
        return result

    def get_title(self):
        return u"%s by %s" % (self.name, self.author)

    def set_title(self, value):
        # Generated automatically.
        pass

    title = property(get_title, set_title)

    def get_view(self):
        return self._view

    def set_view(self, value):
        view = value
        if not view:
            attributes = self.get_attributes()
            if 'youtube' in attributes:
                youtube_player_controls_height = 15.0
                youtube_height = self.MEDIA_WIDTH * 9.0 / 16.0 + youtube_player_controls_height
                view = """<object width="%(width)d" height="%(height)d"><param name="movie" value="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%(width)d" height="%(height)d"></embed></object>""" % {
                    'id': attributes['youtube'],
                    'width': self.MEDIA_WIDTH,
                    'height': youtube_height
                    }
            elif 'dtvvideo' in attributes:
                dtv_player_controls_height = 20.0
                dtv_height = self.MEDIA_WIDTH * 3.0 / 4.0 + dtv_player_controls_height
                view = """<embed src="http://www.demoscene.tv/mediaplayer.swf?id=%(id)s" width="%(width)d" height="%(height)d" allowfullscreen="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />""" % {
                    'id': attributes['dtvvideo'],
                    'width': self.MEDIA_WIDTH,
                    'height': dtv_height
                    }
        self._view = view

    view = property(get_view, set_view)

    def get_thumbnail(self):
        return self._thumbnail

    def set_thumbnail(self, value):
        thumbnail = value
        page = self.page
        levels = 0
        while not thumbnail:
            if THUMBNAIL_IMAGE in page:
                thumbnail = "/".join(['..'] * levels)
                if thumbnail != '':
                    thumbnail += "/"
                thumbnail += THUMBNAIL_IMAGE
                break
            else:
                levels += 1
                if page.type == TYPE_GALLERY_ROOT:
                    break
                page = page.__parent__.page
        self._thumbnail = thumbnail

    thumbnail = property(get_thumbnail, set_thumbnail)

    def copyFrom(self, other):
        self.author = other.author
        self.name = other.name
        self._thumbnail = other._thumbnail
        self.content = other.content
        self.attributes = other.attributes
        self._view = other._view
        super(MediaGalleryItem, self).copyFrom(other)

    def __eq__(self, other):
        if not super(MediaGalleryItem, self).__eq__(other):
            return False
        return (self.author == other.author and
                self.name == other.name and
                self._thumbnail == other._thumbnail and
                self.content == other.content and
                self.attributes == other.attributes and
                self._view == other._view)

    @property
    def size(self):
        parts = [
            self.author,
            self.name,
            self.thumbnail,
            self.view,
            self.content,
            self.attributes
            ]
        longParts = filter(parts, lambda x : x is not None)
        return sum(len(x) for x in longParts)

class ItemEdit(asm.cms.EditForm):

    grok.context(MediaGalleryItem)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.mediagallery.interfaces.IMediaGalleryItem).select(
        *'name author thumbnail content attributes view'.split(" "))
    form_fields['content'].custom_widget = asm.cms.tinymce.TinyMCEWidget

class ItemIndex(asm.cms.Pagelet):

    grok.context(MediaGalleryItem)
    grok.name('index')

    def links(self):
        if self.context.attributes is None:
            return []
        candidates = self.context.attributes.split("\n")
        results = []
        for candidate in candidates:
            candidate = candidate.strip()
            if ":" not in candidate:
                continue
            linkType, value = candidate.split(":", 1)
            if linkType == "youtube":
                results.append(("Watch on Youtube", "http://www.youtube.com/watch?v=%s" % value))
            elif linkType == "sceneorg":
                results.append(("Download original", "http://www.scene.org/file.php?file=%s" % urllib.quote_plus(value)))
            elif linkType == "pouet":
                results.append(("Pouet.net", "http://pouet.net/prod.php?which=%s" % value))
            elif linkType == "dtv":
                results.append(("Watch on DTV", "http://demoscene.tv/prod.php?id_prod=%s" % value))
        return results


@grok.subscribe(asm.mediagallery.interfaces.IMediaGalleryItem, grok.IObjectModifiedEvent)
def update_view(modified_item, event):
    modified_item.view = modified_item.view
    modified_item.thumbnail = modified_item.thumbnail
