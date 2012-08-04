import asm.cms.edition
import asm.cms.interfaces
import base64
import grok
import magic
import ZODB.blob
import zope.interface

# This is also the amount that magic library uses for file type detection.
MAGIC_FILE_BYTES = 8192


class Asset(asm.cms.edition.Edition):
    """An asset stores binary data, like images.

    This can be used to storage images to display in the web site or binary
    files to download from the site.

    It is expected that custom logic can be used in the future that builds on
    the mime type of the content.

    """

    zope.interface.implements(asm.cms.interfaces.IAsset)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'File/Image'
    factory_order = 2
    factory_visible = True

    content = None
    _content_type = None

    def copyFrom(self, other):
        super(Asset, self).copyFrom(other)
        self.content = other.content
        self.title = other.title

    def __eq__(self, other):
        if not super(Asset, self).__eq__(other):
            return False
        return self.content == other.content

    @property
    def size(self):
        if self.content is None:
            return 0
        f = self.content.open('r')
        f.seek(0, 2)
        size = f.tell()
        f.close()
        return size

    @property
    def content_type(self):
        if self.content is None:
            return None
        if self._content_type is not None:
            return self._content_type
        significant_bytes = self.content.open('r').read(MAGIC_FILE_BYTES)
        self._content_type = magic.whatis(significant_bytes)
        return self._content_type


# This might react too many times when object is published and various
# language versions are created. At least this should keep cached
# content type current.
@grok.subscribe(Asset, grok.IObjectModifiedEvent)
def redefine_content_type(obj, event):
    obj._content_type = None
    obj._content_type = obj.content_type


@grok.subscribe(Asset, grok.IObjectCreatedEvent)
@grok.subscribe(Asset, grok.IObjectModifiedEvent)
def update_datauri(obj, event):
    datauriobj = asm.cms.interfaces.IDataUri(obj)
    if obj.content is None:
        datauriobj._datauri = None
        return

    datauri = "data:%s;base64,%s" % (
        obj.content_type,
        base64.b64encode(obj.content.open("r").read()))

    datauri_blob = ZODB.blob.Blob()
    datauri_fh = datauri_blob.open('w')
    datauri_fh.write(datauri)
    datauri_fh.close()
    datauriobj._datauri = datauri_blob


class DataUriAnnotation(grok.Annotation):
    grok.implements(asm.cms.interfaces.IDataUri)
    grok.provides(asm.cms.interfaces.IDataUri)
    grok.context(asm.cms.interfaces.IAsset)

    _datauri = None

    @property
    def datauri(self):
        if self._datauri is None:
            return None
        return self._datauri.open().read()

    def copyFrom(self, other):
        self._datauri = other._datauri

    def __eq__(self, other):
        return (self._datauri == other._datauri)
