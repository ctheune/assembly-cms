import asm.cms.interfaces
import zope.schema


class IBannerManager(zope.interface.Interface):

    def chooseBanners(:


class IBanner(zope.interface.Interface):

    content = zope.schema.Bytes(title=u'Banner image')
    content_type = zope.schema.ASCIILine(title=u'Banner image content type', readonly=True)

    area = zope.schema.TextLine(title=u'Page area')

    target = zope.schema.TextLine(title=u'Target URL')
    alt = zope.schema.TextLine(title=u'Alternative text')
