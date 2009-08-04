# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cms.page
import grok
import megrok.pagelet
import zope.interface


class CMS(grok.Application, asm.cms.page.Page):

    type = 'htmlpage'


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    megrok.pagelet.template('templates/layout.pt')


class Navtree(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)


class ActionView(grok.View):
    grok.baseclass()
    grok.layer(asm.cms.interfaces.ICMSSkin)

    def render(self):
        self.redirect(self.url(self.context))
