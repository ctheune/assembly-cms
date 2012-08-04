
import zope.interface
import zope.schema


class IScheduleUpload(zope.interface.Interface):

    title = zope.schema.TextLine(title=u'Title')
    message = zope.schema.Text(title=u'Custom message', required=False)
    data = zope.schema.Bytes(title=u'Schedule in CSV or JSON format',
                             required=False)
