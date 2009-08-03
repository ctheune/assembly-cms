
import zope.interface
import zope.schema


class IScheduleUpload(zope.interface.Interface):
    
    data = zope.schema.Bytes(title=u'Schedule in csv-format')

