# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import grok
import megrok.pagelet
import asm.cms.interfaces
import asm.cms.form
import zope.interface
import zope.html.widget


class Page(grok.Container):

    zope.interface.implements(asm.cms.interfaces.IPage)

    content = u''


class Index(megrok.pagelet.Pagelet):
    pass


class Edit(asm.cms.form.EditForm):

    form_fields = grok.AutoFields(asm.cms.interfaces.IPage)
    form_fields['content'].custom_widget = zope.html.widget.FckeditorWidget


class AddPage(asm.cms.form.AddForm):

    form_fields = grok.AutoFields(asm.cms.interfaces.IPage)
    factory = Page

    def chooseName(self, obj):
        return obj.__name__
