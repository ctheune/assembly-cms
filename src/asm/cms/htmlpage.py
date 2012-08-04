import asm.cms.edition
import asm.cms.interfaces
import asm.cms.utils
import bn
import grok
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


class TextIndexing(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.ISearchableText)

    def __init__(self, page):
        self.body = page.content + ' ' + page.title

        if page.tags is not None:
            tags = page.tags.split(' ')
            self.body += "\n" + " ".join("tag:" + x for x in tags)


def fix_relative_links(document, current_path):

    def fix_relative(url):
        if not url.startswith('/'):
            return
        return bn.relpath(url, current_path)

    return asm.cms.utils.rewrite_urls(document, fix_relative)
