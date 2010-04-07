# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import random
import asm.banner.interfaces
import asm.cms.interfaces
import datetime
import grok
import pytz
import zope.component
import zope.event


class SponsorsArea(asm.cms.htmlpage.HTMLPage):

    zope.interface.classProvides(asm.cms.IEditionFactory)
    zope.interface.implements(asm.banner.interfaces.ISponsorsArea)

    areas = ()

    factory_title = u'Sponsor area'

    def copyFrom(self, other):
        super(SponsorsArea, self).copyFrom(other)
        self.areas = other.areas


class Edit(asm.cms.form.EditionEditForm):

    grok.context(SponsorsArea)

    main_fields = (asm.cms.htmlpage.Edit.main_fields +
                   grok.AutoFields(asm.banner.interfaces.ISponsorsArea).
                       select('areas'))


class BannerAnnotation(grok.Annotation, grok.Model):

    grok.implements(asm.banner.interfaces.IBanner)
    grok.provides(asm.banner.interfaces.IBanner)
    grok.context(asm.cms.interfaces.IEdition)

    area = None


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

    def __getattr__(self, category):
        import pdb; pdb.set_trace() 
        sponsors = self.application['sponsors']
        banners = []
        for page in sponsors.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if not isinstance(edition, asm.cms.asset.Asset):
                continue
            b = asm.banner.interfaces.IBanner(edition)
            if b.area != category:
                continue
            banners.append(b)
        random.shuffle(banners)
        return iter(banners)
