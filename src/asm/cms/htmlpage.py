# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import grok
import megrok.pagelet
import asm.cms.interfaces
import asm.cms.form
import zope.interface
import zope.html.widget
import asm.cms.page


class HTMLPage(asm.cms.page.Edition):

    zope.interface.implements(asm.cms.interfaces.IHTMLPage)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    content = u''

    def copyFrom(self, other):
        self.content = other.content


class RetailIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.IRetailSkin)
    grok.name('index')
    grok.template('index')


class CMSIndex(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('index')

    form_fields = grok.AutoFields(asm.cms.interfaces.IHTMLPage)
    form_fields['content'].custom_widget = zope.html.widget.FckeditorWidget
