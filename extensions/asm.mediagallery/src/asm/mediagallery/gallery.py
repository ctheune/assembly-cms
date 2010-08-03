import asm.cms
import asm.cms.edition
import asm.mediagallery.interfaces
import grok
import sys
import urllib
import zope.interface
import ZODB.blob

TYPE_GALLERY_ROOT = 'mediagalleryroot'
TYPE_GALLERY_FOLDER = 'mediagalleryfolder'
TYPE_GALLERY_ITEM = 'mediagalleryitem'
THUMBNAIL_IMAGE = 'thumbnail-image'

class MediaGalleryRoot(asm.cms.Edition):
    zope.interface.implements(asm.mediagallery.interfaces.IMediaGalleryRoot)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery root'

    title = u''

    compo_data = None

    def list_folders(self, base=None):
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == TYPE_GALLERY_FOLDER:
                yield page

    def list_items(self, base=None):
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == TYPE_GALLERY_ITEM:
                yield page


class RootEdit(asm.cms.EditForm):

    grok.context(MediaGalleryRoot)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.mediagallery.interfaces.IMediaGalleryRoot).select(
        'title', 'compo_data')


    @grok.action(u'Add compos')
    def add_compos(self, compo_data=None, title=None):
        self.context.title = title

        if not compo_data:
            self.flash('Saved changes.')
            return

        # TODO mass import compo data here.
        self.flash('TODO')


class RootIndex(asm.cms.Pagelet):
    grok.context(MediaGalleryRoot)
    grok.name('index')

    def list_folders(self):
        for folder in self.context.list_folders():
            edition = asm.cms.edition.select_edition(folder, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def list_items(self):
        for item in self.context.list_folders():
            edition = asm.cms.edition.select_edition(item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def list_folder_items(self, folder, limit=None):
        maxLimit = limit
        if maxLimit == None:
            maxLimit = sys.maxint
        returned = 0
        for media in folder.list():
            edition = asm.cms.edition.select_edition(media, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition
            returned += 1
            if returned >= maxLimit:
                break


class MediaGalleryFolder(asm.cms.Edition):
    zope.interface.implements(asm.mediagallery.interfaces.IMediaGalleryFolder)
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Media gallery folder'

    def list(self, base=None):
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == TYPE_GALLERY_ITEM:
                yield page


class FolderEdit(asm.cms.EditForm):

    grok.context(MediaGalleryFolder)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')

class FolderIndex(asm.cms.Pagelet):
    grok.context(MediaGalleryFolder)
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
                view = """<object width="560" height="336"><param name="movie" value="http://www.youtube.com/v/LWDWn6tzsIc&amp;hl=en_US&amp;fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%s&amp;hl=en_US&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="560" height="336"></embed></object>""" % attributes['youtube']
            elif 'dtvvideo' in attributes:
                view = """<embed src="http://www.demoscene.tv/mediaplayer.swf?id=%s" width="560" height="442" allowfullscreen="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />""" % attributes['dtvvideo']
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

