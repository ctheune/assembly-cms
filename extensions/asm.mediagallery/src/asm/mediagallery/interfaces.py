
import zope.interface
import zope.schema

class IMediaGalleryRoot(zope.interface.Interface):
    title = zope.schema.TextLine(title=u'Title')

    compo_data = zope.schema.Bytes(title=u'Compo data', required=False)

class IMediaGalleryFolder(zope.interface.Interface):
    title = zope.schema.TextLine(title=u'Title')

class IMediaGalleryItem(zope.interface.Interface):

    def title():
        """Automatically generated title."""

    name = zope.schema.TextLine(title=u'Name')

    author = zope.schema.TextLine(title=u'Author')

    thumbnail = zope.schema.TextLine(title=u'Thumbnail', required=False)

    content = zope.schema.Text(title=u'Page content', required=False)

    attributes = zope.schema.Text(title=u'Attributes', required=False)

    view = zope.schema.Text(title=u'View content', required=False)

