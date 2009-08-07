# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.form
import asm.cms.interfaces
import asm.cms.edition
import grok
import zope.interface


class Asset(asm.cms.edition.Edition):

    zope.interface.implements(asm.cms.interfaces.IAsset)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    content = ''

    def copyFrom(self, other):
        self.content = other.content


class Edit(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('edit')

    form_fields = grok.AutoFields(asm.cms.interfaces.IAsset)


class Index(grok.View):

    grok.layer(grok.IDefaultBrowserLayer)
    grok.name('index')

    def render(self):
        return self.context.content
