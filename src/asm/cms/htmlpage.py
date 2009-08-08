# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.tinymce
import grok
import megrok.pagelet
import zope.interface


class HTMLPage(asm.cms.edition.Edition):

    zope.interface.implements(asm.cms.interfaces.IHTMLPage)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    content = u''

    def copyFrom(self, other):
        self.content = other.content
        super(HTMLPage, self).copyFrom(other)


class Index(megrok.pagelet.Pagelet):
    pass


class Edit(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)

    form_fields = grok.AutoFields(HTMLPage).select(
        'title', 'tags', 'created', 'modified', 'content')
    form_fields['content'].custom_widget = asm.cms.tinymce.TinyMCEWidget
    form_fields['tags'].location = 'side'
    form_fields['created'].location = 'side'
    form_fields['modified'].location = 'side'


class TextIndexing(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.ISearchableText)

    def __init__(self, page):
        self.body = page.content + ' ' + page.title
