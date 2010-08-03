import asm.cms
import asm.cms.edition
import asm.mediagallery.interfaces
import urllib
import grok
import zope.interface
import ZODB.blob

TYPE_GALLERY_FOLDER = 'galleryfolder'
TYPE_GALLERY_ITEM = 'galleryitem'

class GalleryFolder(asm.cms.Edition):
    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Gallery folder'

    def list(self, base=None):
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == TYPE_GALLERY_ITEM:
                yield page

class FolderEdit(asm.cms.EditForm):

    grok.context(GalleryFolder)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')


class GalleryItem(asm.cms.edition.Edition):

    zope.interface.implements(asm.mediagallery.interfaces.IGalleryItem)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Media gallery item'

    author = u''
    name = u''
    content = u''
    attributes = u''
    _thumbnail = u''
    _view = u''

    def get_attributes(self):
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
                view = """<object width="640" height="385"><param name="movie" value="http://www.youtube.com/v/LWDWn6tzsIc&amp;hl=en_US&amp;fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%s&amp;hl=en_US&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="640" height="385"></embed></object>""" % attributes['youtube']
            elif 'dtvvideo' in attributes:
                view = """<embed src="http://www.demoscene.tv/mediaplayer.swf?id=%s" width="640" height="505" allowfullscreen="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />""" % attributes['dtvvideo']
        self._view = view

    view = property(get_view, set_view)

    def get_thumbnail(self):
        return self._thumbnail

    def set_thumbnail(self, value):
        thumbnail = value
        page = self.page
        levels = 0
        while page.type != TYPE_GALLERY_FOLDER and not thumbnail:
            if 'thumbnail-image' in page:
                thumbnail = "/".join(['..'] * levels)
                if thumbnail != '':
                    thumbnail += "/"
                thumbnail += 'thumbnail-image'
                break
            else:
                levels += 1
                page = page.__parent__.page
        self._thumbnail = thumbnail

    thumbnail = property(get_thumbnail, set_thumbnail)

    def copyFrom(self, other):
        self.author = other.author
        self.name = other.name
        self._thumbnail = other._thumbnail
        self.view = other.view
        self.content = other.content
        self.attributes = other.attributes
        super(GalleryItem, self).copyFrom(other)

    def __eq__(self, other):
        if not super(GalleryItem, self).__eq__(other):
            return False
        return (self.author == other.author and
                self.name == other.name and
                self.thumbnail == other.thumbnail and
                self.view == other.view and
                self.content == other.content and
                self.attributes == other.attributes)

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

    grok.context(GalleryItem)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.mediagallery.interfaces.IGalleryItem).select(
        *'author name thumbnail view content attributes'.split(" "))
    form_fields['content'].custom_widget = asm.cms.tinymce.TinyMCEWidget

class ItemIndex(asm.cms.Pagelet):

    grok.context(GalleryItem)
    grok.name('index')

    def links(self):
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


class FolderIndex(asm.cms.Pagelet):
    grok.context(GalleryFolder)
    grok.name('index')

    def list(self):
        for media in self.context.list():
            edition = asm.cms.edition.select_edition(media, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

class IGalleryItemFields(zope.interface.Interface):

    zope.interface.taggedValue('label', u'Media gallery item')
    zope.interface.taggedValue(
        'description', u'Upload a teaser image.')

    author = zope.schema.TextLine(title=u'Author')
    name = zope.schema.TextLine(title=u'Name')

    thumbnail = zope.schema.Bytes(
        title=u'Thumbnail image', required=False)


THUMBNAIL_IMAGE = 'thumbnail-image'

class ThumbnailAnnotation(grok.Annotation,
                          grok.Model):
    grok.implements(IGalleryItemFields)
    grok.provides(IGalleryItemFields)
    grok.context(asm.cms.interfaces.IEdition)

    author = u''
    name = u''

    def copyFrom(self, other):
        self.author = other.author
        self.name = other.name
        self.thumbnail = other.thumbnail

    def __eq__(self, other):
        return (self.author == other.author,
                self.name == other.name,
                self.thumbnail == other.thumbnail,
                )

    def set_thumbnail(self, value):
        if value is None:
            return
        edition = self.__parent__
        if not THUMBNAIL_IMAGE in edition.page:
            image = asm.cms.page.Page('asset')
            edition.page[THUMBNAIL_IMAGE] = image
        image = edition.page[THUMBNAIL_IMAGE]
        image_edition = image.getEdition(edition.parameters, create=True)
        if image_edition.content is None:
            image_edition.content = ZODB.blob.Blob()
        b = image_edition.content.open('w')
        b.write(value)
        b.close()

    def get_thumbnail(self):
        edition = self.__parent__
        if not THUMBNAIL_IMAGE in edition.page:
            return None
        image = edition.page[THUMBNAIL_IMAGE]
        image_edition = image.getEdition(self.__parent__.parameters,
                                         create=True)
        if image_edition.content is not None:
            b = image_edition.content.open('r')
            result = b.read()
            b.close()
            return result

    thumbnail = property(fget=get_thumbnail, fset=set_thumbnail)


@grok.subscribe(asm.cms.htmlpage.HTMLPage)
@grok.implementer(asm.cms.interfaces.IAdditionalSchema)
def add_thumbnails(edition):
    page = edition.page
    while page:
        if not asm.cms.interfaces.IPage.providedBy(page):
            break
        if page.type == TYPE_GALLERY_FOLDER:
            return IGalleryItemFields
        page = page.__parent__

