# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.edition
import grok
import zope.interface


class NewsFolder(asm.cms.Edition):
    """A news folder aggregates other pages into a listing ordered by
    modification date.
    """

    zope.interface.classProvides(asm.cms.IEditionFactory)

    def list(self, base=None):
        """Recursively list all news item pages.

        This includes all HTML pages directly contained in news folders.

        """
        if base is None:
            base = self.page
        for page in base.subpages:
            if page.type == 'htmlpage':
                yield page
            if page.type == 'news':
                for page in self.list(page):
                    yield page


class ITeaser(zope.interface.Interface):

    teaser = zope.schema.TextLine(title=u'Teaser text')


class TeaserAnnotation(grok.Annotation):
    grok.implements(ITeaser)
    grok.context(asm.cms.interfaces.IEdition)

    teaser = u''


class Edit(asm.cms.EditForm):

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title', 'tags', 'modified')
    form_fields['tags'].location = 'side'
    form_fields['modified'].location = 'side'


@grok.subscribe(asm.cms.htmlpage.HTMLPage)
@grok.implementer(asm.cms.interfaces.IAdditionalSchema)
def add_teaser(page):
    return ITeaser


class Index(asm.cms.Pagelet):

    def list(self):
        for news in self.context.list():
            edition = asm.cms.edition.select_edition(news, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition
