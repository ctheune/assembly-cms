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

    content = ''

    def copyFrom(self, other):
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
        return (html +
                '<br/><img src="data:%s;base64,%s"/>' % (
                    asm.cms.magic.whatis(data), data.encode('base64')))


class Edit(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('edit')

    form_fields = grok.AutoFields(Asset).select(
        'title', 'tags', 'created', 'modified', 'content')
    form_fields['content'].custom_widget = FileWithDisplayWidget
    form_fields['tags'].location = 'side'
    form_fields['created'].location = 'side'
    form_fields['modified'].location = 'side'


class Index(grok.View):

    grok.layer(grok.IDefaultBrowserLayer)
    grok.name('index')

    def render(self):
        self.request.response.setHeader(
            'Content-Type', self.context.content_type)
        return self.context.content


class ImagePicker(grok.View):
    grok.context(Asset)
    grok.name('image-picker')
