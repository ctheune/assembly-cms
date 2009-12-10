# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.tinymce
import bn
import grok
import lxml.etree
import megrok.pagelet
import zope.interface


class HTMLPage(asm.cms.edition.Edition):

    zope.interface.implements(asm.cms.interfaces.IHTMLPage)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    content = u''

    def copyFrom(self, other):
        self.content = other.content
        super(HTMLPage, self).copyFrom(other)

    @property
    def size(self):
        return len(self.content)


class Index(megrok.pagelet.Pagelet):
    grok.layer(asm.cms.interfaces.IRetailSkin)


class CMSIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('index')
    grok.template('index')
    grok.require('asm.cms.EditContent')


class Edit(asm.cms.form.EditionEditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    main_fields = grok.AutoFields(HTMLPage).select(
        'title', 'tags', 'modified', 'content')
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
        focus = text.find(self.keyword)
        text = text[focus - 50:focus + 50]
        text = text.replace(
            self.keyword, '<span class="match">%s</span>' % self.keyword)
        return text


def fix_relative_links(document, current_path):
    # Hrgh. Why is there no obvious simple way to do this?
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainerwrappercafebabe>%s</stupidcontainerwrappercafebabe>' %
        document.decode('utf-8'))
    document = lxml.etree.fromstring(document, parser)
    for a in document.xpath('//a'):
        href = a.get('href')
        if href and href.startswith('/'):
            a.set('href', bn.relpath(href, current_path))
    for img in document.xpath('//img'):
        src = img.get('src')
        if src and src.startswith('/'):
            img.set('src', bn.relpath(src, current_path))

    result = lxml.etree.tostring(
        document.xpath('//stupidcontainerwrappercafebabe')[0],
        pretty_print=True)
    result = result.replace('<stupidcontainerwrappercafebabe>', '')
    result = result.replace('</stupidcontainerwrappercafebabe>', '')
    return result.strip()
