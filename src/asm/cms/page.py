# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import grok
import megrok.pagelet
import asm.cms.interfaces
import asm.cms.form
import zope.interface
import zope.html.widget


class Page(asm.cms.location.Variation):

    zope.interface.implements(asm.cms.interfaces.IPage)

    content = u''


class RetailIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.IRetailSkin)
    grok.name('index')
    grok.template('index')


class CMSIndex(grok.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('index')

    form_fields = grok.AutoFields(asm.cms.interfaces.IPage)
    form_fields['content'].custom_widget = zope.html.widget.FckeditorWidget
