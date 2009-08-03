# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface
import zope.schema


class IContactForm(zope.interface.Interface):

    email = zope.schema.TextLine(
        title=u'E-mail address',
        description=u'This is where user feedback will be sent to.')


class IPublicContactData(zope.interface.Interface):

    name = zope.schema.TextLine(title=u'Your name')
    subject = zope.schema.TextLine(title=u'Subject')
    message = zope.schema.Text(title=u'Your message')

