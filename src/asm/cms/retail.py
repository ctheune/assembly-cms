# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.interfaces
import grok
import megrok.pagelet
import zope.interface


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    megrok.pagelet.template('templates/retail.pt')


class Index(grok.View):

    grok.context(asm.cms.interfaces.ILocation)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    def render(self):
        session = zope.session.interfaces.ISession(self.request)
        variation = self.context.getVariation(session['asm.cms']['variation'])
        return zope.component.getMultiAdapter((variation, self.request),
                                              name='index')()
