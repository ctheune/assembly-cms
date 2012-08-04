import asm.cms.interfaces
import asm.cms
import asm.contact.interfaces
import grok
import zope.interface
import asm.cmsui.form
import asm.cmsui.interfaces


class Contact(asm.cms.Edition):

    zope.interface.implements(asm.contact.interfaces.IContactForm)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Contact form'

    email = ''

    def copyFrom(self, other):
        self.email = other.email


class Edit(asm.cmsui.form.EditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)

    form_fields = grok.AutoFields(asm.contact.interfaces.IContactForm)


class Index(asm.cmsui.form.Form):

    grok.layer(asm.cmsui.interfaces.IRetailSkin)
    form_fields = grok.AutoFields(asm.contact.interfaces.IPublicContactData)

    @grok.action(u'Send')
    def send(self, name, subject, message):
        self.flash(u'Thank you for your message.')
