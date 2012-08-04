import asm.cms.edition
import asm.cms.interfaces
import asm.cmsui.base
import asm.cmsui.interfaces
import grok
import zope.interface
import zope.security


class LayoutHelper(grok.View):
    grok.baseclass()
    grok.context(zope.interface.Interface)

    # A helper class to get access to the static directory from the layout and
    # to accumulate some view-based helper functions needed all around.

    def current_language(self):
        cookie_lang = self.request.cookies.get('asm.translation.lang')
        if cookie_lang in asm.translation.translation.current():
            return cookie_lang
        return asm.translation.translation.fallback()

    def render(self):
        return ''


class PublicLayoutHelper(LayoutHelper):
    grok.layer(asm.cmsui.interfaces.IRetailSkin)
