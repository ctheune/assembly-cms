# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.magic
import grok
import zope.interface


# Asset contains binary data, eg. image
class Asset(asm.cms.edition.Edition):

    zope.interface.implements(asm.cms.interfaces.IAsset)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'File/Image'
    factory_order = 2
    factory_visible = True

    content = ''

    def copyFrom(self, other):
        super(Asset, self).copyFrom(other)
        self.content = other.content
        self.title = other.title

    @property
    def size(self):
        return len(self.content)

    @property
    def content_type(self):
        return asm.cms.magic.whatis(self.content)


class FileWithDisplayWidget(zope.app.form.browser.textwidgets.FileWidget):

    def __call__(self):
        html = super(FileWithDisplayWidget, self).__call__()
        field = self.context
        asset = field.context
        data = field.get(asset)
        if data is not None:
            img = ('<br/><img src="data:%s;base64,%s"/>' %
                   (asm.cms.magic.whatis(data), data.encode('base64')))
        else:
            img = ''
        return (html + img)

    def _toFieldValue(self, input):
        value = super(FileWithDisplayWidget, self)._toFieldValue(input)
        if value is self.context.missing_value:
            # Use existing value, don't override with missing.
            field = self.context
            asset = field.context
            value = field.get(asset)
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
        self.request.response.setHeader(
            'Content-Length', len(self.context.content))
        return self.context.content


class ImagePicker(grok.View):
    grok.context(Asset)
    grok.name('image-picker')
