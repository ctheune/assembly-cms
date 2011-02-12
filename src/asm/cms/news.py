# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.edition
import grok
import zope.interface
import ZODB.blob


class NewsFolder(asm.cms.Edition):
    """A news folder aggregates other pages into a listing.
    """

    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'News section'

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

    zope.interface.taggedValue('label', u'News')
    zope.interface.taggedValue(
        'description', u'Upload a teaser image.')

    teaser = zope.schema.TextLine(
        title=u'Teaser text',
        description=u'The teaser text will be shown on the homepage and in '
                    u'the news portlet. Only plain text is supported.')

    image = zope.schema.Bytes(
        title=u'Teaser image', required=False,
        description=u'An image that can be displayed along this news item. '
                    u'Please note that depending on the context the image '
                    u'may be displayed in different styles.')


class TeaserAnnotation(grok.Annotation):
    grok.implements(INewsFields)
    grok.provides(INewsFields)
    grok.context(asm.cms.interfaces.IEdition)

    teaser = u''

    def copyFrom(self, other):
        self.teaser = other.teaser
        self.image = other.image

    def __eq__(self, other):
        return (self.teaser == other.teaser,
                self.image == other.image)

    def set_image(self, value):
        if value is None:
            return
        edition = self.__parent__
        if not 'teaser-image' in edition.page:
            image = asm.cms.page.Page('asset')
            edition.page['teaser-image'] = image
        image = edition.page['teaser-image']
        image_edition = image.getEdition(edition.parameters, create=True)
        if image_edition.content is None:
            image_edition.content = ZODB.blob.Blob()
        b = image_edition.content.open('w')
        b.write(value)
        b.close()

    def get_image(self):
        edition = self.__parent__
        if not 'teaser-image' in edition.page:
            return None
        image = edition.page['teaser-image']
        image_edition = image.getEdition(self.__parent__.parameters,
                                         create=True)
        if image_edition.content is not None:
            b = image_edition.content.open('r')
            result = b.read()
            b.close()
            return result

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
