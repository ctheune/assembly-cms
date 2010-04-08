# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.banner.interfaces
import asm.cms.interfaces
import datetime
import grok
import pytz
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

    def copyFrom(self, other):
        self.area = other.area


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

    def __getitem__(self, category):
        limit = None
        if '_' in category:
            category, limit = category.rsplit('_', 1)
            try:
                limit = int(limit)
            except ValueError:
                pass
        sponsors = self.application['sponsors']
        banners = []
        for page in sponsors.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if not isinstance(edition, asm.cms.asset.Asset):
                continue
            b = asm.banner.interfaces.IBanner(edition)
            if b.area != category:
                continue
            banners.append(edition)
        random.shuffle(banners)
        return banners[:limit]
