# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import asm.cms.interfaces
import cgi
import datetime
import grok
import grok
import megrok.pagelet
import megrok.pagelet
import z3c.flashmessage.interfaces
import zope.app.intid
import zope.interface
import zope.interface
import zope.security


class Layout(megrok.pagelet.Layout):

    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    megrok.pagelet.template('templates/cms.pt')

    def __call__(self):
        raise zope.security.interfaces.Unauthorized()


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)

    def render(self):
        return ''

    def messages(self):
        receiver = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageReceiver)
        return list(receiver.receive())


class Breadcrumbs(grok.Viewlet):
    grok.viewletmanager(PageHeader)
    grok.context(asm.cms.interfaces.IEdition)

    def update(self):
        pages = []
        page = self.context.page
        while not isinstance(page, asm.cms.cms.CMS):
            pages.insert(0, asm.cms.edition.select_edition(page, self.request))
            page = page.__parent__
        self.breadcrumbs = pages


class FlashMessageNotification(grok.Viewlet):

    grok.viewletmanager(NotificationMessages)
    grok.context(zope.interface.Interface)
