import asm.cms.cms
import asm.cms.interfaces
import grok
import grok.index
import zope.component
import zope.interface


class EditionCatalog(grok.Indexes):

    grok.site(asm.cms.cms.CMS)
    grok.context(asm.cms.interfaces.IIndexedContent)
    grok.name('edition_catalog')

    body = grok.index.Text()
    tags = grok.index.Set(attribute='tags_set')


class IndexedContent(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.IIndexedContent)
    grok.context(asm.cms.interfaces.IEdition)

    @property
    def body(self):
        result = []
        for _, searchable_text in zope.component.getAdapters(
                (self.context,), asm.cms.interfaces.ISearchableText):
            if isinstance(searchable_text, self.__class__):
                # As this adapter provides ISearchableText, too, we need
                # to ignore new occurences to avoid infinite recursion.
                continue
            result.append(searchable_text.body)
        return ' '.join(result)

    @property
    def tags(self):
        return self.context.tags


class SearchSites(grok.Annotation):
    grok.implements(asm.cms.interfaces.ISearchSites)
    grok.context(asm.cms.interfaces.ICMS)

    sites = ()
