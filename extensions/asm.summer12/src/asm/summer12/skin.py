# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cmsui.interfaces
import grok
import zope.interface

summer12 = asm.cms.cms.Profile('summer12')
languages = ['en', 'fi']
skin_name = 'summer12'


class ISkin(asm.cmsui.interfaces.IRetailBaseSkin):
    grok.skin('summer12')


grok.layer(ISkin)

class Index(grok.View):
    grok.context(zope.interface.Interface)


class PageContent(grok.ViewletManager):
    """A general content manager to fill in the actual page content."""

    grok.name('page-content')
    grok.context(zope.interface.Interface)


class NavigationBar(grok.ViewletManager):
    grok.name('navigation-bar')
    grok.context(zope.interface.Interface)


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)

    def render(self):
        pass
