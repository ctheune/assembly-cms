import asm.cms.cms
import asm.cmsui.interfaces
import grok
import zope.interface

summer12 = asm.cms.cms.Profile('summer12')
languages = ['en', 'fi']
skin_name = 'summer12'


class ISkin(asm.cmsui.interfaces.IRetailBaseSkin):
    grok.skin('summer12')


grok.layer(ISkin)


class Index(grok.View):
    grok.context(zope.interface.Interface)

    def render_layout(self):
        layout = asm.layoutpage.selection.ILayoutSelection(
            self.context).get_layout(self.request)
        return layout.render(self.request, self.context, self.render_sub)

    def render_sub(self, request, obj):
        provider = zope.component.getMultiAdapter(
                (obj, request, self),
                zope.contentprovider.interfaces.IContentProvider,
                name='embedded-page-content')
        provider.update()
        return provider.render()


class EmbeddedPageContent(grok.ViewletManager):
    """A content manager to represent a page if it is embedded on a different
    page.
    """

    grok.name('embedded-page-content')
    grok.context(zope.interface.Interface)


class NavigationBar(grok.ViewletManager):
    grok.name('navigation-bar')
    grok.context(zope.interface.Interface)


class Breadcrumbs(grok.ViewletManager):
    grok.name('breadcrumbs')
    grok.context(zope.interface.Interface)


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))


class LayoutHelper(asm.cmsui.public.layout.LayoutHelper):
    grok.layer(ISkin)
