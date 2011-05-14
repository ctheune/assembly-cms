import asm.cms
import asm.cmsui.retail
import asm.cmsui.interfaces
import datetime
import grok
import megrok.pagelet
import zope.interface

asmorg = asm.cms.cms.Profile('asmorg')
languages = ['en', 'fi']
skin_name = 'asmorg'


class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin(skin_name)


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)
    megrok.pagelet.template('layout.pt')


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    def sections(self):
        root = self.application
        for section in asm.cms.edition.find_editions(
                root, request=self.request, recurse=False):
            if section.tags and 'navigation' in section.tags:
                yield section

    def sub_sections(self):
        candidate = self.context.page
        while candidate is not None:
            if asm.cms.interfaces.ICMS.providedBy(candidate.__parent__):
                break
            candidate = candidate.__parent__
        else:
            return
        editions = list(asm.cms.edition.find_editions(
            candidate, request=self.request, recurse=False))
        if not editions:
            return
        return dict(section=asm.cms.edition.select_edition(
                        candidate, self.request),
                    subs=editions)

    # A helper class to get access to the static directory in this module from
    # the layout.

    def render(self):
        return ''
