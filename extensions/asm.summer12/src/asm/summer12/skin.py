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


class EmbeddedPageContent(grok.ViewletManager):
    """A content manager to represent a page if it is embedded on a different
    page.
    """

    grok.name('embedded-page-content')
    grok.context(zope.interface.Interface)


class NavigationBar(grok.ViewletManager):
    grok.name('navigation-bar')
    grok.context(zope.interface.Interface)


class Breadcrumbs(grok.ViewletManager):
    grok.name('breadcrumbs')
    grok.context(zope.interface.Interface)


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)

    def current_language(self):
        if not 'asm.translation.lang' in self.request.cookies:
            return asm.translation.translation.fallback()

        if self.request.cookies['asm.translation.lang'] in asm.translation.translation.current():
            return self.request.cookies['asm.translation.lang']

        return asm.translation.translation.fallback()

    def render(self):
        pass
