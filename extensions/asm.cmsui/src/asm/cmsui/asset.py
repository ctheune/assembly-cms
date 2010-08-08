# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.asset
import asm.cmsui.form
import asm.cmsui.interfaces
import zope.app.form.browser.textwidgets
import grok


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
                       (magic.whatis(data), data.encode('base64')))
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


class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.name('edit')

    main_fields = grok.AutoFields(asm.cms.asset.Asset).select(
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
    grok.name('image-picker')
