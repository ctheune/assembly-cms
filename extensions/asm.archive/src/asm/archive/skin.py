import asm.cms
import asm.cmsui.interfaces
import asm.cmsui.retail
import asm.mediagallery.externalasset
import asm.mediagallery.gallery
import asm.mediagallery.interfaces
import grok
import megrok.pagelet
import re
import urlparse
import zope.interface


skin_name = 'asmarchive'
asmarchive = asm.cms.cms.Profile(skin_name)
languages = ['en', 'fi']

class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin(skin_name)


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

DEFAULT_YEARS = 10
YEAR_MATCH = re.compile("^\d{4}$")

class YearlyNavigation(grok.View):
    grok.layer(ISkin)
    grok.context(zope.interface.Interface)

    limit = DEFAULT_YEARS

    def update(self):
        self.years = filter(
            lambda x: YEAR_MATCH.match(x.__name__),
            reversed(list(self.application.subpages))
            )

        self.year_start, self.year_end = self.get_navigation_limits(self.years, self.limit)

    def get_closest_year(self):
        traversed = self.request._traversed_names
        if len(traversed) > 1:
            # application/yeargallery/somethingelse
            # select the yeargallery
            closest_year = traversed[1]
            return self.application.get(closest_year, None)
        return None

    def get_navigation_limits(self, years, limit=DEFAULT_YEARS):
        current_year = self.get_closest_year()

        max_selection = min(len(years), limit)
        if current_year is not None and YEAR_MATCH.match(current_year.__name__):
            before = max_selection / 2
            after = max_selection - before - 1

            select_index = years.index(current_year)

            # In default we are at the beginning of the year list.
            selection_start = 0
            selection_end = max_selection
            if before < select_index + 1 and after < len(years) - select_index:
                selection_start = select_index - before
                selection_end = select_index + after + 1
            elif len(years) - select_index < max_selection:
                selection_start = len(years) - max_selection
                selection_end = len(years)

            return (selection_start, selection_end)
        else:
            return (0, max_selection)

    def list_years_near_current_page(self, limit=DEFAULT_YEARS):
        assert limit > 2, "Limit must enable navigation back and forth."

        return self.years[self.year_start:self.year_end]

    def can_navigate_forward(self):
        after = (self.limit - self.limit/2)
        return (self.limit < self.year_start + after)

    def can_navigate_backward(self):
        before = self.limit/2
        return (self.year_end - before < self.limit)


class Homepage(asm.cmsui.retail.Pagelet):

    grok.context(asm.cms.homepage.Homepage)
    grok.layer(ISkin)
    grok.name('index')


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))


class GalleryIndex(asm.mediagallery.gallery.Index):

    grok.layer(ISkin)
    grok.context(asm.mediagallery.interfaces.IMediaGallery)
    grok.name('index')


    def render_parent(self):
        return asm.mediagallery.gallery.Index.template.render(self)


class ExternalAssetIndex(asm.mediagallery.externalasset.Index):
    grok.layer(ISkin)
    grok.context(asm.mediagallery.interfaces.IExternalAsset)
    grok.name('index')

    def update(self):
        self.info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(self.context)

class GalleryNavBar(asm.mediagallery.gallery.GalleryNavBar):
    grok.layer(ISkin)
    grok.context(asm.cms.interfaces.IEdition)

    def update(self):
        pages = []
        page = self.context.page
        while not isinstance(page, asm.cms.cms.CMS):
            pages.insert(0, asm.cms.edition.select_edition(page, self.request))
            page = page.__parent__
        self.breadcrumbs = pages[0:-1]

class DownloadDomain(grok.View):
    grok.layer(ISkin)
    grok.context(unicode)
    grok.name("downloaddomain")

    def render(self):
        address = re.sub(""".+href="([^"]+?)".+""", "\\1", self.context)
        return urlparse.urlparse(address).netloc
