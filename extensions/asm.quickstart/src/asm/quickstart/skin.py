import asm.cms
import asm.cmsui.retail
import asm.cmsui.interfaces
import grok
import megrok.pagelet
import zope.interface

quickstart = asm.cms.cms.Profile('quickstart')
languages = ['en', 'fr', 'de']
skin_name = 'quickstart'


class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin('quickstart')


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)
    megrok.pagelet.template('layout.pt')


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    # A helper class to get access to the static directory in this module from
    # the layout.

    def render(self):
        return ''


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))
