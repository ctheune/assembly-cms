import asm.cms.interfaces
import zc.sourcefactory.contextual
import zope.schema
import zope.interface


class ISponsorsArea(zope.interface.Interface):

    areas = zope.schema.List(
        title=u"Banner areas",
        description=u"Provide a list of names for areas that will "
                     "contain sponsor banners.",
        value_type=zope.schema.TextLine())


class BannerSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):

    def getValues(self, context):
        asset = context.__parent__
        page = asset.page
        while page:
            if not asm.cms.interfaces.IPage.providedBy(page):
                return []
            if page.type == 'sponsorsarea':
                break
            page = page.__parent__
        try:
            edition = page.getEdition(asset.parameters)
        except KeyError:
            return []
        return edition.areas


class IBanner(zope.interface.Interface):

    zope.interface.taggedValue('label', u'Sponsor banner')
    zope.interface.taggedValue('description',
       u'Turn this asset into a sponsor banner and choose a banner area.')

    area = zope.schema.Choice(
        title=u'Banner area',
        description=u'Turn this asset into a sponsor banner by selecting an '
                     'area where this asset should appear.',
        source=BannerSource(),
        required=False)
