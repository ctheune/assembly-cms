# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.tinymce
import grok
import lxml
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


class Preview(grok.View):

    def update(self, q):
        self.keyword = q

    def render(self):
        tree = lxml.etree.fromstring('<stupidcafebabe>%s</stupidcafebabe>' %
                                     self.context.content)
        text = ''.join(tree.itertext())
        focus = text.find(self.keyword)
        text = text[focus-50:focus+50]
        text = text.replace(self.keyword, '<span class="match">%s</span>' % self.keyword)
        return text
