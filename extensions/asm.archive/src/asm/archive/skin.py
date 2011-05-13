import asm.cms
import asm.cmsui.interfaces
import asm.cmsui.retail
import asm.mediagallery.externalasset
import asm.mediagallery.gallery
import asm.mediagallery.interfaces
import grok
import megrok.pagelet
import random
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

def select_years(application_subpages, request):
    years = filter(
        lambda x: YEAR_MATCH.match(x.__name__),
        list(application_subpages)
        )
    result = []
    for year_page in years:
        edition = asm.cms.edition.select_edition(year_page, request)
        if isinstance(edition, asm.cms.edition.NullEdition):
            continue
        result.append(edition)

    return result


class YearlyNavigation(grok.View):
    grok.layer(ISkin)
    grok.context(zope.interface.Interface)

    limit = DEFAULT_YEARS

    def update(self):
        self.years = select_years(self.application.subpages, self.request)
        self.year_start, self.year_end = self.get_navigation_limits(self.years, self.limit)

    def get_closest_year(self):
        closest_page = self.context
        application = asm.cms.get_application(closest_page)
        if closest_page == application:
            return None
        while closest_page.__parent__ != application:
            closest_page = closest_page.__parent__

        return asm.cms.edition.select_edition(closest_page, self.request)

    def get_navigation_limits(self, years, limit=DEFAULT_YEARS):
        current_year = self.get_closest_year()

        max_selection = min(len(years), limit)
        if current_year is not None and YEAR_MATCH.match(current_year.page.__name__):
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
        assert limit > 2, "Limit must enable navigating back and forth."

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

    @property
    def years(self):
        return select_years(self.application.subpages, self.request)

    def editioned_subpages(self, root):
        for page in root.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def select_random_items(self, year, limit=None):

        def randomize_and_limit(items, limit=None):
            result = items
            random.shuffle(result)
            if limit is not None:
                return result[:limit]
            return result

        items = []

        for category in self.editioned_subpages(year.page):
            category_items = []
            for media in category.list_subpages(type=[
                'asset', asm.mediagallery.externalasset.TYPE_EXTERNAL_ASSET]):
                edition = asm.cms.edition.select_edition(media, self.request)
                if isinstance(edition, asm.cms.edition.NullEdition):
                    continue
                category_items.append(dict(
                        edition=edition,
                        gallery=asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)))
            # Limit impact of large categories on front page listings.
            items.extend(randomize_and_limit(category_items, limit))

        return randomize_and_limit(items, limit)

    @property
    def description(self):
        if 'description' in self.application:
            edition = asm.cms.edition.select_edition(self.application['description'], self.request)
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


class GalleryIndex(asm.mediagallery.gallery.Index):

    grok.layer(ISkin)
    grok.context(asm.mediagallery.interfaces.IMediaGallery)
    grok.name('index')

    ITEMS_PER_PAGE = 30

    sort_items = False

    def render_parent(self):
        return asm.mediagallery.gallery.Index.template.render(self)

ENDINGS = {1: 'st', 2: 'nd', 3: 'rd'}

class ExternalAssetIndex(asm.mediagallery.externalasset.Index):
    grok.layer(ISkin)
    grok.context(asm.mediagallery.interfaces.IExternalAsset)
    grok.name('index')

    def update(self):
        self.info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(self.context)


class GalleryNavBar(asm.mediagallery.gallery.GalleryNavBar):
    grok.layer(ISkin)
    grok.context(asm.cms.interfaces.IEdition)

    def cut_string(self, data, max_length):
        if len(data) <= max_length:
            return data
        return data[:max_length - 3] + "..."

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
