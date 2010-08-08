# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import ZODB.blob
import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.magic
import grok
import zope.interface


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
        return asm.cms.magic.whatis(self.content.open('r').read())


class FileWithDisplayWidget(zope.app.form.browser.textwidgets.FileWidget):

    def __call__(self):
        html = super(FileWithDisplayWidget, self).__call__()
        field = self.context
        asset = field.context
        blob = field.get(asset)
        img = ''
        if blob is not None:
            data = blob.open().read()
            if data:
                img = ('<br/><img src="data:%s;base64,%s"/>' %
                       (asm.cms.magic.whatis(data), data.encode('base64')))
        return (html + img)

    def _toFieldValue(self, input):
        if input == self._missing:
            # Use existing value, don't override with missing.
            field = self.context
            asset = field.context
            value = field.get(asset)
        else:
            value = ZODB.blob.Blob()
            f = value.open('w')
            f.write(input.read())
            f.close()
        return value


class Edit(asm.cms.form.EditionEditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('edit')

    main_fields = grok.AutoFields(Asset).select(
        'title', 'content')
    main_fields['content'].custom_widget = FileWithDisplayWidget


class Index(grok.View):

    grok.layer(grok.IDefaultBrowserLayer)
    grok.name('index')

    def render(self):
        self.request.response.setHeader(
            'Content-Type', self.context.content_type)
        f = open(self.context.content.committed())
        f.seek(0, 2)
        self.request.response.setHeader(
            'Content-Length', f.tell())
        f.seek(0)
        return f


class ImagePicker(grok.View):
    grok.context(Asset)
    grok.name('image-picker')
