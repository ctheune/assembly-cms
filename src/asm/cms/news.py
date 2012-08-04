import asm.cms
import asm.cms.interfaces
import asm.cms.edition
import grok
import zope.interface


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

    image = asm.cms.interfaces.Blob(
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
        image_edition.content = value

    def _get_image_asset(self):
        edition = self.__parent__
        if not 'teaser-image' in edition.page:
            return None
        image = edition.page['teaser-image']
        image_edition = image.getEdition(self.__parent__.parameters,
                                         create=True)
        return image_edition

    def get_image(self):
        asset = self._get_image_asset()
        if asset is None:
            return None
        return asset.content

    image = property(fget=get_image, fset=set_image)

    @property
    def content_type(self):
        asset = self._get_image_asset()
        if asset is None:
            return None
        return asset.content_type


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
