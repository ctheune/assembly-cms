# -*- coding: utf-8 -*-
import asm.cms
import asm.cmsui.interfaces
import asm.cmsui.public.layout
import asm.cmsui.retail
import asm.mediagallery.externalasset
import asm.mediagallery.gallery
import asm.mediagallery.interfaces
import grok
import megrok.pagelet
import zope.interface

skin_name = 'assemblytv'
assemblytv = asm.cms.cms.Profile(skin_name)
languages = ['en', 'fi']


class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin(skin_name)


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)
    megrok.pagelet.template('layout.pt')


class MetadataManager(grok.ViewletManager):
    grok.name('metadata')
    grok.layer(ISkin)
    grok.context(asm.cms.interfaces.IEdition)


class LayoutHelper(asm.cmsui.public.layout.LayoutHelper):
    grok.layer(ISkin)

    @property
    def navigation(self):
        if 'navigation' in self.application:
            edition = asm.cms.edition.select_edition(
                self.application['navigation'], self.request)
            return edition
        else:
            return None


class Homepage(asm.cmsui.retail.Pagelet):

    grok.context(asm.cms.homepage.Homepage)
    grok.layer(ISkin)
    grok.name('index')

    @property
    def content(self):
        if 'homepage-content' in self.application:
            edition = asm.cms.edition.select_edition(
                self.application['homepage-content'], self.request)
            return edition
        else:
            return None


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))
