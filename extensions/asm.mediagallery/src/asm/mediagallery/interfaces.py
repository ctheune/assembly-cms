
import zope.interface
import zope.schema
import asm.cms.interfaces
import zc.sourcefactory.basic


class IMediaGallery(zope.interface.Interface):
    pass


class IMediaGalleryAdditionalInfo(zope.interface.Interface):

    zope.interface.taggedValue('label', u'Gallery')
    zope.interface.taggedValue(
        'description', u'Enter author and ranking information.')

    author = zope.schema.TextLine(title=u'Author')

    ranking = zope.schema.Int(
        title=u'Rank',
        required=False)


class HostingServices(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return [name for name, service in
                zope.component.getUtilitiesFor(IContentHostingService)]


class IHostingServiceChoice(zope.interface.Interface):

    service_id = zope.schema.Choice(
        title=u'Service',
        source=HostingServices())

    id = zope.schema.TextLine(
        title=u'ID',
        description=u'ID of this content at the service.')


class IExternalAsset(zope.interface.Interface):

    thumbnail = asm.cms.interfaces.Blob(
        title=u'Thumbnail', required=False)

    locations = zope.schema.List(
        title=u'Hosting services',
        value_type=zope.schema.Object(
            schema=IHostingServiceChoice))


class IContentHostingService(zope.interface.Interface):


    def link_code(id):
        pass


class IEmbeddableContentHostingService(IContentHostingService):

    def embed_code(id):
        pass
