import asm.cmsui.interfaces
import grok
import zope.component
import zope.interface
import zope.intid


class IntId(grok.View):

    grok.context(zope.interface.Interface)   # XXX Meh.
    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def render(self):
        intids = zope.component.getUtility(zope.intid.IIntIds)
        return intids.getId(self.context)
