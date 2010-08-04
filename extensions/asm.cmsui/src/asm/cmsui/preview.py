# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

class Preview(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def render(self):
        skin_name = zope.component.getUtility(asm.cms.interfaces.ISkinProfile)
        skin = zope.component.getUtility(
            zope.publisher.interfaces.browser.IBrowserSkinType, skin_name)
        edition = asm.cms.edition.select_edition(self.context, self.request)
        zope.publisher.browser.applySkin(self.request, skin)
        return zope.component.getMultiAdapter(
            (edition, self.request), zope.interface.Interface,
            name='index')()

