
import zope.interface
import zope.schema


class IScheduleUpload(zope.interface.Interface):

    title = zope.schema.TextLine(title=u'Title')
    data = zope.schema.Bytes(title=u'Schedule in CSV format', required=False)
