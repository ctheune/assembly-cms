# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.form
import asm.cms.interfaces
import asm.cms.location
import grok
import megrok.pagelet
import zope.interface


class Asset(asm.cms.location.Variation):

    zope.interface.implements(asm.cms.interfaces.IAsset)
    zope.interface.classProvides(asm.cms.interfaces.IVariationFactory)

    content = ''

    def copyFrom(self, other):
        self.content = other.content


class RetailIndex(grok.View):

    grok.layer(asm.cms.interfaces.IRetailSkin)
    grok.name('index')

    def render(self):
        return self.context.content


class CMSIndex(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('index')

    form_fields = grok.AutoFields(asm.cms.interfaces.IAsset)
