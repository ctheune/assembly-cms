# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt


class IntId(grok.View):

    grok.context(zope.interface.Interface)   # XXX Meh.
    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def render(self):
        intids = zope.component.getUtility(zope.app.intid.IIntIds)
        return intids.getId(self.context)
