# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.tinymce
import asm.cms.utils
import bn
import cgi
import grok
import lxml.etree
import megrok.pagelet
import zope.interface


class HTMLPage(asm.cms.edition.Edition):

    zope.interface.implements(asm.cms.interfaces.IHTMLPage)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Page'
    factory_visible = True
    factory_order = 1

    content = u''

    def copyFrom(self, other):
        self.content = other.content
        super(HTMLPage, self).copyFrom(other)

    def __eq__(self, other):
        if not super(HTMLPage, self).__eq__(other):
            return False
        return self.content == other.content

    @property
    def size(self):
        return len(self.content)


class Index(megrok.pagelet.Pagelet):
    grok.layer(asm.cms.interfaces.IRetailSkin)


class Edit(asm.cms.form.EditionEditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    main_fields = grok.AutoFields(HTMLPage).select(
        'title', 'content')
    main_fields['content'].custom_widget = asm.cms.tinymce.TinyMCEWidget

    def post_process(self):
        self.content = fix_relative_links(
            self.context.content, self.url(self.context))


class TextIndexing(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.ISearchableText)

    def __init__(self, page):
        self.body = page.content + ' ' + page.title


class SearchPreview(grok.View):

    def update(self, q):
        self.keyword = q

    def render(self):
        try:
            tree = lxml.etree.fromstring(
                '<stupidcafebabe>%s</stupidcafebabe>' % self.context.content)
        except Exception:
            return ''
        text = ''.join(tree.itertext())

        # Select limited amount of characters
        focus = text.lower().find(self.keyword.lower())
        if focus == -1:
            return cgi.escape(text[:100])
        text = text[max(focus - 50, 0):focus + 50]

        # Insert highlighting. Recompute offset of focus with shorter text.
        focus = text.lower().find(self.keyword.lower())
        pre, keyword, post = (text[:focus],
                              text[focus:focus + len(self.keyword)],
                              text[focus + len(self.keyword):])
        text = '%s<span class="match">%s</span>%s' % tuple(map(cgi.escape, [pre, keyword, post]))
        return text


def fix_relative_links(document, current_path):

    def fix_relative(url):
        if not url.startswith('/'):
            return
        return bn.relpath(url, current_path)

    return asm.cms.utils.rewrite_urls(document, fix_relative)
