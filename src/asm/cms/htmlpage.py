# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.page
import grok
import megrok.pagelet
import zope.html.widget
import zope.interface


class HTMLPage(asm.cms.edition.Edition):

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
