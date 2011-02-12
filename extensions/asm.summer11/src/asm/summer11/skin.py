import asm.cms
import asm.cmsui.interfaces
import asm.cmsui.retail
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


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    def render(self):
        return ''


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
