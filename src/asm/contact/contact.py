# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cms.location
import asm.contact.interfaces
import grok
import zope.interface
import zope.schema


class Contact(asm.cms.location.Variation):

    zope.interface.implements(asm.contact.interfaces.IContactForm)
    zope.interface.classProvides(asm.cms.interfaces.IVariationFactory)

    email = ''

    def copyFrom(self, other):
        self.email = other.email


class Edit(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('index')

    form_fields = grok.AutoFields(asm.contact.interfaces.IContactForm)


class Index(asm.cms.form.Form):

    grok.layer(asm.cms.interfaces.IRetailSkin)
    form_fields = grok.AutoFields(asm.contact.interfaces.IPublicContactData)

    @grok.action(u'Send')
    def send(self, name, subject, message):
        self.flash(u'Thank you for your message.')
