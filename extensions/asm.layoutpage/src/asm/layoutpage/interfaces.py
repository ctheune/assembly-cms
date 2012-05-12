import zope.interface
import zope.schema


class ILayoutPage(zope.interface.Interface):

    layout = zope.schema.Text(title=u'Layout')
