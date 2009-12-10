# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.edition
import grok
import zope.interface


class NewsFolder(asm.cms.Edition):
    """A news folder aggregates other pages into a listing.
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


class INewsFields(zope.interface.Interface):

    teaser = zope.schema.TextLine(title=u'Teaser text')
    image = zope.schema.Bytes(title=u'File', required=False)


class TeaserAnnotation(grok.Annotation,
                       grok.Model):
    grok.implements(INewsFields)
    grok.provides(INewsFields)
    grok.context(asm.cms.interfaces.IEdition)

    teaser = u''

    def copyFrom(self, other):
        self.teaser = other.teaser
        self.image = other.image

    def set_image(self, value):
        if value is None:
            return
        edition = self.__parent__
        if not 'teaser-image' in edition.page:
            image = asm.cms.page.Page()
            image.type = 'asset'
            edition.page['teaser-image'] = image
        image = edition.page['teaser-image']
        image_edition = image.getEdition(edition.parameters, create=True)
        image_edition.content = value

    def get_image(self):
        edition = self.__parent__
        if not 'teaser-image' in edition.page:
            return None
        image = edition.page['teaser-image']
        image_edition = image.getEdition(self.__parent__.parameters,
                                         create=True)
        return image_edition.content

    image = property(fget=get_image, fset=set_image)


@grok.subscribe(asm.cms.htmlpage.HTMLPage)
@grok.implementer(asm.cms.interfaces.IAdditionalSchema)
def add_teaser(edition):
    page = edition.page
    while page:
        if not asm.cms.interfaces.IPage.providedBy(page):
            break
        if page.type == 'news':
            return INewsFields
        page = page.__parent__


class Edit(asm.cms.EditForm):

    grok.context(NewsFolder)

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title', 'tags', 'modified')
    form_fields['tags'].location = 'side'
    form_fields['modified'].location = 'side'


class Index(asm.cms.Pagelet):

    grok.context(NewsFolder)

    def list(self):
        for news in self.context.list():
            edition = asm.cms.edition.select_edition(news, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition
