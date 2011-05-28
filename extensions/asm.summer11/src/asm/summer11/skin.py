import asm.cms
import asm.cmsui.interfaces
import asm.cmsui.retail
import asm.translation.translation
import grok
import megrok.pagelet
import zope.interface


summer11 = asm.cms.cms.Profile('summer11')
languages = ['en', 'fi']
skin_name = 'summer11'

class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin('summer11')


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)
    megrok.pagelet.template('layout.pt')


class MainNavigation(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    def top_navigation_pages(self):
        for page in self.application.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if edition.tags and "navigation" in edition.tags:
                yield edition


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    def render(self):
        return ''

    def header_background(self):
        page = self.context.page
        if 'header-background' in page:
            return self.url(page, 'header-background')
        while page != self.application:
            page = page.__parent__
            if 'header-background' in page:
                return self.url(page, 'header-background')
        # Fallback
        return "/@@/asm.summer11/img/bg-sleepy.jpg"

    def current_language(self):
        if self.request.cookies['asm.translation.lang'] in asm.translation.translation.current():
            return self.request.cookies['asm.translation.lang']
        else:
            return asm.translation.translation.fallback()


class Homepage(asm.cmsui.retail.Pagelet):
    grok.context(asm.cms.homepage.Homepage)
    grok.layer(ISkin)
    grok.name('index')

    def news(self, tag):
        news_edition = asm.cms.edition.select_edition(
            self.context.page['news'], self.request)
        for item in news_edition.list():
            edition = asm.cms.edition.select_edition(
                item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            if not edition.has_tag(tag):
                continue
            result = dict(edition=edition,
                          news=asm.cms.news.INewsFields(edition))
            if result['news'].image:
                result['teaser_url'] = self.url(edition.page['teaser-image'])
            else:
                result['teaser_url'] = ''
            yield result

    def frontpage(self):
        return list(sorted(self.news('frontpage'),
                           key=lambda x: x['edition'].modified,
                           reverse=True))[:12]


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))


class HtmlPage(asm.cmsui.retail.Pagelet):
    grok.layer(ISkin)
    grok.context(asm.cms.htmlpage.HTMLPage)
    grok.name("index")
