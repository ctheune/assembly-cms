
import zope.interface
import zope.schema

class IGalleryItem(zope.interface.Interface):

    def title():
        """Automatically generated title."""

    author = zope.schema.TextLine(title=u'Author')

    name = zope.schema.TextLine(title=u'Name')

    thumbnail = zope.schema.TextLine(title=u'Thumbnail', required=False)

    content = zope.schema.Text(title=u'Page content', required=False)

    attributes = zope.schema.Text(title=u'Attributes', required=False)

    view = zope.schema.Text(title=u'View content', required=False)

