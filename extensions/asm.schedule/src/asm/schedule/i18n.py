# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.i18nmessageid
import zope.i18n

_ = MessageFactory = zope.i18nmessageid.MessageFactory('asm.schedule')

_(u'Monday')
_(u'Tuesday')
_(u'Wednesday')
_(u'Thursday')
_(u'Friday')
_(u'Saturday')
_(u'Sunday')

# We need to distinguish those occurances of weekday names to comply with
# Finnish insanity.
_(u'Monday(until)')
_(u'Tuesday(until)')
_(u'Wednesday(until)')
_(u'Thursday(until)')
_(u'Friday(until)')
_(u'Saturday(until)')
_(u'Sunday(until)')

_(u'%H:%M')

def i18n_strftime(format, time, request):
    return time.strftime(
        zope.i18n.translate(_(format),
                            context=request).encode('utf-8')).decode('utf-8')
