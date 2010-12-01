# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.blob
import asm.cms.asset
import asm.cmsui.base
import asm.cmsui.form
import asm.cmsui.interfaces
import grok
import locale
import magic
import os
import urllib
import zope.app.form.browser.textwidgets

grok.context(asm.cms.asset.Asset)

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

    def update(self):
        self.response.setHeader('Content-Type', self.context.content_type)

        oldlocale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, 'en_US')
        modified = self.context.modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.response.setHeader('Last-Modified', modified)
        locale.setlocale(locale.LC_TIME, oldlocale)

        filedata = open(self.context.content.committed())
        filedata.seek(0, os.SEEK_END)
        self.response.setHeader('Content-Length', filedata.tell())
        filedata.seek(0)
        self.filedata = filedata

    def render(self):
        return self.filedata


class ImagePicker(grok.View):
    grok.name('image-picker')


class DownloadAction(grok.Viewlet):
    grok.viewletmanager(asm.cmsui.base.ExtendedPageActions)


class Download(Index):
    """Adds headers that enable downloading of assets.

    This just wraps the index view and executes its update and render functions
    as the index view would execute them normally.
    """

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.name('download')

    def update(self, *args, **kw):
        self.response.setHeader("Content-Type", "application/force-download")
        self.response.setHeader("Content-Type", "application/octet-stream")
        self.response.setHeader("Content-Transfer-Encoding", "binary")
        self.response.setHeader("Content-Description", "File Transfer")
        filename = urllib.quote_plus(self.context.page.__name__)
        self.response.setHeader("Content-Disposition", "attachment; filename=%s" % filename)

        return super(Download, self).update(*args, **kw)

    def render(self, *args, **kw):
        return super(Download, self).render(*args, **kw)
