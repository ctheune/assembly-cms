import asm.banner.interfaces
import asm.cms.interfaces
import asm.cms.edition
import asm.cmsui.form
import asm.cmsui.htmlpage
import grok
import random
import sys
import zope.component
import zope.event


class SponsorsArea(asm.cms.htmlpage.HTMLPage):

    zope.interface.classProvides(asm.cms.IEditionFactory)
    zope.interface.implements(asm.banner.interfaces.ISponsorsArea)

    areas = ()

    factory_title = u'Sponsors area'
    factory_visible = False
    factory_order = sys.maxint

    def copyFrom(self, other):
        super(SponsorsArea, self).copyFrom(other)
        self.areas = other.areas


class Edit(asm.cmsui.form.EditionEditForm):

    grok.context(SponsorsArea)

    main_fields = (asm.cmsui.htmlpage.Edit.main_fields +
                   grok.AutoFields(asm.banner.interfaces.ISponsorsArea).
                       select('areas'))


class BannerAnnotation(grok.Annotation):

    grok.implements(asm.banner.interfaces.IBanner)
    grok.provides(asm.banner.interfaces.IBanner)
    grok.context(asm.cms.interfaces.IEdition)

    area = None

    def copyFrom(self, other):
        self.area = other.area

    def __eq__(self, other):
        return self.area == other.area


def add_banner(edition):
    page = edition.page
    while page:
        if not asm.cms.interfaces.IPage.providedBy(page):
            break
        if page.type == 'sponsorsarea':
            return asm.banner.interfaces.IBanner
        page = page.__parent__


class ChooseBanner(grok.View):

    grok.context(zope.interface.Interface)

    def render(self):
        # Just a helper view.
        pass

    def choose(self, category, limit=None, randomize=True):
        # XXX use utility to look up the sponsors area
        if 'sponsors' not in self.application:
            return []

        banners = []
        for banner in asm.cms.edition.find_editions(
                self.application['sponsors'], self.request,
                asm.banner.interfaces.IBanner):
            if banner.area == category:
                banners.append(banner)
        if randomize:
            random.shuffle(banners)
        return banners[:limit]
