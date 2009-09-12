# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.form
import asm.cms.interfaces
import asm.cms.edition
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


class Edit(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('edit')

    form_fields = reduce(
        lambda x,y: x.omit(y),
        ['parameters','tags','date_created','date_modified'],
        grok.AutoFields(Asset))


class Index(grok.View):

    grok.layer(grok.IDefaultBrowserLayer)
    grok.name('index')

    def render(self):
        return self.context.content


class ImagePicker(grok.View):
    grok.context(Asset)
    grok.name('image-picker')
